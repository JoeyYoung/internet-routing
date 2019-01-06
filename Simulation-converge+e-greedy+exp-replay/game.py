from generator import Generator
from actor import Actor
from critic import Critic
import tensorflow as tf
import numpy as np
import collections
import random


# TODO, redefine link load
class Game:
    def __init__(self):
        # Internet topology
        self.generator = Generator(40, 12)
        self.generator.build_topology()
        self.RLs = self.generator.Ts + self.generator.Cs + self.generator.Ms + self.generator.CPs

        self.N = 52
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids
        # for each agent, add [s,a,r,s'] as element. size
        self.experience_pool = collections.defaultdict(list)
        self.pool_size = 10

    def play_game(self):
        print("play")
        sess = tf.Session()
        print('sess')
        # init states, add neigh-dim
        # order in states is important
        # id: []
        states = collections.defaultdict(list)
        for t in self.generator.Ts:
            for t_customer in t.customers_M:
                states[t.id].append(100)
            for t_customer in t.customers_CP:
                states[t.id].append(100)
            for t_customer in t.customers_C:
                states[t.id].append(100)
            for t_peer in t.peers_T:
                states[t.id].append(10000)

            # reachable end-to-end throughput (all advertised are considered here)
            for destination in t.table:
                states[t.id].append(0)
            for destination in t.table_peer:
                states[t.id].append(0)
            for destination in t.table_provider:
                states[t.id].append(0)

        for m in self.generator.Ms:
            for m_provider in m.providers_T:
                states[m.id].append(100)
            for m_provider in m.providers_M:
                states[m.id].append(100)
            for m_customer in m.customers_M:
                states[m.id].append(100)
            for m_customer in m.customers_CP:
                states[m.id].append(100)
            for m_customer in m.customers_C:
                states[m.id].append(100)
            for m_peer in m.peers_M:
                states[m.id].append(100)
            for m_peer in m.peers_CP:
                states[m.id].append(100)

            for destination in m.table:
                states[m.id].append(0)
            for destination in m.table_peer:
                states[m.id].append(0)
            for destination in m.table_provider:
                states[m.id].append(0)

        for cp in self.generator.CPs:
            for cp_provider in cp.providers_T:
                states[cp.id].append(100)
            for cp_provider in cp.providers_M:
                states[cp.id].append(100)
            for cp_peer in cp.peers_M:
                states[cp.id].append(100)
            for cp_peer in cp.peers_CP:
                states[cp.id].append(100)

            for destination in cp.table:
                states[cp.id].append(0)
            for destination in cp.table_peer:
                states[cp.id].append(0)
            for destination in cp.table_provider:
                states[cp.id].append(0)

        for c in self.generator.Cs:
            for c_provider in c.providers_T:
                states[c.id].append(100)
            for c_provider in c.providers_M:
                states[c.id].append(100)
            for destination in c.table:
                states[c.id].append(0)
            for destination in c.table_peer:
                states[c.id].append(0)
            for destination in c.table_provider:
                states[c.id].append(0)

        for i in self.RLs:
            print("create mode for: " + str(i.id))
            # node i
            n_features = len(states[i.id])
            actor = Actor(sess, n_features, i.n_actions, i.id)
            critic = Critic(sess, n_features, i.id)
            i.set_rl_setting(actor, critic)
            sess.run(tf.global_variables_initializer())

        print("model created")
        ''' 
            loop time as time epoch
        '''

        sums = []
        sums_random = []
        sumt = []

        # TODO, redefine the matrix
        TF = collections.defaultdict(dict)
        for i in range(12, 52):
            for j in range(12, 52):
                pro = random.random()
                if pro < 0.04:
                    TF[i][j] = 1

        for time in range(self.MAX):
            print("begin time epoch: " + str(time))

            # every node takes the actions
            # {id: action label}
            actions = {}
            for i in self.Ns:
                # node i
                if i in self.RLs:
                    s = np.array(states[i.id])
                    # TODO, apply e greedy
                    pro = random.random()
                    if pro > 0.1:
                        actions[i.id] = i.actor.choose_action(s)
                    else:
                        actions[i.id] = random.randint(0, i.n_actions - 1)
                else:
                    actions[i.id] = 0

            """
            RANDOM
            """
            actions_random = {}
            for i in self.Ns:
                # node i
                if i in self.RLs:
                    actions_random[i.id] = random.randint(0, i.n_actions - 1)
                else:
                    actions_random[i.id] = 0

            # actual_flow: id:id:path
            actual_flow = collections.defaultdict(dict)
            for i in range(self.N):
                for j in TF[i].keys():
                    # print("=====================")
                    # print(str(i) + 'to' + str(j))
                    # based on next-hop to get the path, hops_path
                    # action: {0:3,1:4,..., no self}
                    hop_path = []
                    cur = i
                    hop_path.append(self.ids[cur])
                    flag = -1
                    count = 0
                    while cur != j:
                        count += 1
                        if count > 10:
                            flag = 1
                            break
                        flag = 0
                        action = self.ids[cur].action_labels[actions[cur]]
                        if action.get(j) is not None:
                            cur = action[j]
                            hop_path.append(self.ids[cur])
                        else:
                            flag = 1
                            break
                    if flag == 0:
                        actual_flow[i][j] = hop_path

            num = 0
            if time == 0:
                for i in actual_flow.keys():
                    for j in actual_flow[i].keys():
                        num += 1
                print('actual flow: ' + str(num))
            """
            RANDOM
            """
            actual_flow_random = collections.defaultdict(dict)
            for i in range(self.N):
                for j in TF[i].keys():
                    hop_path = []
                    cur = i
                    hop_path.append(self.ids[cur])
                    flag = -1
                    count = 0
                    while cur != j:
                        count += 1
                        if count > 10:
                            flag = 1
                            break
                        flag = 0
                        action = self.ids[cur].action_labels[actions_random[cur]]
                        if action.get(j) is not None:
                            cur = action[j]
                            hop_path.append(self.ids[cur])
                        else:
                            flag = 1
                            break
                    if flag == 0:
                        actual_flow_random[i][j] = hop_path

            # compute link load based on actual flow, TF(weight),
            # link_load   id:id V, two directions
            link_load = np.zeros([self.N, self.N])
            for i in actual_flow.keys():
                for j in actual_flow[i].keys():
                    path = actual_flow[i][j]
                    for k in range(len(path) - 1):
                        e1 = path[k]
                        e2 = path[k + 1]
                        link_load[e1.id][e2.id] += TF[i][j]
                        link_load[e2.id][e1.id] += TF[i][j]
            """
            RANDOM
            """
            link_load_random = np.zeros([self.N, self.N])
            for i in actual_flow_random.keys():
                for j in actual_flow_random[i].keys():
                    path = actual_flow_random[i][j]
                    for k in range(len(path) - 1):
                        e1 = path[k]
                        e2 = path[k + 1]
                        link_load_random[e1.id][e2.id] += TF[i][j]
                        link_load_random[e2.id][e1.id] += TF[i][j]

            # need build link, based on actual flow?
            # compute end-to-end throughput, min in the whole path
            # id: id: T, one direction
            ee_throughput = np.zeros([self.N, self.N])
            for i in actual_flow.keys():
                # input node i
                for j in actual_flow[i].keys():
                    path = actual_flow[i][j]
                    temp_min = 9999
                    for k in range(len(path) - 1):
                        node1 = path[k]
                        node2 = path[k + 1]
                        # TODO, enlarge link capacity of TT
                        if node1 in self.generator.Ts and node2 in self.generator.Ts:
                            ee = 10000 / (1 + link_load[node1.id][node2.id])
                        else:
                            ee = 100 / (1 + link_load[node1.id][node2.id])
                        if ee < temp_min:
                            temp_min = ee
                    ee_throughput[i][j] = temp_min
            """
            RANDOM
            """
            ee_throughput_random = np.zeros([self.N, self.N])
            for i in actual_flow_random.keys():
                # input node i
                for j in actual_flow_random[i].keys():
                    path = actual_flow_random[i][j]
                    temp_min = 9999
                    for k in range(len(path) - 1):
                        node1 = path[k]
                        node2 = path[k + 1]
                        # TODO, modify here, and the state
                        if node1 in self.generator.Ts and node2 in self.generator.Ts:
                            ee = 10000 / (1 + link_load_random[node1.id][node2.id])
                        else:
                            ee = 100 / (1 + link_load_random[node1.id][node2.id])
                        if ee < temp_min:
                            temp_min = ee
                    ee_throughput_random[i][j] = temp_min

            """
                RL model
            """
            states_ = collections.defaultdict(list)
            for t in self.generator.Ts:
                for t_customer in t.customers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_customer.id]))
                for t_customer in t.customers_CP:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_customer.id]))
                for t_customer in t.customers_C:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_customer.id]))
                for t_peer in t.peers_T:
                    states_[t.id].append(10000 / (1 + link_load[t.id][t_peer.id]))

            for t in self.generator.Ms:
                for t_provider in t.providers_T:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_provider.id]))
                for t_provider in t.providers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_provider.id]))

                for t_customer in t.customers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_customer.id]))
                for t_customer in t.customers_CP:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_customer.id]))
                for t_customer in t.customers_C:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_customer.id]))
                for t_peer in t.peers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_peer.id]))
                for t_peer in t.peers_CP:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_peer.id]))

            for t in self.generator.CPs:
                for t_provider in t.providers_T:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_provider.id]))
                for t_provider in t.providers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_provider.id]))
                for t_peer in t.peers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_peer.id]))
                for t_peer in t.peers_CP:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_peer.id]))

            for t in self.generator.Cs:
                for t_provider in t.providers_T:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_provider.id]))
                for t_provider in t.providers_M:
                    states_[t.id].append(100 / (1 + link_load[t.id][t_provider.id]))

            # get the reward
            # id: mean reward
            # extend the new states
            # TODO, modify reward design
            rewards = {}
            for agent in self.RLs:
                temp_table = collections.defaultdict(list)
                for des in agent.table:
                    temp_table[des].append(0)
                for des in agent.table_peer:
                    temp_table[des].append(0)
                for des in agent.table_provider:
                    temp_table[des].append(0)

                sum_flow = 0
                sum_ee = 0
                for i in actual_flow.keys():
                    for j in actual_flow[i].keys():
                        path = actual_flow[i][j]
                        if agent in path and agent is not path[-1]:
                            sum_flow += 1
                            sum_ee += ee_throughput[i][j]
                            temp_table[j].append(ee_throughput[i][j])
                if sum_flow == 0:
                    rewards[agent.id] = 0
                else:
                    rewards[agent.id] = sum_ee / sum_flow
                for i in temp_table:
                    avg = sum(temp_table[i])/len(temp_table[i])
                    states_[agent.id].append(avg)
                d = len(states[agent.id]) - len(states_[agent.id])
                if d > 0:
                    for i in range(d):
                        states_[agent.id].append(0)

            sum_all = 0
            for i in range(self.N):
                for j in range(self.N):
                    sum_all += ee_throughput[i][j]
            """
                RANDOM
            """
            sum_all_random = 0
            for i in range(self.N):
                for j in range(self.N):
                    sum_all_random += ee_throughput_random[i][j]

            # add experience replay, what is the size
            for agent in self.RLs:
                s = np.array(states[agent.id])
                r = rewards[agent.id]
                s_ = np.array(states_[agent.id])
                a = actions[agent.id]
                exp = []
                exp.append(s)
                exp.append(r)
                exp.append(a)
                exp.append(s_)
                if len(self.experience_pool[agent.id]) < self.pool_size:
                    self.experience_pool[agent.id].append(exp)
                else:
                    self.experience_pool[agent.id] = self.experience_pool[agent.id][1:]
                    self.experience_pool[agent.id].append(exp)
                experience = random.choice(self.experience_pool[agent.id])
                s = experience[0]
                r = experience[1]
                a = experience[2]
                s_ = experience[3]
                td_error = agent.critic.learn(s, r, s_)
                agent.actor.learn(s, a, td_error)

            states = states_

            sums.append(sum_all)
            sums_random.append(sum_all_random)
            sumt.append(rewards[0])  # agent 0
            print(sum_all)
            print(sum_all_random)

            if time % 500 == 0 and time != 0:
                str1 = 'sums' + str(time) + '.txt'
                file = open(str1, 'w')
                file.write(str(sums))
                file.close()
                str2 = 'sums_random' + str(time) + '.txt'
                file = open(str2, 'w')
                file.write(str(sums_random))
                file.close()


game = Game()
game.play_game()
