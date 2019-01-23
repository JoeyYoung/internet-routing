import numpy as np
import pulp
from scipy import optimize

'''
    input:
        topology: 二维01矩阵关系拓扑
        traffic: 二维01矩阵表示s-t的需求矩阵
    TODO， 考虑整数规划
'''


class IntLp:
    def __init__(self, matrix, traffic):
        print("init linear program")
        self.matrix = matrix
        self.traffic = traffic

    def do_ilp(self, objective, constrains):
        prob = pulp.LpProblem('LP1', pulp.LpMaximize)
        prob += objective
        for cons in constrains:
            prob += cons
        status = prob.solve()
        if status != 1:
            print("fail in do INT status")
            return None
        else:
            print('Int objective:')
            print(prob.objective)
            return prob.objective

    def solve_ilp(self):
        print("begin solve global int optimal")
        index_map = {}
        index_map_v = {}
        pars = []
        '''
            init pars
        '''
        for src in self.traffic.keys():
            for dst in self.traffic.keys():
                for i in range(self.matrix.shape[0]):
                    for j in range(self.matrix.shape[1]):
                        if self.matrix[i][j] == 0: continue
                        par = []
                        par.append(src)
                        par.append(dst)
                        par.append(i)
                        par.append(j)
                        index_map[str(par)] = len(pars)
                        # flow s-t on edge i to j
                        pars.append(par)
                v = []
                v.append(src)
                v.append(dst)
                index_map_v[str(v)] = len(pars)
                pars.append(v)

        c_list = [0] * len(pars)
        c_list_int = [0] * len(pars)
        for key in index_map_v.keys():
            c_list[index_map_v[key]] = -1
            c_list_int[index_map_v[key]] = 1

        c = np.array(c_list)

        a_list = []
        b_list = []

        '''
            i in not source and destination for each flow, b = 0
        '''
        for src in self.traffic.keys():
            for dst in self.traffic.keys():
                temp = [0] * len(pars)
                for i in range(self.matrix.shape[0]):
                    if i != src and i != dst:
                        for j in range(self.matrix.shape[1]):
                            if self.matrix[i][j] == 1:
                                key_out = []
                                key_out.append(src)
                                key_out.append(dst)
                                key_out.append(i)
                                key_out.append(j)
                                temp[index_map[str(key_out)]] = -1
                                key_in = []
                                key_in.append(src)
                                key_in.append(dst)
                                key_in.append(j)
                                key_in.append(i)
                                temp[index_map[str(key_in)]] = 1
                a_list.append(temp)
                b_list.append(0)

        '''
            i is the source for each flow
        '''
        for src in self.traffic.keys():
            for dst in self.traffic.keys():
                temp = [0] * len(pars)
                for i in range(self.matrix.shape[0]):
                    if i == src:
                        for j in range(self.matrix.shape[1]):
                            if self.matrix[i][j] == 1:
                                key_out = []
                                key_out.append(src)
                                key_out.append(dst)
                                key_out.append(i)
                                key_out.append(j)
                                temp[index_map[str(key_out)]] = -1
                                key_in = []
                                key_in.append(src)
                                key_in.append(dst)
                                key_in.append(j)
                                key_in.append(i)
                                temp[index_map[str(key_in)]] = 1
                # add vf
                key_v = []
                key_v.append(src)
                key_v.append(dst)
                temp[index_map_v[str(key_v)]] = 1
                a_list.append(temp)
                b_list.append(0)

        '''
            i is the destination for each flow
        '''
        for src in self.traffic.keys():
            for dst in self.traffic.keys():
                temp = [0] * len(pars)
                for i in range(self.matrix.shape[0]):
                    if i == dst:
                        for j in range(self.matrix.shape[1]):
                            if self.matrix[i][j] == 1:
                                key_out = []
                                key_out.append(src)
                                key_out.append(dst)
                                key_out.append(i)
                                key_out.append(j)
                                temp[index_map[str(key_out)]] = -1
                                key_in = []
                                key_in.append(src)
                                key_in.append(dst)
                                key_in.append(j)
                                key_in.append(i)
                                temp[index_map[str(key_in)]] = 1
                # add vf
                key_v = []
                key_v.append(src)
                key_v.append(dst)
                temp[index_map_v[str(key_v)]] = -1
                a_list.append(temp)
                b_list.append(0)

        '''
            add utility constrains
        '''
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                if self.matrix[i][j] == 0: continue
                temp = [0] * len(pars)
                for src in self.traffic.keys():
                    for dst in self.traffic.keys():
                        key_u = []
                        key_u.append(src)
                        key_u.append(dst)
                        key_u.append(i)
                        key_u.append(j)
                        temp[index_map[str(key_u)]] = 1
                        key_u_r = []
                        key_u_r.append(src)
                        key_u_r.append(dst)
                        key_u_r.append(j)
                        key_u_r.append(i)
                        temp[index_map[str(key_u_r)]] = 1
                a_list.append(temp)
                # Modify the utility
                b_list.append(100)

        '''
            USE PULP solve INTLINEAR
        '''
        print('step into INT problem')
        V_NUM = len(pars)
        variables = [pulp.LpVariable('X%d' % i, lowBound=0, cat=pulp.LpInteger) for i in range(0, V_NUM)]
        c_int = c_list_int
        objective = sum([c_int[i] * variables[i] for i in range(0, V_NUM)])

        constrains = []
        for k in range(len(a_list)):
            a_con = a_list[k]  # list
            b_con = b_list[k]  # value
            constrains.append(sum([a_con[i] * variables[i] for i in range(0, V_NUM)]) <= b_con)

        print('packet into INT problem')
        res = self.do_ilp(objective, constrains)
        return res
