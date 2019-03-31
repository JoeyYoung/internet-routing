import numpy as np
import tensorflow as tf


class DeepQNetwork:
    def __init__(self, sess, n_features, n_actions, id, action_labels, lr=0.0001):
        self.lr = lr
        self.id = id
        self.sess = sess
        self.n_features = n_features
        self.n_actions = n_actions
        self.action_labels = action_labels
        self.gamma = 0.95

        self.learn_step_counter = 0
        self.replace_target_iter = 100

        self.memory_size = 200
        self.batch_size = 16

        self.memory = np.zeros((self.memory_size, n_features * 2 + 2))
        self._build_net()

        t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='target_net' + str(id))
        e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='eval_net' + str(id))

        with tf.variable_scope('hard_replacement' + str(id)):
            self.target_replace_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

    def _build_net(self):
        self.s = tf.placeholder(tf.float32, [None, self.n_features], name='s')
        self.s_ = tf.placeholder(tf.float32, [None, self.n_features], name='s_')
        self.r = tf.placeholder(tf.float32, [None, ], name='r')
        self.a = tf.placeholder(tf.int32, [None, ], name='a')

        w_initializer, b_initializer = tf.random_normal_initializer(0., 0.3), tf.constant_initializer(0.1)

        # ------------------ build evaluate_net ------------------
        with tf.variable_scope('eval_net' + str(self.id)):
            e1 = tf.layers.dense(self.s, 20, tf.nn.relu, kernel_initializer=w_initializer,
                                 bias_initializer=b_initializer, name='e1')
            self.q_eval = tf.layers.dense(e1, self.n_actions, kernel_initializer=w_initializer,
                                          bias_initializer=b_initializer, name='q')

        # ------------------ build target_net ------------------
        with tf.variable_scope('target_net' + str(self.id)):
            t1 = tf.layers.dense(self.s_, 20, tf.nn.relu, kernel_initializer=w_initializer,
                                 bias_initializer=b_initializer, name='t1')
            self.q_next = tf.layers.dense(t1, self.n_actions, kernel_initializer=w_initializer,
                                          bias_initializer=b_initializer, name='t2')

        with tf.variable_scope('q_target' + str(self.id)):
            q_target = self.r + self.gamma * tf.reduce_max(self.q_next, axis=1, name='Qmax_s_')  # shape=(None, )
            self.q_target = tf.stop_gradient(q_target)

        with tf.variable_scope('q_eval' + str(self.id)):
            a_indices = tf.stack([tf.range(tf.shape(self.a)[0], dtype=tf.int32), self.a], axis=1)
            self.q_eval_wrt_a = tf.gather_nd(params=self.q_eval, indices=a_indices)  # shape=(None, )
        with tf.variable_scope('loss' + str(self.id)):
            self.loss = tf.reduce_mean(tf.squared_difference(self.q_target, self.q_eval_wrt_a, name='TD_error'))
        with tf.variable_scope('train' + str(self.id)):
            self._train_op = tf.train.RMSPropOptimizer(self.lr).minimize(self.loss)

    def store_transition(self, s, a, r, s_):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0
        transition = np.hstack((s, [a, r], s_))
        # replace the old memory with new memory
        index = self.memory_counter % self.memory_size
        self.memory[index, :] = transition

        self.memory_counter += 1

    def choose_action(self, observation, valida):
        # print("#########"+str(self.id))
        # to have batch dimension when feed into tf placeholder
        observation = observation[np.newaxis, :]

        # forward feed the observation and get q value for every actions
        actions_value = self.sess.run(self.q_eval, feed_dict={self.s: observation})
        p = actions_value.ravel()
        p = np.array(p)
        # print(p)
        for i in range(len(self.action_labels)):
            if self.action_labels[i] not in valida:
                p[i] = -999999
        # print(p)
        if -1 in valida:
            return 0
        else:
            action = np.argmax(p)
        return action

    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.sess.run(self.target_replace_op)

        # sample batch memory from all memory
        if self.memory_counter > self.memory_size:
            sample_index = np.random.choice(self.memory_size, size=self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_counter, size=self.batch_size)
        batch_memory = self.memory[sample_index, :]

        _, cost = self.sess.run(
            [self._train_op, self.loss],
            feed_dict={
                self.s: batch_memory[:, :self.n_features],
                self.a: batch_memory[:, self.n_features],
                self.r: batch_memory[:, self.n_features + 1],
                self.s_: batch_memory[:, -self.n_features:],
            })

        self.learn_step_counter += 1
