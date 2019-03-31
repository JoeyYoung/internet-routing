import collections
import random
from functools import reduce


# TODO, consider about regions
# TODO, redefine, object or id to store


def lists_combination(lists):
    def myfunc(list1, list2):
        return [str(i) + "*" + str(j) for i in list1 for j in list2]

    return reduce(myfunc, lists)


class T:
    """
        T nodes, using peer links to connect each
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.peers_T = []
        self.customers_M = []
        self.customers_CP = []
        self.customers_C = []
        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)
        # BGP paths learned from provider
        self.table_provider = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.dqn = None

        # [{0: 3, 1: 4}, {0: 3, 1: 6}]
        self.action_labels = []
        self.n_actions = 0
        self.filter = collections.defaultdict(list)

    def init_action_label_next(self, matrix):
        # TODO, define all next hops as action space
        action_labels = []
        for i in range(len(matrix[self.id])):
            if matrix[self.id][i] == 1 and i not in action_labels:
                action_labels.append(i)

        self.action_labels = action_labels
        self.n_actions = len(action_labels)
        print('action space: ' + str(self.n_actions))

    # TODO, init filter, when choose action, use filter to give valid action set
    def init_filter(self):
        table_all = dict(
            list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        next_hops = collections.defaultdict(list)
        keys = sorted(table_all.keys())
        for i in keys:
            next_hops[i] = []
            # destination is self
            if i == self.id:
                next_hops[i].append(-1)
                continue
            pathes = table_all[i]
            for path in pathes:
                hop = path[1].id
                if hop not in next_hops[i]:
                    next_hops[i].append(hop)
        self.filter = next_hops

        # action_labels = []
        # table_all = dict(list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        # # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        # next_hops = collections.defaultdict(list)
        # res = 1
        # keys = sorted(table_all.keys())
        # # going to destination i
        # for i in keys:
        #     if i not in dest_list: continue
        #     next_hops[i] = []
        #     # destination is self
        #     if i == self.id:
        #         next_hops[i].append(-1)
        #         continue
        #     pathes = table_all[i]
        #     for path in pathes:
        #         hop = path[1].id
        #         if hop not in next_hops[i]:
        #             next_hops[i].append(hop)
        #     res *= len(next_hops[i])
        # # if self.id == 1:
        # #     print(next_hops)
        # print('action space: ' + str(res))
        # self.n_actions = res
        #
        # index = list(next_hops)
        # # for each destination, choose an next-hop to form a vector
        # dsts = []
        # for i in next_hops.keys():
        #     l = next_hops[i]
        #     dsts.append(l)
        # str_actions = lists_combination(dsts)
        # for str_action in str_actions:
        #     action = {}
        #     temp = str_action.split('*')
        #     for t in range(len(temp)):
        #         if int(temp[t]) == -1:
        #             continue
        #         # index t error
        #         action[index[t]] = int(temp[t])
        #     action_labels.append(action)

    def set_rl_setting(self, actor, critic):
        self.actor = actor
        self.critic = critic

    def set_dqn(self, dqn):
        self.dqn = dqn


class M:
    """
        M nodes, T or M as providers; peer links with M, CP ; M CP C as customers
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.peer_degree = 0

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
        # BGP paths learned from provider
        self.table_provider = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.dqn = None

        self.action_labels = []
        self.n_actions = 0
        self.filter = collections.defaultdict(list)

    def init_action_label_next(self, matrix):
        # TODO, define all next hops as action space
        action_labels = []
        for i in range(len(matrix[self.id])):
            if matrix[self.id][i] == 1 and i not in action_labels:
                action_labels.append(i)

        self.action_labels = action_labels
        self.n_actions = len(action_labels)
        print('action space: ' + str(self.n_actions))

    # TODO, init filter, when choose action, use filter to give valid action set
    def init_filter(self):
        table_all = dict(list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        next_hops = collections.defaultdict(list)
        keys = sorted(table_all.keys())
        for i in keys:
            next_hops[i] = []
            # destination is self
            if i == self.id:
                next_hops[i].append(-1)
                continue
            pathes = table_all[i]
            for path in pathes:
                hop = path[1].id
                if hop not in next_hops[i]:
                    next_hops[i].append(hop)
        self.filter = next_hops

        # action_labels = []
        # table_all = dict(list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        #
        # # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        # next_hops = collections.defaultdict(list)
        # res = 1
        # keys = sorted(table_all.keys())
        # for i in keys:
        #     if i not in dest_list: continue
        #     next_hops[i] = []
        #     # destination is self
        #     if i == self.id:
        #         next_hops[i].append(-1)
        #         continue
        #     pathes = table_all[i]
        #     for path in pathes:
        #         hop = path[1].id
        #         if hop not in next_hops[i]:
        #             next_hops[i].append(hop)
        #     res *= len(next_hops[i])
        # print('action space: ' + str(res))
        # self.n_actions = res
        #
        # index = list(next_hops)
        # # for each destination, choose an next-hop from 104-dim vector,
        # dsts = []
        # for i in next_hops.keys():
        #     l = next_hops[i]
        #     dsts.append(l)
        # str_actions = lists_combination(dsts)
        # for str_action in str_actions:
        #     action = {}
        #     temp = str_action.split('*')
        #     for t in range(len(temp)):
        #         if int(temp[t]) == -1:
        #             continue
        #         # index error
        #         action[index[t]] = int(temp[t])
        #     action_labels.append(action)
        #
        # self.action_labels = action_labels

    def set_rl_setting(self, actor, critic):
        self.actor = actor
        self.critic = critic

    def set_dqn(self, dqn):
        self.dqn = dqn


class CP:
    """
        CP nodes, T or M as providers, peer links with CP or M
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0

        self.providers_T = []
        self.providers_M = []
        self.peers_CP = []
        self.peers_M = []

        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)
        # BGP paths learned from provider
        self.table_provider = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.dqn = None

        self.action_labels = []
        self.n_actions = 0
        self.filter = collections.defaultdict(list)

    def init_action_label_next(self, matrix):
        # TODO, define all next hops as action space
        action_labels = []
        for i in range(len(matrix[self.id])):
            if matrix[self.id][i] == 1 and i not in action_labels:
                action_labels.append(i)

        self.action_labels = action_labels
        self.n_actions = len(action_labels)
        print('action space: ' + str(self.n_actions))

    # TODO, init filter, when choose action, use filter to give valid action set
    def init_filter(self):
        table_all = dict(
            list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        next_hops = collections.defaultdict(list)
        keys = sorted(table_all.keys())
        for i in keys:
            next_hops[i] = []
            # destination is self
            if i == self.id:
                next_hops[i].append(-1)
                continue
            pathes = table_all[i]
            for path in pathes:
                hop = path[1].id
                if hop not in next_hops[i]:
                    next_hops[i].append(hop)
        self.filter = next_hops

        # action_labels = []
        # table_all = dict(list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        #
        # # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        # next_hops = collections.defaultdict(list)
        # res = 1
        # keys = sorted(table_all.keys())
        # for i in keys:
        #     if i not in dest_list: continue
        #     next_hops[i] = []
        #     # destination is self
        #     if i == self.id:
        #         next_hops[i].append(-1)
        #         continue
        #     pathes = table_all[i]
        #     for path in pathes:
        #         hop = path[1].id
        #         if hop not in next_hops[i]:
        #             next_hops[i].append(hop)
        #     res *= len(next_hops[i])
        # self.n_actions = res
        # print('action space: ' + str(res))
        #
        # index = list(next_hops)
        # # for each destination, choose an next-hop from 104-dim vector,
        # dsts = []
        # for i in next_hops.keys():
        #     l = next_hops[i]
        #     dsts.append(l)
        # str_actions = lists_combination(dsts)
        # for str_action in str_actions:
        #     action = {}
        #     temp = str_action.split('*')
        #     for t in range(len(temp)):
        #         if int(temp[t]) == -1:
        #             continue
        #         # index error
        #         action[index[t]] = int(temp[t])
        #     action_labels.append(action)
        #
        # self.action_labels = action_labels

    def set_rl_setting(self, actor, critic):
        self.actor = actor
        self.critic = critic

    def set_dqn(self, dqn):
        self.dqn = dqn


class C:
    """
        C nodes, T or M as providers, no peer links
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0

        self.providers_T = []
        self.providers_M = []

        # BGP paths
        self.table = collections.defaultdict(list)
        # BGP paths learned from peers
        self.table_peer = collections.defaultdict(list)
        # BGP paths learned from provider
        self.table_provider = collections.defaultdict(list)

        # RL setting
        self.actor = None
        self.critic = None
        self.dqn = None

        self.action_labels = []
        self.n_actions = 0
        self.filter = collections.defaultdict(list)

    def init_action_label_next(self, matrix):
        # TODO, define all next hops as action space
        action_labels = []
        for i in range(len(matrix[self.id])):
            if matrix[self.id][i] == 1 and i not in action_labels:
                action_labels.append(i)

        self.action_labels = action_labels
        self.n_actions = len(action_labels)
        print('action space: ' + str(self.n_actions))

    # TODO, init filter, when choose action, use filter to give valid action set
    def init_filter(self):
        table_all = dict(
            list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        next_hops = collections.defaultdict(list)
        keys = sorted(table_all.keys())
        for i in keys:
            next_hops[i] = []
            # destination is self
            if i == self.id:
                next_hops[i].append(-1)
                continue
            pathes = table_all[i]
            for path in pathes:
                hop = path[1].id
                if hop not in next_hops[i]:
                    next_hops[i].append(hop)
        self.filter = next_hops

        # action_labels = []
        # table_all = dict(list(self.table.items()) + list(self.table_peer.items()) + list(self.table_provider.items()))
        # # next_hops: destinationID:[hop1, hop2,...], self destination is [-1]
        # next_hops = collections.defaultdict(list)
        # res = 1
        # keys = sorted(table_all.keys())
        #
        # for i in keys:
        #     if i not in dest_list: continue
        #     next_hops[i] = []
        #     # destination is self
        #     if i == self.id:
        #         next_hops[i].append(-1)
        #         continue
        #     pathes = table_all[i]
        #     for path in pathes:
        #         hop = path[1].id
        #         if hop not in next_hops[i]:
        #             next_hops[i].append(hop)
        #     res *= len(next_hops[i])
        # self.n_actions = res
        # print('action space: ' + str(res))
        #
        # index = list(next_hops)
        # # for each destination, choose an next-hop from 104-dim vector,
        # dsts = []
        # for i in next_hops.keys():
        #     l = next_hops[i]
        #     dsts.append(l)
        # str_actions = lists_combination(dsts)
        # for str_action in str_actions:
        #     action = {}
        #     temp = str_action.split('*')
        #     for t in range(len(temp)):
        #         if int(temp[t]) == -1:
        #             continue
        #         # index error
        #         action[index[t]] = int(temp[t])
        #     action_labels.append(action)
        #
        # self.action_labels = action_labels

    def set_rl_setting(self, actor, critic):
        self.actor = actor
        self.critic = critic

    def set_dqn(self, dqn):
        self.dqn = dqn
