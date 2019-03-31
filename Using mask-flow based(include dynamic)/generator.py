import numpy as np
import random
from nodes import T
from nodes import M
from nodes import CP
from nodes import C


class Generator:
    # init with nodes number and T number
    def __init__(self, n, nT):
        # set the number of each type
        self.n = n
        self.nT = nT
        self.nM = 30
        self.nCP = 10
        self.nC = 0

        # number of providers, random (1,2)
        self.dM = 1  # 2+2.5n/10000
        self.dCP = 1  # 2+1.5n/10000
        self.dC = 2  # 1+5n/10000

        # number of peers
        self.pM = 0  # 1+2n/10000
        self.pCP_M = 0  # 0.2 + 2 * n / 10000
        self.pCP_CP = 0  # 0.05 + 5 * n / 100000

        # probability to choose T as provider
        self.tM = 1  # 0.375
        self.tCP = 0.2
        self.tC = 0.2

        # collections for nodes
        self.Ts = []
        self.Ms = []
        self.CPs = []
        self.Cs = []
        # id: actual node
        self.ids = {}

        # label id from 0 ~ nT-1
        for i in range(self.nT):
            t = T(i)
            self.ids[t.id] = t
            self.Ts.append(t)

        # label id from nT ~ nT+nM-1
        for i in range(self.nM):
            m = M(i + self.nT)
            self.ids[m.id] = m
            self.Ms.append(m)

        # label id from nT+nM ~ nT+nM+nCP-1
        for i in range(self.nCP):
            cp = CP(i + self.nT + self.nM)
            self.ids[cp.id] = cp
            self.CPs.append(cp)

        # label id from nT+nM+nCP ~ nT+nM+nCP+nC-1
        for i in range(self.nC):
            c = C(i + self.nT + self.nM + self.nCP)
            self.ids[c.id] = c
            self.Cs.append(c)

    def add_t_nodes(self):
        # for t in self.Ts:
        #     for t_p in self.Ts:
        #         if t_p == t: continue
        #         if t_p in t.peers_T: continue
        #         t.peers_T.append(t_p)
        #         t_p.peers_T.append(t)
        #         t.degree += 1
        #         t_p.degree += 1

        for i in range(self.nT - 1):
            self.Ts[i].peers_T.append(self.Ts[i + 1])
            self.Ts[i + 1].peers_T.append(self.Ts[i])
            self.Ts[i].degree += 1
            self.Ts[i + 1].degree += 1
        self.Ts[self.nT - 1].peers_T.append(self.Ts[0])
        self.Ts[0].peers_T.append(self.Ts[self.nT - 1])
        self.Ts[self.nT - 1].degree += 1
        self.Ts[0].degree += 1

    def add_m_nodes(self):
        for m in self.Ms:
            # TODO, consider distribution
            temp = [2]
            num_providers = random.choice(temp)

            # TODO, consider preference

            # number has been determined, sorted, here degree added has no impact
            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tM:
                    # provider is T, build relationship
                    pt = random.choice(self.Ts)
                    while pt in m.providers_T is True:
                        pt = random.choice(self.Ts)
                    m.providers_T.append(pt)
                    m.degree += 1
                    pt.customers_M.append(m)
                    pt.degree += 1

                else:
                    # provider is M, build relationship
                    pm = self.Ms[im]
                    while pm == m is False:
                        im += 1
                        pm = self.Ms[im]
                    m.providers_M.append(pm)
                    m.degree += 1
                    pm.customers_M.append(m)
                    pm.degree += 1
                    im += 1

    def add_cp_nodes(self):
        im = 0
        for cp in self.CPs:
            pm = self.Ms[im]
            pt = random.choice(self.Ts)
            while pt in pm.providers_T:
                pt = random.choice(self.Ts)

            cp.providers_M.append(pm)
            cp.degree += 1
            pm.customers_CP.append(cp)
            pm.degree += 1

            cp.providers_T.append(pt)
            cp.degree += 1
            pt.customers_CP.append(cp)
            pt.degree += 1

            im += 1
            # temp = [0]
            # num_providers = random.choice(temp)
            # random.shuffle(self.Ts)
            # random.shuffle(self.Ms)
            #
            # it = im = 0
            # for i in range(num_providers):
            #     pro = random.random()
            #     if pro <= self.tCP:
            #         # provider is T, build relationship
            #         pt = self.Ts[it]
            #         cp.providers_T.append(pt)
            #         cp.degree += 1
            #         pt.customers_CP.append(cp)
            #         pt.degree += 1
            #         it += 1
            #
            #     else:
            #         # provider is M, build relationship
            #         pm = self.Ms[im]
            #
            #         cp.providers_M.append(pm)
            #         cp.degree += 1
            #         pm.customers_CP.append(cp)
            #         pm.degree += 1
            #         im += 1

    def add_c_nodes(self):
        # TODO, m > c
        im = 0
        for c in self.Cs:
            # pm = self.Ms[im]
            # pt = random.choice(pm.providers_T)
            #
            # c.providers_M.append(pm)
            # c.degree += 1
            # pm.customers_C.append(c)
            # pm.degree += 1
            #
            # c.providers_T.append(pt)
            # c.degree += 1
            # pt.customers_C.append(c)
            # pt.degree += 1
            #
            # im += 1
            temp = [1]
            num_providers = random.choice(temp)

            random.shuffle(self.Ts)
            random.shuffle(self.Ms)
            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tC:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    while pt in c.providers_T:
                        it += 1
                        pt = self.Ts[it]
                    c.providers_T.append(pt)
                    c.degree += 1
                    pt.customers_C.append(c)
                    pt.degree += 1
                    it += 1

                else:
                    # provider is M, build relationship
                    pm = self.Ms[im]
                    while pm in c.providers_M:
                        im += 1
                        pm = self.Ms[im]
                    c.providers_M.append(pm)
                    c.degree += 1
                    pm.customers_C.append(c)
                    pm.degree += 1
                    im += 1

    def add_m_peers(self):
        for m in self.Ms:
            number_peers = random.randint(1, 2)
            # build relationship
            im = 0
            for i in range(number_peers):
                pm = self.Ms[im]
                # avoid self
                if pm == m:
                    im += 1
                    pm = self.Ms[im]
                # avoid relationship that have been already built
                while pm in m.providers_M or pm in m.customers_M:
                    im += 1
                    pm = self.Ms[im]

                m.peers_M.append(pm)
                m.peer_degree += 1
                m.degree += 1
                pm.peers_M.append(m)
                pm.peer_degree += 1
                pm.degree += 1
                im += 1

    def add_cp_peers(self):
        for cp in self.CPs:
            number_peers_m = random.randint(0, 1)  # self.pCP_M
            number_peers_cp = random.randint(0, 1)  # self.pCP_CP

            # build relationship
            for i in range(number_peers_m):
                pm = random.choice(self.Ms)
                while pm in cp.providers_M:
                    pm = random.choice(self.Ms)
                cp.peers_M.append(pm)
                pm.peers_CP.append(cp)
                pm.peer_degree += 1
                cp.degree += 1
                pm.degree += 1
            for i in range(number_peers_cp):
                cpp = random.choice(self.CPs)
                while cpp == cp:
                    cpp = random.choice(self.CPs)
                cp.peers_CP.append(cpp)
                cpp.peers_CP.append(cp)
                cp.degree += 1
                cpp.degree += 1

    """
        considering BGP advertisement to providers
    """

    def advertise_c_to_provider(self):
        # from low to high. advertise learned from customer to provider(T, M), M recursion
        for c in self.Cs:
            # destination: c.id
            # advertise itself
            path = []
            path.insert(0, c)
            c.table[c.id].append(path)
            # advertise to its T provider
            for c_provider in c.providers_T:
                path_new = path[:]
                path_new.insert(0, c_provider)
                c_provider.table[c.id].append(path_new)

            for c_provider in c.providers_M:
                path_new = path[:]
                path_new.insert(0, c_provider)
                c_provider.table[c.id].append(path_new)
                # continue to advertise this M to provider
                self.advertise_m_to_provider(c_provider)

    def advertise_m_to_provider(self, m):
        # used for recursion. advertise learned from customer to provider(T, M), M recursion
        for m_provider in m.providers_T:
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path[:]
                    path_new.insert(0, m_provider)
                    if path_new not in m_provider.table[destination]:
                        m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            if path_self not in m_provider.table[m.id]:
                m_provider.table[m.id].append(path_self)

        # Not in this loop if M's provider is only T
        for m_provider in m.providers_M:
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path[:]
                    path_new.insert(0, m_provider)
                    if path_new not in m_provider.table[destination]:
                        m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            if path_self not in m_provider.table[m.id]:
                m_provider.table[m.id].append(path_self)
            self.advertise_m_to_provider(m_provider)

    def advertise_cp_to_provider(self):
        # from low to high. advertise learned from customer to provider(T, M), M recursion
        for cp in self.CPs:
            # destination: cp.id
            # advertise itself
            path = []
            path.insert(0, cp)
            cp.table[cp.id].append(path)
            # advertise to its T provider
            for cp_provider in cp.providers_T:
                path_new = path[:]
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)

            for cp_provider in cp.providers_M:
                path_new = path[:]
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)
                # continue to advertise this M to provider
                self.advertise_m_to_provider(cp_provider)

    """
        considering BGP advertisement to peers
        considering that prefer customer to peer to provider,
        put this preference into the function
    """

    def advertise_t_to_peers(self):
        # advertise learned from customer to peers
        for t in self.Ts:
            for t_peer in t.peers_T:
                for destination in t.table:
                    if t_peer.table.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_peer)
                        t_peer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_peer)
                t_peer.table_peer[t.id].append(path_self)

    def advertise_m_to_peers(self):
        # advertise learned from customer to peers, to m, to cp
        for m in self.Ms:
            for m_Mpeer in m.peers_M:
                for destination in m.table:
                    if m_Mpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, m_Mpeer)
                        m_Mpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, m)
                path_self.insert(0, m_Mpeer)
                m_Mpeer.table_peer[m.id].append(path_self)
            for m_CPpeer in m.peers_CP:
                for destination in m.table:
                    if m_CPpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, m_CPpeer)
                        m_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, m)
                path_self.insert(0, m_CPpeer)
                m_CPpeer.table_peer[m.id].append(path_self)

    def advertise_cp_to_peers(self):
        # TODO, advertise learned from customer to peers, to cp, to m
        for cp in self.CPs:
            for cp_Mpeer in cp.peers_M:
                for destination in cp.table:
                    if cp_Mpeer.table.get(destination) is not None: continue
                    pathes = cp.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, cp_Mpeer)
                        cp_Mpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_Mpeer)
                cp_Mpeer.table_peer[cp.id].append(path_self)
            for cp_CPpeer in cp.peers_CP:
                for destination in cp.table:
                    if cp_CPpeer.table.get(destination) is not None: continue
                    pathes = cp.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, cp_CPpeer)
                        cp_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_CPpeer)
                cp_CPpeer.table_peer[cp.id].append(path_self)

    """
        considering BGP advertisement to customer
    """

    def advertise_t_to_customers(self):
        # advertise all table(peers, pc) to customers
        for t in self.Ts:
            for t_Ccustomer in t.customers_C:
                for destination in t.table:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table_provider[t.id].append(path_self)
            print('end c')

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table_provider[t.id].append(path_self)
            print('end cp')

            for t_Mcustomer in t.customers_M:
                for destination in t.table:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Mcustomer)
                t_Mcustomer.table_provider[t.id].append(path_self)
            print('end m')

    def advertise_m_to_customers(self):
        # advertise all table(peers, pc) to customers
        for t in self.Ms:
            for t_Ccustomer in t.customers_C:
                for destination in t.table:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table_provider[t.id].append(path_self)

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table_provider[t.id].append(path_self)

    def advertise_self_to_self(self):
        for i in self.Ts:
            temp = []
            temp.append(i)
            if temp not in i.table[i.id]:
                i.table[i.id].append(temp)
        for i in self.Ms:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
        for i in self.CPs:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
        for i in self.Cs:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)

    def build_matrix(self):
        for t in self.Ts:
            for c_m in t.customers_M:
                self.matrix[t.id][c_m.id] = 1
                self.matrix[c_m.id][t.id] = 1
            for c_cp in t.customers_CP:
                self.matrix[t.id][c_cp.id] = 1
                self.matrix[c_cp.id][t.id] = 1
            for c_c in t.customers_C:
                self.matrix[t.id][c_c.id] = 1
                self.matrix[c_c.id][t.id] = 1
            for p_t in t.peers_T:
                self.matrix[t.id][p_t.id] = 1
                self.matrix[p_t.id][t.id] = 1

        for m in self.Ms:
            for c_m in m.customers_M:
                self.matrix[m.id][c_m.id] = 1
                self.matrix[c_m.id][m.id] = 1
            for c_cp in m.customers_CP:
                self.matrix[m.id][c_cp.id] = 1
                self.matrix[c_cp.id][m.id] = 1
            for c_c in m.customers_C:
                self.matrix[m.id][c_c.id] = 1
                self.matrix[c_c.id][m.id] = 1
            for p_m in m.peers_M:
                self.matrix[m.id][p_m.id] = 1
                self.matrix[p_m.id][m.id] = 1
            for p_cp in m.peers_CP:
                self.matrix[m.id][p_cp.id] = 1
                self.matrix[p_cp.id][m.id] = 1

        for cp in self.CPs:
            for p_cp in cp.peers_CP:
                self.matrix[cp.id][p_cp.id] = 1
                self.matrix[p_cp.id][cp.id] = 1

    def build_topology(self):
        self.add_t_nodes()
        self.add_m_nodes()
        self.add_c_nodes()
        self.add_cp_nodes()
        self.add_m_peers()
        self.add_cp_peers()
        print("nodes added")

        self.advertise_c_to_provider()
        print("advertise c to provider")
        self.advertise_cp_to_provider()
        print("advertise cp to provider")
        # advertise for M that has no customer
        for m in self.Ms:
            if len(m.customers_C) == 0:
                self.advertise_m_to_provider(m)
        print("advertise m to provider")
        self.advertise_t_to_peers()
        print("advertise t to peer")
        self.advertise_m_to_peers()
        print("advertise m to peer")
        self.advertise_cp_to_peers()
        print("advertise cp to peer")
        self.advertise_t_to_customers()
        print("advertise t to customer")
        self.advertise_m_to_customers()
        print("advertise m to customer")
        self.advertise_self_to_self()
        print("advertise self to self")
        print("advertisement finished")

        for i in self.Ts:
            i.init_action_label_next()
        print("============")
        for i in self.Ms:
            i.init_action_label_next()
        print("============")
        for i in self.CPs:
            i.init_action_label_next()
        print("============")
        for i in self.Cs:
            i.init_action_label_next()
        print("============")


