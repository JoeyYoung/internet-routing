import numpy as np
import tensorflow as tf

# TODO, consider that by-passing domain can also know the ee throughput
# TODO, set correct number of units
'''
    State for each agent:
        - neighbor link throughput
        - obtained end-to-end throughput
    
    action:
        - next hop for each flow with different destinations
        
    reward:
        - end-to-end throughput
    
    train:
        - each time epoch, use one s,a,r to single train
'''


class Actor:
    def __init__(self, sess, n_features, n_actions, id, version, lr=0.001):
        self.id = id
        self.sess = sess
        # state: observable end-to-end throughput + neighbor end-to-end throughput
        self.s = tf.placeholder(tf.float32, [1, n_features], name='state')
        self.a = tf.placeholder(tf.int32, None, name='action')
        self.td_error = tf.placeholder(tf.float32, None, name='td-error')

        with tf.variable_scope('Actor' + str(id) + '8888' + str(version)):
            l1 = tf.layers.dense(
                inputs=self.s,
                units=1000,
                activation=tf.nn.relu,
                kernel_initializer=tf.random_normal_initializer(mean=0, stddev=0.1),
                bias_initializer=tf.constant_initializer(0.1),
                name='l1'
            )

            self.acts_prob = tf.layers.dense(
                inputs=l1,
                units=n_actions,
                activation=tf.nn.softmax,
                kernel_initializer=tf.random_normal_initializer(mean=0, stddev=0.1),
                bias_initializer=tf.constant_initializer(0.1),
                name='acts_prob'
            )

            with tf.variable_scope('exp_v'):
                # how to consider self.a
                log_prob = tf.log(self.acts_prob[0, self.a])
                self.exp_v = tf.reduce_mean(log_prob * self.td_error)

            with tf.variable_scope('train'):
                self.train_op = tf.train.AdamOptimizer(lr).minimize(-self.exp_v)

    def learn(self, s, a, td):
        # add a dim(sample num), here is single sample train
        s = s[np.newaxis, :]
        feed_dict = {self.s: s, self.a: a, self.td_error: td}
        _, exp_v = self.sess.run([self.train_op, self.exp_v], feed_dict=feed_dict)
        return exp_v

    def choose_action(self, s):
        s = s[np.newaxis, :]
        probs = self.sess.run(self.acts_prob, feed_dict={self.s: s})
        p = probs.ravel()
        p = np.array(p)
        p /= p.sum()
        # note the bug: for sum not 1
        return np.random.choice(np.arange(probs.shape[1]), p=p)

# sess = tf.Session()
# sess.run(tf.global_variables_initializer())
# actor = Actor(sess, 10, 20)
# np.array([1.23, 2.2, 3.3, 4.43, 5.4, 6.3, 7.3, 8.3, 9.3, 10.2]), [1, 2], 0.23
