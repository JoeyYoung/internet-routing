import tensorflow as tf
import numpy as np


class Critic(object):
    def __init__(self, sess, n_features, gamma=0.9, lr=0.01):
        self.sess = sess
