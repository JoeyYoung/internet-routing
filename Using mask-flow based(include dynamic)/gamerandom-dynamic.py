"""
    Cut down action space,
    focus on each flow to choose action (next-hop)
"""

from generator import MidGenerator
import numpy as np
import collections
import random
import os
import sys

class Game:
    def __init__(self):
        # Internet topology
        self.generator = MidGenerator(29, 1)
        self.generator.build_topology()

        self.RLs = self.generator.Ts + self.generator.Cs + self.generator.Ms + self.generator.CPs
        self.N = 30
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids

        # define time epoch
        self.tf_num = 35
        self.TF_time = collections.defaultdict(dict)
        # 24 flow
        self.TF_time[0][7] = 1
        self.TF_time[0][10] = 2
        self.TF_time[0][11] = 3
        self.TF_time[0][14] = 1
        self.TF_time[0][15] = 2
        self.TF_time[0][18] = 3
        self.TF_time[0][19] = 1
        self.TF_time[0][22] = 2
        self.TF_time[0][23] = 3
        self.TF_time[0][26] = 1
        self.TF_time[0][27] = 2
        self.TF_time[0][29] = 3
        self.TF_time[7][11] = 1
        self.TF_time[10][14] = 2
        self.TF_time[11][15] = 3
        self.TF_time[14][18] = 1
        self.TF_time[15][19] = 2
        self.TF_time[18][22] = 3
        self.TF_time[19][23] = 1
        self.TF_time[22][26] = 2
        self.TF_time[23][27] = 3
        self.TF_time[26][29] = 1
        self.TF_time[27][7] = 2
        self.TF_time[29][10] = 3

        # 11 flows
        self.TF_time[10][15] = 3
        self.TF_time[14][26] = 2
        self.TF_time[18][29] = 1
        self.TF_time[19][7] = 3
        self.TF_time[0][8] = 2
        self.TF_time[23][11] = 1
        self.TF_time[27][16] = 3
        self.TF_time[24][13] = 2
        self.TF_time[11][7] = 1
        self.TF_time[22][9] = 2
        self.TF_time[26][11] = 1

        # in order, index as id
        self.TF_id = []
        self.TF_id.append([0, 7])
        self.TF_id.append([0, 10])
        self.TF_id.append([0, 11])
        self.TF_id.append([0, 14])
        self.TF_id.append([0, 15])
        self.TF_id.append([0, 18])
        self.TF_id.append([0, 19])
        self.TF_id.append([0, 22])
        self.TF_id.append([0, 23])
        self.TF_id.append([0, 26])
        self.TF_id.append([0, 27])
        self.TF_id.append([0, 29])
        self.TF_id.append([7, 11])
        self.TF_id.append([10, 14])
        self.TF_id.append([11, 15])
        self.TF_id.append([14, 18])
        self.TF_id.append([15, 19])
        self.TF_id.append([18, 22])
        self.TF_id.append([19, 23])
        self.TF_id.append([22, 26])
        self.TF_id.append([23, 27])
        self.TF_id.append([26, 29])
        self.TF_id.append([27, 7])
        self.TF_id.append([29, 10])

        self.TF_id.append([10, 15])
        self.TF_id.append([14, 26])
        self.TF_id.append([18, 29])
        self.TF_id.append([19, 7])
        self.TF_id.append([0, 8])
        self.TF_id.append([23, 11])
        self.TF_id.append([27, 16])
        self.TF_id.append([24, 13])
        self.TF_id.append([11, 7])
        self.TF_id.append([22, 9])
        self.TF_id.append([26, 11])

        self.episode = 1

        # for each agent, add [s,a,r,s'] as element. size
        self.experience_pool = collections.defaultdict(list)
        self.pool_size = 200
        self.sample_size = 16

    def play_game(self):
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

        # TODO, combine others' states and last actions for each flow
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

        print("model created")

        """
            loop time as time epoch
        """
        # keep updating
        actions = collections.defaultdict(dict)
        for i in self.TF_time.keys():
            for j in self.TF_time[i].keys():
                f_num = self.TF_id.index([i, j])
                for k in range(self.N):
                    valida = self.ids[k].filter[j]
                    if -1 in valida:
                        actions[f_num][k] = 0
                    else:
                        actions[f_num][k] = self.ids[k].action_labels.index(random.choice(valida))

        sums = []
        sums_rand = []

        # init tf
        TF = collections.defaultdict(dict)
        TF[0][7] = 0
        TF[0][10] = 0
        TF[0][11] = 0
        TF[0][14] = 0
        TF[0][15] = 0
        TF[0][18] = 0
        TF[0][19] = 0
        TF[0][22] = 0
        TF[0][23] = 0
        TF[0][26] = 0
        TF[0][27] = 0
        TF[0][29] = 0
        TF[7][11] = 0
        TF[10][14] = 0
        TF[11][15] = 0
        TF[14][18] = 0
        TF[15][19] = 0
        TF[18][22] = 0
        TF[19][23] = 0
        TF[22][26] = 0
        TF[23][27] = 0
        TF[26][29] = 0
        TF[27][7] = 0
        TF[29][10] = 0

        queue = collections.deque([24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34])
        for time in range(1):
            # check if any flow out time
            expire = []
            for i in TF.keys():
                for j in TF[i].keys():
                    if TF[i][j] > self.TF_time[i][j]:
                        # inject new flow from queue
                        # store old flow to queue
                        expire.append([i, j])

            for f in expire:
                i = f[0]
                j = f[1]
                TF[i].pop(j)
                queue.append(self.TF_id.index([i, j]))
                for k in actions[self.TF_id.index([i, j])].keys():
                    actions[self.TF_id.index([i, j])][k] = 0

                new_flow = queue.popleft()
                TF[self.TF_id[new_flow][0]][self.TF_id[new_flow][1]] = 0

            for round in range(3000):
                whole_time = time * 3000 + round
                print("time: " + str(whole_time))

                pro = random.random()
                train_state_pool = collections.defaultdict(dict)
                train_local_view = collections.defaultdict(dict)
                flow_actual_path = collections.defaultdict(list)
                sum_all = 0
                rewards = {}
                for i in TF.keys():
                    for j in TF[i].keys():
                        for agent in self.Ns:
                            flow_num = self.TF_id.index([i, j])
                            # store state and state'
                            train_state_pool[flow_num][agent.id] = []
                            # specific one node to one flow
                            states_g[agent.id][0] = flow_num
                            ss = states_g[agent.id]
                            ss = np.array(ss)

                            local_view = np.array([flow_num] + states[agent.id])
                            if pro > self.episode:
                                valida = agent.filter[j]
                                cnm = agent.actor.choose_action(local_view, valida, method='prob')
                                actions[flow_num][agent.id] = cnm
                            else:
                                valida = agent.filter[j]
                                if -1 in valida:
                                    actions[flow_num][agent.id] = 0
                                else:
                                    actions[flow_num][agent.id] = agent.action_labels.index(random.choice(valida))

                            train_state_pool[flow_num][agent.id].append(ss)
                            train_local_view[flow_num][agent.id] = local_view

                        flow_num = self.TF_id.index([i, j])
                        # update states to ss_
                        states_, rewards, sum_all, hh = self.update_state(TF, flow_num, actions)

                        flow_actual_path[flow_num] = hh
                        states_g_ = collections.defaultdict(list)
                        for k in range(self.N):
                            states_g_[k] = [flow_num]
                            for q in range(self.N):
                                states_g_[k] += states_[q]
                            count = 0
                            for z in actions.keys():
                                for x in actions[z].keys():
                                    states_g_[k].append(actions[z][x])
                                    count += 1
                        states_g = states_g_
                        states = states_

                sums.append(sum_all)
                # sums_rand.append(rand_value)
                print('game30-dtf-random: ' + str(sum_all))
                # print('random: ' + str(rand_value))
                if whole_time % 3000 == 0 and whole_time != 0:
                    str1 = 'game30-dtf-random' + str(whole_time) + '.txt'
                    file = open(str1, 'w')
                    file.write(str(sums))
                    file.close()

            for i in TF.keys():
                for j in TF[i].keys():
                    TF[i][j] += 1

    def update_state(self, tf, cur_flow, actions):
        TF = tf
        actual_flow = collections.defaultdict(dict)
        for i in TF.keys():
            for j in TF[i].keys():
                flow_num = self.TF_id.index([i, j])
                hop_path = []
                cur = i
                hop_path.append(self.ids[cur])
                flag = -1
                count = 0
                while cur != j:
                    count += 1
                    if count > 10:
                        print("error in hop path")
                        flag = 1
                        break
                    flag = 0
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
                    print(i.actor.oldp)
                    print(i.actor.newp)
                    sys.exit(0)

        link_load = np.zeros([self.N, self.N])
        for i in actual_flow.keys():
            for j in actual_flow[i].keys():
                path = actual_flow[i][j]
                for k in range(len(path) - 1):
                    e1 = path[k]
                    e2 = path[k + 1]
                    link_load[e1.id][e2.id] += 1
                    link_load[e2.id][e1.id] += 1

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