"""
    Used for a defined topology 12 nodes, 10+2
"""


class MiniGenerator:
    def __init__(self, n, nT):
        self.n = n
        self.nT = nT
        self.nM = 4
        self.nCP = 6
        self.nC = 0
        self.matrix = np.zeros([self.n + self.nT, self.n + self.nT])

        self.Ts = []
        self.Ms = []
        self.CPs = []
        self.Cs = []
        # id: actual node
        self.ids = {}

        # label id from 0 ~ nT-1
        for i in range(self.nT):
            t = T(i)
            self.ids[t.id] = t
            self.Ts.append(t)

        # label id from nT ~ nT+nM-1
        for i in range(self.nM):
            m = M(i + self.nT)
            self.ids[m.id] = m
            self.Ms.append(m)

        # label id from nT+nM ~ nT+nM+nCP-1
        for i in range(self.nCP):
            cp = CP(i + self.nT + self.nM)
            self.ids[cp.id] = cp
            self.CPs.append(cp)

        # label id from nT+nM+nCP ~ nT+nM+nCP+nC-1
        for i in range(self.nC):
            c = C(i + self.nT + self.nM + self.nCP)
            self.ids[c.id] = c
            self.Cs.append(c)

    def add_t_nodes(self):
        self.Ts[0].peers_T.append(self.Ts[1])
        self.Ts[1].peers_T.append(self.Ts[0])
        self.Ts[0].degree += 1
        self.Ts[1].degree += 1

    def add_m_nodes(self):
        for m in self.Ms:
            for pt in self.Ts:
                m.providers_T.append(pt)
                m.degree += 1
                pt.customers_M.append(m)
                pt.degree += 1

    def add_cp_nodes(self):
        # cp  0 1 2 m 0 1 t 0
        # 手动
        self.CPs[0].providers_M.append(self.Ms[0])
        self.CPs[0].providers_T.append(self.Ts[0])
        self.Ms[0].customers_CP.append(self.CPs[0])
        self.Ts[0].customers_CP.append(self.CPs[0])

        self.CPs[1].providers_M.append(self.Ms[0])
        self.CPs[1].providers_M.append(self.Ms[1])
        self.Ms[0].customers_CP.append(self.CPs[1])
        self.Ms[1].customers_CP.append(self.CPs[1])

        self.CPs[2].providers_M.append(self.Ms[1])
        self.CPs[2].providers_T.append(self.Ts[1])
        self.Ms[1].customers_CP.append(self.CPs[2])
        self.Ts[1].customers_CP.append(self.CPs[2])

        # change
        self.CPs[3].providers_M.append(self.Ms[2])
        self.CPs[3].providers_T.append(self.Ts[0])
        self.Ms[2].customers_CP.append(self.CPs[3])
        self.Ts[0].customers_CP.append(self.CPs[3])

        self.CPs[4].providers_M.append(self.Ms[2])
        self.CPs[4].providers_M.append(self.Ms[3])
        self.Ms[2].customers_CP.append(self.CPs[4])
        self.Ms[3].customers_CP.append(self.CPs[4])

        self.CPs[5].providers_M.append(self.Ms[3])
        self.CPs[5].providers_T.append(self.Ts[1])
        self.Ms[3].customers_CP.append(self.CPs[5])
        self.Ts[1].customers_CP.append(self.CPs[5])

    def advertise_m_to_provider(self, m):
        # used for recursion. advertise learned from customer to provider(T, M), M recursion
        for m_provider in m.providers_T:
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path[:]
                    path_new.insert(0, m_provider)
                    if path_new not in m_provider.table[destination]:
                        m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            if path_self not in m_provider.table[m.id]:
                m_provider.table[m.id].append(path_self)

        # Not in this loop if M's provider is only T
        for m_provider in m.providers_M:
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path[:]
                    path_new.insert(0, m_provider)
                    if path_new not in m_provider.table[destination]:
                        m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            if path_self not in m_provider.table[m.id]:
                m_provider.table[m.id].append(path_self)
            self.advertise_m_to_provider(m_provider)

    def advertise_cp_to_provider(self):
        # from low to high. advertise learned from customer to provider(T, M), M recursion
        for cp in self.CPs:
            # destination: cp.id
            # advertise itself
            path = []
            path.insert(0, cp)
            cp.table[cp.id].append(path)
            # advertise to its T provider
            for cp_provider in cp.providers_T:
                path_new = path[:]
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)

            for cp_provider in cp.providers_M:
                path_new = path[:]
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)
                # continue to advertise this M to provider
                self.advertise_m_to_provider(cp_provider)

    """
        considering BGP advertisement to peers
        considering that prefer customer to peer to provider,
        put this preference into the function
    """

    def advertise_t_to_peers(self):
        # advertise learned from customer to peers
        for t in self.Ts:
            for t_peer in t.peers_T:
                for destination in t.table:
                    if t_peer.table.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_peer)
                        t_peer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_peer)
                t_peer.table_peer[t.id].append(path_self)

    def advertise_m_to_peers(self):
        # advertise learned from customer to peers, to m, to cp
        for m in self.Ms:
            for m_Mpeer in m.peers_M:
                for destination in m.table:
                    if m_Mpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, m_Mpeer)
                        m_Mpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, m)
                path_self.insert(0, m_Mpeer)
                m_Mpeer.table_peer[m.id].append(path_self)
            for m_CPpeer in m.peers_CP:
                for destination in m.table:
                    if m_CPpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, m_CPpeer)
                        m_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, m)
                path_self.insert(0, m_CPpeer)
                m_CPpeer.table_peer[m.id].append(path_self)

    def advertise_cp_to_peers(self):
        # TODO, advertise learned from customer to peers, to cp, to m
        for cp in self.CPs:
            for cp_Mpeer in cp.peers_M:
                for destination in cp.table:
                    if cp_Mpeer.table.get(destination) is not None: continue
                    pathes = cp.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, cp_Mpeer)
                        cp_Mpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_Mpeer)
                cp_Mpeer.table_peer[cp.id].append(path_self)
            for cp_CPpeer in cp.peers_CP:
                for destination in cp.table:
                    if cp_CPpeer.table.get(destination) is not None: continue
                    pathes = cp.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, cp_CPpeer)
                        cp_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_CPpeer)
                cp_CPpeer.table_peer[cp.id].append(path_self)

    """
        considering BGP advertisement to customer
    """

    def advertise_t_to_customers(self):
        # advertise all table(peers, pc) to customers
        for t in self.Ts:
            for t_Ccustomer in t.customers_C:
                for destination in t.table:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table_provider[t.id].append(path_self)

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table_provider[t.id].append(path_self)

            for t_Mcustomer in t.customers_M:
                for destination in t.table:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Mcustomer)
                t_Mcustomer.table_provider[t.id].append(path_self)

    def advertise_m_to_customers(self):
        # advertise all table(peers, pc) to customers
        for t in self.Ms:
            for t_Ccustomer in t.customers_C:
                for destination in t.table:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table_provider[t.id].append(path_self)

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table_provider[t.id].append(path_self)

    # cut table_provider itself
    def advertise_self_to_self(self):
        for i in self.Ts:
            temp = []
            temp.append(i)
            if temp not in i.table[i.id]:
                i.table[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

        for i in self.Ms:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

        for i in self.CPs:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

        for i in self.Cs:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

    def build_topology(self):
        self.add_t_nodes()
        self.add_m_nodes()
        self.add_cp_nodes()
        print("nodes added")
        self.advertise_cp_to_provider()
        print("advertise cp to provider")
        # advertise for M that has no customer
        for m in self.Ms:
            if len(m.customers_C) == 0:
                self.advertise_m_to_provider(m)
        print("advertise m to provider")
        self.advertise_t_to_peers()
        print("advertise t to peer")
        self.advertise_t_to_customers()
        print("advertise t to customer")
        self.advertise_m_to_customers()
        print("advertise m to customer")
        self.advertise_self_to_self()
        print("advertise self to self")
        print("advertisement finished")
        self.build_matrix()
        print("directed matrix built")

        for i in self.Ts:
            i.init_action_label_next(self.matrix)
            i.init_filter()
            print(i.action_labels)
            print(i.filter)
        print("============")
        for i in self.Ms:
            i.init_action_label_next(self.matrix)
            i.init_filter()
            print(i.action_labels)
            print(i.filter)
        print("============")
        for i in self.CPs:
            i.init_action_label_next(self.matrix)
            i.init_filter()
            print(i.action_labels)
            print(i.filter)
        print("============")

    def build_matrix(self):
        for t in self.Ts:
            for c_m in t.customers_M:
                self.matrix[t.id][c_m.id] = 1
                self.matrix[c_m.id][t.id] = 1
            for c_cp in t.customers_CP:
                self.matrix[t.id][c_cp.id] = 1
                self.matrix[c_cp.id][t.id] = 1
            for c_c in t.customers_C:
                self.matrix[t.id][c_c.id] = 1
                self.matrix[c_c.id][t.id] = 1
            for p_t in t.peers_T:
                self.matrix[t.id][p_t.id] = 1
                self.matrix[p_t.id][t.id] = 1

        for m in self.Ms:
            for c_m in m.customers_M:
                self.matrix[m.id][c_m.id] = 1
                self.matrix[c_m.id][m.id] = 1
            for c_cp in m.customers_CP:
                self.matrix[m.id][c_cp.id] = 1
                self.matrix[c_cp.id][m.id] = 1
            for c_c in m.customers_C:
                self.matrix[m.id][c_c.id] = 1
                self.matrix[c_c.id][m.id] = 1
            for p_m in m.peers_M:
                self.matrix[m.id][p_m.id] = 1
                self.matrix[p_m.id][m.id] = 1
            for p_cp in m.peers_CP:
                self.matrix[m.id][p_cp.id] = 1
                self.matrix[p_cp.id][m.id] = 1

        for cp in self.CPs:
            for p_cp in cp.peers_CP:
                self.matrix[cp.id][p_cp.id] = 1
                self.matrix[p_cp.id][cp.id] = 1

    def build_directed_matrix(self):
        self.matrix[6][0] = 1
        self.matrix[6][2] = 1
        self.matrix[7][2] = 1
        self.matrix[7][3] = 1
        self.matrix[8][3] = 1
        self.matrix[8][1] = 1
        self.matrix[2][0] = 1
        self.matrix[2][1] = 1
        self.matrix[3][0] = 1
        self.matrix[3][1] = 1
        self.matrix[0][1] = 1
        self.matrix[1][0] = 1
        self.matrix[0][4] = 1
        self.matrix[0][9] = 1
        self.matrix[0][5] = 1
        self.matrix[1][4] = 1
        self.matrix[1][5] = 1
        self.matrix[1][11] = 1
        self.matrix[4][9] = 1
        self.matrix[4][10] = 1
        self.matrix[5][10] = 1
        self.matrix[5][11] = 1


"""
    Used for a defined topology 27 nodes, 51 edges, 24 TF
"""


class MidGenerator:
    def __init__(self, n, nT):
        self.n = n
        self.nT = nT
        self.nM = 6
        self.nCP = 23
        self.nC = 0
        self.matrix = np.zeros([self.n + self.nT, self.n + self.nT])

        self.Ts = []
        self.Ms = []
        self.CPs = []
        self.Cs = []
        # id: actual node
        self.ids = {}

        # label id from 0 ~ nT-1
        for i in range(self.nT):
            t = T(i)
            self.ids[t.id] = t
            self.Ts.append(t)

        # label id from nT ~ nT+nM-1
        for i in range(self.nM):
            m = M(i + self.nT)
            self.ids[m.id] = m
            self.Ms.append(m)

        # label id from nT+nM ~ nT+nM+nCP-1
        for i in range(self.nCP):
            cp = CP(i + self.nT + self.nM)
            self.ids[cp.id] = cp
            self.CPs.append(cp)

        # label id from nT+nM+nCP ~ nT+nM+nCP+nC-1
        for i in range(self.nC):
            c = C(i + self.nT + self.nM + self.nCP)
            self.ids[c.id] = c
            self.Cs.append(c)

    def add_t_nodes(self):
        print("add Tier 0")

    def add_m_nodes(self):
        # add m providers
        self.connect_m_t(1, 0)
        self.connect_m_t(2, 0)
        self.connect_m_t(3, 0)
        self.connect_m_t(4, 0)
        self.connect_m_t(5, 0)
        self.connect_m_t(6, 0)

        # add m_peers
        self.connect_mm_peer(1, 2)
        self.connect_mm_peer(4, 5)

    def add_cp_nodes(self):
        self.connect_cp_m(7, 6)
        self.connect_cp_m(7, 1)
        self.connect_cp_m(8, 1)
        self.connect_cp_m(9, 1)
        self.connect_cp_m(10, 1)
        self.connect_cp_m(10, 2)
        self.connect_cp_m(11, 1)
        self.connect_cp_m(11, 2)
        self.connect_cp_m(12, 2)
        self.connect_cp_m(13, 2)
        self.connect_cp_m(14, 2)
        self.connect_cp_m(14, 3)
        self.connect_cp_m(15, 2)
        self.connect_cp_m(15, 3)
        self.connect_cp_m(16, 3)
        self.connect_cp_m(17, 3)
        self.connect_cp_m(18, 3)
        self.connect_cp_m(18, 4)
        self.connect_cp_m(19, 3)
        self.connect_cp_m(19, 4)
        self.connect_cp_m(20, 4)
        self.connect_cp_m(21, 4)
        self.connect_cp_m(22, 4)
        self.connect_cp_m(22, 5)
        self.connect_cp_m(23, 4)
        self.connect_cp_m(23, 5)
        self.connect_cp_m(24, 5)
        self.connect_cp_m(25, 5)
        self.connect_cp_m(26, 5)
        self.connect_cp_m(26, 6)
        self.connect_cp_m(27, 6)
        self.connect_cp_m(27, 5)
        self.connect_cp_m(28, 6)
        self.connect_cp_m(29, 6)
        self.connect_cp_m(29, 1)

    def advertise_m_to_provider(self, m):
        # used for recursion. advertise learned from customer to provider(T, M), M recursion
        for m_provider in m.providers_T:
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path[:]
                    path_new.insert(0, m_provider)
                    if path_new not in m_provider.table[destination]:
                        m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            if path_self not in m_provider.table[m.id]:
                m_provider.table[m.id].append(path_self)

        # Not in this loop if M's provider is only T
        for m_provider in m.providers_M:
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path[:]
                    path_new.insert(0, m_provider)
                    if path_new not in m_provider.table[destination]:
                        m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            if path_self not in m_provider.table[m.id]:
                m_provider.table[m.id].append(path_self)
            self.advertise_m_to_provider(m_provider)

    def advertise_cp_to_provider(self):
        # from low to high. advertise learned from customer to provider(T, M), M recursion
        for cp in self.CPs:
            # destination: cp.id
            # advertise itself
            path = []
            path.insert(0, cp)
            cp.table[cp.id].append(path)
            # advertise to its T provider
            for cp_provider in cp.providers_T:
                path_new = path[:]
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)

            for cp_provider in cp.providers_M:
                path_new = path[:]
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)
                # continue to advertise this M to provider
                self.advertise_m_to_provider(cp_provider)

    def advertise_t_to_peers(self):
        # advertise learned from customer to peers
        for t in self.Ts:
            for t_peer in t.peers_T:
                for destination in t.table:
                    if t_peer.table.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_peer)
                        t_peer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_peer)
                t_peer.table_peer[t.id].append(path_self)

    def advertise_m_to_peers(self):
        # advertise learned from customer to peers, to m, to cp
        for m in self.Ms:
            for m_Mpeer in m.peers_M:
                for destination in m.table:
                    if m_Mpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, m_Mpeer)
                        m_Mpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, m)
                path_self.insert(0, m_Mpeer)
                m_Mpeer.table_peer[m.id].append(path_self)
            for m_CPpeer in m.peers_CP:
                for destination in m.table:
                    if m_CPpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, m_CPpeer)
                        m_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, m)
                path_self.insert(0, m_CPpeer)
                m_CPpeer.table_peer[m.id].append(path_self)

    def advertise_cp_to_peers(self):
        # TODO, advertise learned from customer to peers, to cp, to m
        for cp in self.CPs:
            for cp_Mpeer in cp.peers_M:
                for destination in cp.table:
                    if cp_Mpeer.table.get(destination) is not None: continue
                    pathes = cp.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, cp_Mpeer)
                        cp_Mpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_Mpeer)
                cp_Mpeer.table_peer[cp.id].append(path_self)
            for cp_CPpeer in cp.peers_CP:
                for destination in cp.table:
                    if cp_CPpeer.table.get(destination) is not None: continue
                    pathes = cp.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, cp_CPpeer)
                        cp_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_CPpeer)
                cp_CPpeer.table_peer[cp.id].append(path_self)

    """
        considering BGP advertisement to customer
    """

    def advertise_t_to_customers(self):
        # advertise all table(peers, pc) to customers
        for t in self.Ts:
            for t_Ccustomer in t.customers_C:
                for destination in t.table:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table_provider[t.id].append(path_self)

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table_provider[t.id].append(path_self)

            for t_Mcustomer in t.customers_M:
                for destination in t.table:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Mcustomer)
                t_Mcustomer.table_provider[t.id].append(path_self)

    def advertise_m_to_customers(self):
        # advertise all table(peers, pc) to customers
        for t in self.Ms:
            for t_Ccustomer in t.customers_C:
                for destination in t.table:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table_provider[t.id].append(path_self)

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                for destination in t.table_provider:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_provider[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path[:]
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table_provider[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table_provider[t.id].append(path_self)

    # cut table_provider itself
    def advertise_self_to_self(self):
        for i in self.Ts:
            temp = []
            temp.append(i)
            if temp not in i.table[i.id]:
                i.table[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

        for i in self.Ms:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

        for i in self.CPs:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

        for i in self.Cs:
            if i.table.get(i.id) is not None:
                temp = []
                temp.append(i)
                if temp not in i.table[i.id]:
                    i.table[i.id].append(temp)
            else:
                temp = []
                temp.append(i)
                if temp not in i.table_peer[i.id]:
                    i.table_peer[i.id].append(temp)
            if i.table_provider[i.id] is not None:
                i.table_provider.pop(i.id)

    def connect_m_t(self, mid, tid):
        self.ids[mid].providers_T.append(self.ids[tid])
        self.ids[tid].customers_M.append(self.ids[mid])

    def connect_cp_t(self, cid, tid):
        self.ids[cid].providers_T.append(self.ids[tid])
        self.ids[tid].customers_CP.append(self.ids[cid])

    def connect_cp_m(self, cid, mid):
        self.ids[cid].providers_M.append(self.ids[mid])
        self.ids[mid].customers_CP.append(self.ids[cid])

    def connect_mm_provider(self, midc, midp):
        self.ids[midc].providers_M.append(self.ids[midp])
        self.ids[midp].customers_M.append(self.ids[midc])

    def connect_mm_peer(self, mid1, mid2):
        self.ids[mid1].peers_M.append(self.ids[mid2])
        self.ids[mid2].peers_M.append(self.ids[mid1])

    def build_matrix(self):
        for t in self.Ts:
            for c_m in t.customers_M:
                self.matrix[t.id][c_m.id] = 1
                self.matrix[c_m.id][t.id] = 1
            for c_cp in t.customers_CP:
                self.matrix[t.id][c_cp.id] = 1
                self.matrix[c_cp.id][t.id] = 1
            for c_c in t.customers_C:
                self.matrix[t.id][c_c.id] = 1
                self.matrix[c_c.id][t.id] = 1
            for p_t in t.peers_T:
                self.matrix[t.id][p_t.id] = 1
                self.matrix[p_t.id][t.id] = 1

        for m in self.Ms:
            for c_m in m.customers_M:
                self.matrix[m.id][c_m.id] = 1
                self.matrix[c_m.id][m.id] = 1
            for c_cp in m.customers_CP:
                self.matrix[m.id][c_cp.id] = 1
                self.matrix[c_cp.id][m.id] = 1
            for c_c in m.customers_C:
                self.matrix[m.id][c_c.id] = 1
                self.matrix[c_c.id][m.id] = 1
            for p_m in m.peers_M:
                self.matrix[m.id][p_m.id] = 1
                self.matrix[p_m.id][m.id] = 1
            for p_cp in m.peers_CP:
                self.matrix[m.id][p_cp.id] = 1
                self.matrix[p_cp.id][m.id] = 1

        for cp in self.CPs:
            for p_cp in cp.peers_CP:
                self.matrix[cp.id][p_cp.id] = 1
                self.matrix[p_cp.id][cp.id] = 1

    def build_topology(self):
        self.add_t_nodes()
        self.add_m_nodes()
        self.add_cp_nodes()
        print("nodes added")
        self.advertise_cp_to_provider()
        print("advertise cp to provider")
        # advertise for M that has no customer
        for m in self.Ms:
            if len(m.customers_C) == 0:
                self.advertise_m_to_provider(m)
        print("advertise m to provider")
        self.advertise_t_to_peers()
        print("advertise t to peer")
        self.advertise_t_to_customers()
        print("advertise t to customer")
        self.advertise_m_to_customers()
        print("advertise m to customer")
        self.advertise_self_to_self()
        print("advertise self to self")
        print("advertisement finished")

        self.build_matrix()
        for i in self.Ts:
            i.init_action_label_next(self.matrix)
            i.init_filter()
        print("============")
        for i in self.Ms:
            i.init_action_label_next(self.matrix)
            i.init_filter()
        print("============")
        for i in self.CPs:
            i.init_action_label_next(self.matrix)
            i.init_filter()
        print("============")

# game = MiniGenerator(10, 2)
# game.build_topology()
