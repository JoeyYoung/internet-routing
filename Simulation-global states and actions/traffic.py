import random
import collections


class Traffic:
    def __init__(self, pro):
        self.pro = pro

    def inject_traffic(self):
        tf = collections.defaultdict(dict)
        for i in range(5, 25):
            for j in range(5, 25):
                p = random.random()
                if p < self.pro:
                    tf[i][j] = 1
        return tf
