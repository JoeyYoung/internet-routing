import numpy as np
import collections

"""
    internet TM, when network has total traffic T, every node has lamda for in and out (2N)
    then every node has a exp distribution on time series
    
    at the same time epoch, get P, then finally T
"""

"""
        def expovariate(self, lambd):
        Exponential distribution.
        lambd is 1.0 divided by the desired mean.  It should be
        nonzero.  (The parameter would be called "lambda", but that is
        a reserved word in Python.)  Returned values range from 0 to
        positive infinity if lambd is positive, and from negative
        infinity to 0 if lambd is negative.
        
        # lambd: rate lambd = 1/mean
        # ('lambda' is a Python reserved word)

        # we use 1-random() instead of random() to preclude the
        # possibility of taking the log of zero.
        return -_log(1.0 - self.random())/lambd
"""


class Traffic:
    def __init__(self, T, n, lamda):
        self.T = T
        self.n = n
        self.lamda = lamda

    # TODO, get the P matrix, store T(ni, nj) in dict
    def get_traffic_matrix(self):
        # id: in/out: distributions(time vary)
        distributions = collections.defaultdict(np.array)
        for i in range(self.n):
            continue
