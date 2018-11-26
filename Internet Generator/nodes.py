import collections
import random

all_regions = [1, 2, 3, 4]


def choose_regions(l, num):
    results = []
    while len(results) < num:
        a = random.choice(l)
        while a in results:
            a = random.choice(l)
        results.append(a)
    return results


"""
    table: id:[ [path1], [path2] ]
"""


class T:
    """
        T nodes, clique using peer links
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.peers_T = []
        self.customers_M = []
        self.customers_CP = []
        self.customers_C = []
        # T can represented in all regions
        self.regions = choose_regions(all_regions, 4)
        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.action_labels = self.init_action_label()
        self.n_actions = len(self.action_labels)

    def init_action_label(self):
        action_labels = []
        # dim: table.keys()
        # TODO, build actions set
        return action_labels


class M:
    """
        M nodes, T or M as providers, peer links with M, CP
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.peer_degree = 0
        # 0.2 M is in two regions, other only one
        pro = random.random()
        if pro <= 0.2:
            self.regions = choose_regions(all_regions, 2)
        else:
            self.regions = choose_regions(all_regions, 1)

        self.providers_T = []
        self.providers_M = []
        self.peers_M = []
        self.peers_CP = []
        self.customers_M = []
        self.customers_CP = []
        self.customers_C = []

        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.action_labels = self.init_action_label()
        self.n_actions = len(self.action_labels)

    def init_action_label(self):
        action_labels = []
        # dim: table.keys()
        # TODO, build actions set
        return action_labels


class CP:
    """
        CP nodes, T or M as providers, peer links with CP or M
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        pro = random.random()
        if pro < 0.05:
            self.regions = choose_regions(all_regions, 2)
        else:
            self.regions = choose_regions(all_regions, 1)

        self.providers_T = []
        self.providers_M = []
        self.peers_CP = []
        self.peers_M = []

        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.action_labels = self.init_action_label()
        self.n_actions = len(self.action_labels)

    def init_action_label(self):
        action_labels = []
        # dim: table.keys()
        # TODO, build actions set
        return action_labels


class C:
    """
        C nodes, T or M as providers, no peer links
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.regions = choose_regions(all_regions, 1)

        self.providers_T = []
        self.providers_M = []

        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.action_labels = self.init_action_label()
        self.n_actions = len(self.action_labels)

    def init_action_label(self):
        action_labels = []
        # dim: table.keys()
        # TODO, build actions set
        return action_labels
