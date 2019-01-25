import numpy as np
from scipy import optimize

'''
    input:
        topology: 二维01矩阵关系拓扑
        traffic: 二维01矩阵表示s-t的需求矩阵
    TODO， 考虑整数规划
'''


class Linprog:
    def __init__(self, matrix, traffic):
        print("init linear program")
        self.matrix = matrix
        self.traffic = traffic

    def solve_linprog(self):
        print("begin solve global optimal")
        index_map = {}
        index_map_v = {}
        pars = []
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
        for key in index_map_v.keys():
            c_list[index_map_v[key]] = -1

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
        print("constrains one done")

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
        print("constrains two done")

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

        print("constrains three done")

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

        print("constrains four done")

        a = np.array(a_list)
        b = np.array(b_list)

        print("begin computing")
        res = optimize.linprog(c, A_ub=a, b_ub=b, bounds=(0, None), method='interior-point', options={'maxiter':3000, 'disp': True})
        print(res)
        print(res.nit)
        print(res.message)
        return res.fun

        # TODO, 基于拓扑和F，定义变量集合
        # TODO, 封装一下各个vf
        # TODO，限制系数定义
