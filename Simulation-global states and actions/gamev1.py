from generator import Generator
from actor import Actor
from critic import Critic
from traffic import Traffic
from intlin import IntLp
import tensorflow as tf
from linprog import Linprog
import numpy as np
import collections
import random
import copy


# TODO, redefine link load
class Game:
    def __init__(self):
        # Internet topology
        self.generator = Generator(20, 5)
        self.generator.build_topology()
        self.generator.build_matrix()

        self.RLs = self.generator.Ts + self.generator.Cs + self.generator.Ms + self.generator.CPs

        self.N = 25
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids

        # for each agent, add [s,a,r,s'] as element. size
        self.experience_pool = collections.defaultdict(list)
        self.pool_size = 10
        self.global_optimal = 0
        self.int_optimal = 0

        # TODO, define TF, Matrix, Linprog
        self.traffic = Traffic(0.5)
        self.TF = self.traffic.inject_traffic()

        # intlp = IntLp(self.generator.matrix, self.TF)
        # self.int_optimal = intlp.solve_ilp()

        # linear = Linprog(self.generator.matrix, self.TF)
        # self.global_optimal = linear.solve_linprog()

    def play_game(self):
        print("play")
        sess = tf.Session()
        print('sess')

        """
            basic states for every node
        """
        states = collections.defaultdict(list)
        for i in range(self.N):
            # add neighbor
            for j in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][j] == 1:
                    if i in range(len(self.generator.Ts)) and j in range(len(self.generator.Ts)):
                        states[i].append(1000)
                    else:
                        states[i].append(100)

            # reachable end-to-end throughput (all advertised are considered here)
            node = self.ids[i]
            for d in node.table:    states[i].append(0)
            for d in node.table_peer:   states[i].append(0)
            for d in node.table_provider:   states[i].append(0)

        """
            states_v1 to combine neighbor agents' states and actions
        """
        states_v1 = collections.defaultdict(list)
        for i in range(self.N):
            states_v1[i] = []
            # neighbor's state
            for j in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][j] == 1 or i == j:
                    states_v1[i] += states[j]
            # neighbor's action
            for k in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][k] == 1 or i == k:
                    states_v1[i].append(0)

        """
            create RL module
        """
        # v0 state
        # TODO, COPY
        for i in self.RLs:
            print("create mode for: " + str(i.id) + ", version 0")
            # node i
            n_features = len(states_v1[i.id])
            actor = Actor(sess, n_features, i.n_actions, i.id, 0)
            critic = Critic(sess, n_features, i.id, 0)
            i.set_rl_setting(actor, critic)
            sess.run(tf.global_variables_initializer())

        print("model created")
        '''
            loop time as time epoch
        '''

        sums_random = []
        sums_v1 = []
        sumt = []

        TF = self.TF
        for time in range(self.MAX):
            print("begin time epoch: " + str(time))

            """
                choose an action
                    id : action label
            """

            # v1
            #TODO COPY
            actions_v1 = {}
            for i in self.Ns:
                if i in self.RLs:
                    s = np.array(states_v1[i.id])
                    pro = random.random()
                    if pro > 0.1:
                        actions_v1[i.id] = i.actor.choose_action(s)
                    else:
                        actions_v1[i.id] = random.randint(0, i.n_actions - 1)
                else:
                    actions_v1[i.id] = 0

            # random
            actions_random = {}
            for i in self.Ns:
                # node i
                if i in self.RLs:
                    actions_random[i.id] = random.randint(0, i.n_actions - 1)
                else:
                    actions_random[i.id] = 0

            """
                actual flow
                    id : id : path
            """
            # v1
            # TODO, COPY
            actual_flow_v1 = collections.defaultdict(dict)
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
                        action = self.ids[cur].action_labels[actions_v1[cur]]
                        if action.get(j) is not None:
                            cur = action[j]
                            hop_path.append(self.ids[cur])
                        else:
                            flag = 1
                            break
                    if flag == 0:
                        actual_flow_v1[i][j] = hop_path

            num = 0
            if time == 0:
                for i in actual_flow_v1.keys():
                    for j in actual_flow_v1[i].keys():
                        num += 1
                print('actual flow: ' + str(num))

            # random
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

            """
                link load 
                    id : id : V
            """
            # v1
            link_load_v1 = np.zeros([self.N, self.N])
            for i in actual_flow_v1.keys():
                for j in actual_flow_v1[i].keys():
                    path = actual_flow_v1[i][j]
                    for k in range(len(path) - 1):
                        e1 = path[k]
                        e2 = path[k + 1]
                        link_load_v1[e1.id][e2.id] += TF[i][j]
                        link_load_v1[e2.id][e1.id] += TF[i][j]

            # random
            link_load_random = np.zeros([self.N, self.N])
            for i in actual_flow_random.keys():
                for j in actual_flow_random[i].keys():
                    path = actual_flow_random[i][j]
                    for k in range(len(path) - 1):
                        e1 = path[k]
                        e2 = path[k + 1]
                        link_load_random[e1.id][e2.id] += TF[i][j]
                        link_load_random[e2.id][e1.id] += TF[i][j]

            """
                ee throughput
                    id : id : T
            """
            # v1
            ee_throughput_v1 = np.zeros([self.N, self.N])
            for i in actual_flow_v1.keys():
                # input node i
                for j in actual_flow_v1[i].keys():
                    path = actual_flow_v1[i][j]
                    temp_min = 9999
                    for k in range(len(path) - 1):
                        node1 = path[k]
                        node2 = path[k + 1]
                        # TODO, enlarge link capacity of TT
                        if node1.id in range(len(self.generator.Ts)) and node2 in range(len(self.generator.Ts)):
                            ee = 1000 / (1 + link_load_v1[node1.id][node2.id])
                        else:
                            ee = 100 / (1 + link_load_v1[node1.id][node2.id])
                        if ee < temp_min:
                            temp_min = ee
                    ee_throughput_v1[i][j] = temp_min

            # random
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
                            ee = 1000 / (1 + link_load_random[node1.id][node2.id])
                        else:
                            ee = 100 / (1 + link_load_random[node1.id][node2.id])
                        if ee < temp_min:
                            temp_min = ee
                    ee_throughput_random[i][j] = temp_min

            """
                next basic states for every node, neighbor part
            """
            # TODO, COPY
            v1_states_ = collections.defaultdict(list)
            for i in range(self.N):
                for j in range(len(self.generator.matrix[i])):
                    if self.generator.matrix[i][j] == 1:
                        if i in range(len(self.generator.Ts)) and j in range(len(self.generator.Ts)):
                            if link_load_v1[i][j] in range(2):
                                v1_states_[i].append(1000)
                            else:
                                v1_states_[i].append(1000 / (1 + link_load_v1[i][j]))
                        else:
                            if link_load_v1[i][j] in range(2):
                                v1_states_[i].append(100)
                            else:
                                v1_states_[i].append(100 / (1 + link_load_v1[i][j]))

            """
                reward, 
                basic states, ee part
            """
            # v1
            #TODO, copy
            rewards_v1 = {}
            for agent in self.RLs:
                temp_table_v1 = collections.defaultdict(list)
                for des in agent.table:
                    temp_table_v1[des].append(0)
                for des in agent.table_peer:
                    temp_table_v1[des].append(0)
                for des in agent.table_provider:
                    temp_table_v1[des].append(0)

                sum_flow = 0
                sum_ee = 0
                for i in actual_flow_v1.keys():
                    for j in actual_flow_v1[i].keys():
                        path = actual_flow_v1[i][j]
                        if agent in path and agent is not path[-1]:
                            sum_flow += 1
                            sum_ee += ee_throughput_v1[i][j]
                            temp_table_v1[j].append(ee_throughput_v1[i][j])
                if sum_flow == 0:
                    rewards_v1[agent.id] = 0
                else:
                    rewards_v1[agent.id] = sum_ee / sum_flow

                for i in temp_table_v1:
                    avg = sum(temp_table_v1[i]) / len(temp_table_v1[i])
                    v1_states_[agent.id].append(avg)

            """
                system throughput
            """


            # v1
            sum_all_v1 = 0
            for i in range(self.N):
                for j in range(self.N):
                    sum_all_v1 += ee_throughput_v1[i][j]

            # random
            sum_all_random = 0
            for i in range(self.N):
                for j in range(self.N):
                    sum_all_random += ee_throughput_random[i][j]

            """
                next states v0
            """
            states_v1_ = collections.defaultdict(list)
            for i in range(self.N):
                states_v1_[i] = []
                for j in range(self.N):
                    if self.generator.matrix[i][j] == 1 or i == j:
                        states_v1_[i] += v1_states_[j]
                for k in range(self.N):
                    if self.generator.matrix[i][k] == 1 or i == k:
                        states_v1_[i].append(actions_v1[k])

            """
                agent learns through s, a, r, s_
            """

            # v0
            # TODO COPY
            for agent in self.RLs:
                s = np.array(states_v1[agent.id])
                r = rewards_v1[agent.id]
                s_ = np.array(states_v1_[agent.id])
                a = actions_v1[agent.id]
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

            states_v1 = states_v1_

            # sums.append(sum_all)
            sums_random.append(sum_all_random)
            sums_v1.append(sum_all_v1)
            # sumt.append(rewards[0])  # agent 0
            # print('rl: ' + str(sum_all))
            print("rl-v1: " + str(sum_all_v1))
            print('random: ' + str(sum_all_random))
            print('global optimal: ' + str(self.global_optimal))

            if time % 1000 == 0 and time != 0:
                str2 = 'v1sums_random' + str(time) + '.txt'
                file = open(str2, 'w')
                file.write(str(sums_random))
                file.close()
                str3 = 'sums-v1' + str(time) + '.txt'
                file = open(str3, 'w')
                file.write(str(sums_v1))
                file.close()


game = Game()
game.play_game()
