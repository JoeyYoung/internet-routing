import numpy as np
import collections


class NetEnv:
    def __init__(self):
        self.num_agents = 5
        self.num_links = 5
        self.agents = []
        self.STEP = 50
        self.MAX = 3000

        # store the connection information and link capacity
        # can be modified to some special cases
        self.links = np.zeros([5, 5])
        # TODO define the links

        # TODO define the traffic matrix


        # TODO set BGP paths for each agent
        paths_0, paths_1, paths_2, paths_3, paths_4 = self.init_path()

    # TODO set AS pathes: path_id[dest]:[path], no self index
    @staticmethod
    def init_path():
        paths_0 = collections.defaultdict(list)
        paths_0[1].append([0, 1])


        paths_1 = collections.defaultdict(list)


        paths_2 = collections.defaultdict(list)


        paths_3 = collections.defaultdict(list)


        paths_4 = collections.defaultdict(list)


        return paths_0, paths_1, paths_2, paths_3, paths_4

    def play_game(self):
