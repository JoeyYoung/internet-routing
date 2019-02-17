"""
    Cut down action space,
    focus on each flow to choose action (next-hop)
"""

from generator import MiniGenerator
import numpy as np
import collections
import random


class Game:
    def __init__(self):
        # Internet topology
        self.generator = MiniGenerator(10, 2)
        self.generator.build_topology()
        self.generator.build_directed_matrix()

        self.RLs = self.generator.Ts + self.generator.Cs + self.generator.Ms + self.generator.CPs
        self.N = 12
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids

        # for each agent, add [s,a,r,s'] as element. size
        self.experience_pool = collections.defaultdict(list)
        self.pool_size = 10

        # TODO, define TF, Matrix, Linprog
        self.TF = collections.defaultdict(dict)
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

    def play_game(self):
        """
            loop time as time epoch
        """
        TF = self.TF
        # keep updating
        actions = collections.defaultdict(dict)
        for i in range(10):
            for j in range(self.N):
                actions[i][j] = 0

        sums = []
        for time in range(self.MAX):
            print("begin time epoch: " + str(time))
            train_state_pool = collections.defaultdict(dict)
            flow_num = 0
            sum_all = 0
            for i in TF.keys():
                for j in TF[i].keys():
                    for agent in self.Ns:
                        actions[flow_num][agent.id] = random.randint(0, agent.n_actions - 1)

                    # update states to ss_
                    sum_all = self.update_state(flow_num, actions)

                    flow_num += 1

            sums.append(sum_all)
            print('cut-random: ' + str(sum_all))
            if time % 10000 == 0 and time != 0:
                str1 = 'cut-mini-random' + str(time) + '.txt'
                file = open(str1, 'w')
                file.write(str(sums))
                file.close()

    def update_state(self, cur_flow, actions):
        TF = self.TF
        actual_flow = collections.defaultdict(dict)
        flow_num = 0
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
                        print("error in hop path")
                        flag = 1
                        break
                    flag = 0
                    action = self.ids[cur].action_labels[actions[flow_num][cur]]
                    if action.get(j) is not None:
                        cur = action[j]
                        hop_path.append(self.ids[cur])
                    else:
                        flag = 1
                        print("error in hop path")
                        break
                if flag == 0:
                    actual_flow[i][j] = hop_path
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

        # TODO, increase each flow throughput, update link_residue
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

        sum_all = 0
        for i in range(self.N):
            for j in range(self.N):
                sum_all += ee_throughput[i][j]

        return sum_all


cutgame = Game()
cutgame.play_game()
