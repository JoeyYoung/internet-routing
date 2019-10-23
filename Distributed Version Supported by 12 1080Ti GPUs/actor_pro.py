import numpy as np
import tensorflow as tf
import math
import sys

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
    def __init__(self, n_features, n_actions, id, version, action_labels, lr=0.00001):
        self.lr = lr
        self.id = id
        self.sess = None
        self.bound = n_actions / 2 - 1
        # state: observable end-to-end throughput + neighbor end-to-end throughput
        self.s = tf.placeholder(tf.float32, [1, n_features], name='state')  # [1, n_F]
        self.a = tf.placeholder(tf.int32, None, name='action')  # None
        self.td_error = tf.placeholder(tf.float32, None, name='td-error')  # None
        self.action_labels = action_labels
        self.oldp = []
        self.newp = []

        with tf.variable_scope('Actor' + str(id) + '8888' + str(version)):
            l1 = tf.layers.dense(
                inputs=self.s,
                units=20,
                activation=tf.nn.leaky_relu,
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
                log_prob = tf.log(self.acts_prob[0, self.a] + 0.0000001)  # self.acts_prob[0, self.a]
                self.exp_v = tf.reduce_mean(log_prob * self.td_error)

            with tf.variable_scope('train'):
                self.train_op = tf.train.AdamOptimizer(self.lr).minimize(-self.exp_v)

    def learn(self, s, a, td):
        # add a dim(sample num), here is single sample train
        s = s[np.newaxis, :]
        feed_dict = {self.s: s, self.a: a, self.td_error: td}
        _, exp_v = self.sess.run([self.train_op, self.exp_v], feed_dict=feed_dict)
        return exp_v

    def choose_action(self, s, valida, method):
        # TODO, need to know action label, use mask, rescale possibility
        # TODO, here use distribution or max possibility?
        s = s[np.newaxis, :]
        probs = self.sess.run(self.acts_prob, feed_dict={self.s: s})
        p = probs.ravel()
        p = np.array(p)
        self.oldp = p
        # index
        for i in range(len(self.action_labels)):
            if self.action_labels[i] not in valida:
                p[i] = 0
        self.newp = p
        # return np.argmax(p)
        # TODO, BUG, one valid, sometimes it be set 0, cause bug
        if -1 in valida:
            return 0
        if p.sum() == 0:
            print("this going to here")
            return self.action_labels.index(np.random.choice(valida))
        else:
            if method == 'max':
                return np.argmax(p)
            elif method == 'prob':
                p /= p.sum()
                return np.random.choice(np.arange(probs.shape[1]), p=p)
            else:
                print("fuck method error in actor")
                sys.exit(0)

        # # array, from 0 to increase by 1, random_choice choose from probability p
        # return np.random.choice(np.arange(probs.shape[1]), p=p)

    def set_session(self, sess):
        self.sess = sess

# sess = tf.Session()
# sess.run(tf.global_variables_initializer())
# actor = Actor(sess, 10, 20)
# np.array([1.23, 2.2, 3.3, 4.43, 5.4, 6.3, 7.3, 8.3, 9.3, 10.2]), [1, 2], 0.23
