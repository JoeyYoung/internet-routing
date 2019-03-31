"""
    Cut down action space,
    focus on each flow to choose action (next-hop)
"""

from generator import MiniGenerator
from dqn import DeepQNetwork
import tensorflow as tf
import numpy as np
import collections
import random
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "3"
gpu_options = tf.GPUOptions(allow_growth=True)


class Game:
    def __init__(self):
        # Internet topology
        self.generator = MiniGenerator(10, 2)
        self.generator.build_topology()

        self.RLs = self.generator.Ts + self.generator.Cs + self.generator.Ms + self.generator.CPs
        self.N = 12
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids

        self.TF = collections.defaultdict(dict)
        self.tf_num = 10
        self.TF[6][9] = 1
        self.TF[6][10] = 1
        self.TF[7][4] = 1
        self.TF[7][5] = 1
        self.TF[8][10] = 1
        self.TF[8][11] = 1
        self.TF[0][9] = 1
        self.TF[1][11] = 1
        self.TF[2][5] = 1
        self.TF[3][4] = 1

        self.global_optimal = 600
        self.episode = 0.8

        # for each agent, add [s,a,r,s'] as element. size
        self.experience_pool = collections.defaultdict(dict)
        self.pool_size = 50
        self.sample_size = 10
        for i in range(self.tf_num):
            for j in range(self.N):
                self.experience_pool[i][j] = []

    def play_game(self):
        print("play")
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        print('sess')

        """
            init states for every node:
                src, dst, neighbor, e-e, others' actions
        """
        # basic states
        states = collections.defaultdict(list)
        for i in range(self.N):
            # add neighbor
            for j in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][j] == 1:
                    states[i].append(0)

            # reachable end-to-end throughput (all advertised are considered here)
            node = self.ids[i]
            for d in node.table:    states[i].append(0)
            for d in node.table_peer:   states[i].append(0)
            for d in node.table_provider:   states[i].append(0)

        # combine others' states and last actions for each flow
        states_g = collections.defaultdict(list)
        for i in range(self.N):
            # add flow num
            states_g[i] = [0]
            # all agents' basic states
            for j in range(self.N):
                states_g[i] += states[j]
            # actions of all agents for all flows
            for k in range(self.tf_num):
                for q in range(self.N):
                    states_g[i].append(0)

        """
            create RL module
        """
        # TODO, give the action_labels
        for i in self.RLs:
            print("create mode for: " + str(i.id) + ", version -1")
            n_features_critic = len(states_g[i.id])  # len(states[i.id]) + 1
            n_features_actor = len(states[i.id]) + 1
            dqn = DeepQNetwork(sess, n_features_critic, i.n_actions, i.id, i.action_labels)
            i.set_dqn(dqn)
            sess.run(tf.global_variables_initializer())

        print("model created")

        """
            loop time as time epoch
        """
        TF = self.TF
        # keep updating
        actions = collections.defaultdict(dict)
        f_num = 0
        for i in TF.keys():
            for j in TF[i].keys():
                for k in range(self.N):
                    # TODO, init without path error
                    valida = self.ids[k].filter[j]
                    if -1 in valida:
                        actions[f_num][k] = 0
                    else:
                        actions[f_num][k] = self.ids[k].action_labels.index(random.choice(valida))
                f_num += 1

        sums = []
        for time in range(self.MAX):
            if time % 3000 == 0 and time != 0:
                self.episode /= 2
            # if time % 100 == 0 and time != 0:
            #     states = collections.defaultdict(list)
            #     for i in range(self.N):
            #         # add neighbor
            #         for j in range(len(self.generator.matrix[i])):
            #             if self.generator.matrix[i][j] == 1:
            #                 states[i].append(0)
            #
            #         # reachable end-to-end throughput (all advertised are considered here)
            #         node = self.ids[i]
            #         for d in node.table:    states[i].append(0)
            #         for d in node.table_peer:   states[i].append(0)
            #         for d in node.table_provider:   states[i].append(0)
            #
            #     # combine others' states and last actions for each flow
            #     states_g = collections.defaultdict(list)
            #     for i in range(self.N):
            #         # add flow num
            #         states_g[i] = [0]
            #         # all agents' basic states
            #         for j in range(self.N):
            #             states_g[i] += states[j]
            #         # actions of all agents for all flows
            #         for k in range(self.tf_num):
            #             for q in range(self.N):
            #                 states_g[i].append(0)
            #
            #     actions = collections.defaultdict(dict)
            #     f_num = 0
            #     for i in TF.keys():
            #         for j in TF[i].keys():
            #             for k in range(self.N):
            #                 # TODO, init without path error
            #                 valida = self.ids[k].filter[j]
            #                 if -1 in valida:
            #                     actions[f_num][k] = 0
            #                 else:
            #                     actions[f_num][k] = self.ids[k].action_labels.index(random.choice(valida))
            #             f_num += 1

            print("time: " + str(time))
            pro = random.random()
            train_state_pool = collections.defaultdict(dict)
            train_local_view = collections.defaultdict(dict)
            flow_num = 0
            sum_all = 0
            flow_actual_path = collections.defaultdict(list)
            rewards = {}
            for i in TF.keys():
                for j in TF[i].keys():
                    for agent in self.Ns:
                        # store state and state'
                        train_state_pool[flow_num][agent.id] = []
                        # specific one node to one flow
                        states_g[agent.id][0] = flow_num
                        ss = np.array(states_g[agent.id])

                        local_view = np.array([flow_num] + states[agent.id])
                        if pro > self.episode:
                            # TODO, use filter process, give the valid next-hops
                            valida = agent.filter[j]
                            if time >= 20000:
                                cnm = agent.dqn.choose_action(ss, valida)
                            else:
                                cnm = agent.dqn.choose_action(ss, valida)
                            actions[flow_num][agent.id] = cnm

                        # TODO, random need filter
                        else:
                            valida = agent.filter[j]
                            if -1 in valida:
                                actions[flow_num][agent.id] = 0
                            else:
                                actions[flow_num][agent.id] = agent.action_labels.index(random.choice(valida))

                        train_state_pool[flow_num][agent.id].append(ss)
                        train_local_view[flow_num][agent.id] = local_view

                    # update states to ss_
                    states_, rewards, sum_all, hh = self.update_state(flow_num, actions)
                    flow_actual_path[flow_num] = hh

                    states_g_ = collections.defaultdict(list)
                    for k in range(self.N):
                        states_g_[k] = [flow_num]
                        for q in range(self.N):
                            states_g_[k] += states_[q]
                        for z in actions.keys():
                            for x in actions[z].keys():
                                states_g_[k].append(actions[z][x])
                    flow_num += 1
                    states_g = states_g_
                    states = states_

            flow_num = 0
            for i in TF.keys():
                for j in TF[i].keys():
                    for agent in self.Ns:
                        # TODO, only make useful agents to learn
                        if agent not in flow_actual_path[flow_num][:len(flow_actual_path[flow_num])-1]:
                            continue
                        ss = train_state_pool[flow_num][agent.id][0]
                        ss_ = states_g[agent.id]  # states[agent.id]  #
                        ss_[0] = flow_num
                        ss_ = np.array(ss_)
                        # ss_ = np.array([flow_num] + ss_)
                        view = train_local_view[flow_num][agent.id]

                        cur_exp = [ss, ss_, actions[flow_num][agent.id], rewards[agent.id], view]
                        agent.dqn.store_transition(cur_exp[0], cur_exp[2], cur_exp[3], cur_exp[1])
                        agent.dqn.learn()
                    flow_num += 1

            sums.append(sum_all)
            print('game12-dqn-glb: ' + str(sum_all))
            if time % 3000 == 0 and time != 0:
                str1 = 'game12-dqn-glb' + str(time) + '.txt'
                file = open(str1, 'w')
                file.write(str(sums))
                file.close()

    def update_state(self, cur_flow, actions):
        TF = self.TF
        actual_flow = collections.defaultdict(dict)
        flow_num = 0
        path_return = []
        for i in TF.keys():
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
                    # TODO, action type changed
                    action = self.ids[cur].action_labels[actions[flow_num][cur]]
                    cur = action
                    hop_path.append(self.ids[cur])

                if flag == 0:
                    actual_flow[i][j] = hop_path
                    if flow_num == cur_flow:
                        path_return = hop_path
                else:
                    print("error in hop path")
                    print("==================from " + str(i) + ' to ' + str(j))
                    for i in hop_path:
                        print(i.id)
                    print(actions)
                    sys.exit(0)
                flow_num += 1

        link_load = np.zeros([self.N, self.N])
        for i in actual_flow.keys():
            for j in actual_flow[i].keys():
                path = actual_flow[i][j]
                for k in range(len(path) - 1):
                    e1 = path[k]
                    e2 = path[k + 1]
                    link_load[e1.id][e2.id] += TF[i][j]
                    link_load[e2.id][e1.id] += TF[i][j]

        # store flow information on each link
        # node1:node2:[[src,dst],[src,dst]]
        # node2:node1:[[src,dst],...]
        link_flow_records = collections.defaultdict(dict)
        for i in range(self.N):
            for j in range(self.N):
                if self.generator.matrix[i][j] == 1:
                    link_flow_records[i][j] = []
                    link_flow_records[j][i] = []

        ee_throughput = np.zeros([self.N, self.N])
        for i in actual_flow.keys():
            # input node i
            for j in actual_flow[i].keys():
                flow = [i, j]
                path = actual_flow[i][j]
                temp_min = 9999
                for k in range(len(path) - 1):
                    node1 = path[k]
                    node2 = path[k + 1]
                    # record flow 'i j' on link 'node1 node2'
                    link_flow_records[node1.id][node2.id].append(flow)
                    link_flow_records[node2.id][node1.id].append(flow)

                    ee = 100 / link_load[node1.id][node2.id]
                    if ee < temp_min:
                        temp_min = ee
                ee_throughput[i][j] = temp_min
        # ee is basic throughput for each flow, need to be increased

        link_residue = collections.defaultdict(dict)
        for i in range(self.N):
            for j in range(self.N):
                if self.generator.matrix[i][j] == 1:
                    # for link 'i j'
                    remain = 100
                    for flow in link_flow_records[i][j]:
                        remain -= ee_throughput[flow[0]][flow[1]]
                    link_residue[i][j] = remain
                    link_residue[j][i] = remain

        # increase each flow throughput, update link_residue
        for i in actual_flow.keys():
            for j in actual_flow[i].keys():
                path = actual_flow[i][j]
                temp_min = 9999
                for k in range(len(path) - 1):
                    node1 = path[k]
                    node2 = path[k + 1]
                    if link_residue[node1.id][node2.id] < temp_min:
                        temp_min = link_residue[node1.id][node2.id]
                # increase
                if temp_min == 0:
                    continue
                ee_throughput[i][j] += temp_min
                # update
                for k in range(len(path) - 1):
                    node1 = path[k]
                    node2 = path[k + 1]
                    link_residue[node1.id][node2.id] -= temp_min
                    link_residue[node2.id][node1.id] -= temp_min

        states_ = collections.defaultdict(list)
        for i in range(self.N):
            for j in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][j] == 1:
                    states_[i].append(link_load[i][j])
                    # if link_load[i][j] == 0:
                    #     states_[i].append(100)
                    # else:
                    #     states_[i].append(100 / link_load[i][j])

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
                avg = sum(temp_table[i]) / len(temp_table[i])
                states_[agent.id].append(avg)

        sum_all = 0
        for i in range(self.N):
            for j in range(self.N):
                sum_all += ee_throughput[i][j]

        return states_, rewards, sum_all, path_return


cutgame = Game()
cutgame.play_game()
