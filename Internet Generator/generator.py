import numpy as np
import operator
import random
from nodes import T
from nodes import M
from nodes import CP
from nodes import C
import collections

'''
    here may consider the 'region', net *only* in one region are not allowed to connect net in other regions
'''


class Generator:
    # init with n number and number of T
    def __init__(self, n, nT):
        self.n = n
        self.nT = nT
        self.nM = int(0.15 * self.n)
        self.nCP = int(0.05 * self.n)
        self.nC = int(0.80 * self.n)
        # other pars for d, p, t
        self.dM = 2 + 2.5 * n / 10000
        self.dCP = 2 + 1.5 * n / 10000
        self.dC = 1 + 5 * n / 100000
        self.pM = 1 + 2 * n / 10000
        self.pCP_M = 0.2 + 2 * n / 10000
        self.pCP_CP = 0.05 + 5 * n / 100000
        self.tM = 1  # 0.375
        self.tCP = 0.375
        self.tC = 0.125

        # collections for nodes
        self.Ts = []
        self.Ms = []
        self.CPs = []
        self.Cs = []

        # create object for nodes, init parameters with ids
        # label id from 0 ~ nT-1
        for i in range(self.nT):
            t = T(i)
            self.Ts.append(t)

        # label id from nT ~ nT+nM-1
        for i in range(self.nM):
            m = M(i + self.nT)
            self.Ms.append(m)

        # label id from nT+nM ~ nT+nM+nCP-1
        for i in range(self.nCP):
            cp = CP(i + self.nT + self.nM)
            self.CPs.append(cp)

        # label id from nT+nM+nCP ~ nT+nM+nCP+nC-1
        for i in range(self.nC):
            c = C(i + self.nT + self.nM + self.nCP)
            self.Cs.append(c)

    @staticmethod
    def same_region(list1, list2):
        for a in list1:
            for b in list2:
                if a == b:
                    return True
        return False

    def check_loop(self, m, mp):
        if mp in m.customers_M:
            return False
        else:
            for t in m.customers_M:
                if self.check_loop(t, mp) is False:
                    return False
            return True

    # create clique for T nodes, complete graph
    # here add peer, need to check if double build
    def add_t_nodes(self):
        for t in self.Ts:
            for t_p in self.Ts:
                if t_p == t: continue
                if t_p in t.peers_T: continue
                t.peers_T.append(t_p)
                t_p.peers_T.append(t)
                t.degree += 1
                t_p.degree += 1

    # add M nodes one by one, with provider determined
    # M can only select provider in the same region,
    # TODO, BUG, add index loop
    def add_m_nodes(self):
        for m in self.Ms:
            # determine how many provider, uniform distribution between 0-2dM, average dM
            num_providers = random.randint(1, 2 * int(self.dM))

            # preference those with higher degrees, rank with decreasing
            func = operator.attrgetter('degree')
            self.Ts.sort(key=func, reverse=True)
            self.Ms.sort(key=func, reverse=True)

            # number has been determined, sorted, here degree added has no impact
            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tM:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    while self.same_region(pt.regions, m.regions) is False:
                        it += 1
                        pt = self.Ts[it]
                    m.providers_T.append(pt)
                    m.degree += 1
                    pt.customers_M.append(m)
                    pt.degree += 1
                    it += 1

                else:
                    # provider is M, build relationship
                    # TODO, avoid provider loop
                    pm = self.Ms[im]
                    # avoid itself as provider
                    while pm == m \
                            or self.same_region(pm.regions, m.regions) is False:
                        im += 1
                        pm = self.Ms[im]
                    while self.check_loop(m, pm) is False:
                        print("has loop")
                        im += 1
                        pm = self.Ms[im]

                    m.providers_M.append(pm)
                    m.degree += 1
                    pm.customers_M.append(m)
                    pm.degree += 1
                    im += 1

    # same as M nodes
    def add_cp_nodes(self):
        for cp in self.CPs:
            num_providers = random.randint(1, 2 * int(self.dCP))
            func = operator.attrgetter('degree')
            self.Ts.sort(key=func, reverse=True)
            self.Ms.sort(key=func, reverse=True)

            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tCP:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    # Net only in one region, not connect others
                    if len(cp.regions) == 1:
                        while self.same_region(pt.regions, cp.regions) is False:
                            it += 1
                            pt = self.Ts[it]
                    cp.providers_T.append(pt)
                    cp.degree += 1
                    pt.customers_CP.append(cp)
                    pt.degree += 1
                    it += 1

                else:
                    # provider is M, build relationship
                    pm = self.Ms[im]
                    if len(cp.regions) == 1:
                        while self.same_region(pm.regions, cp.regions) is False:
                            im += 1
                            pm = self.Ms[im]

                    cp.providers_M.append(pm)
                    cp.degree += 1
                    pm.customers_CP.append(cp)
                    pm.degree += 1
                    im += 1

    # same as M nodes
    def add_c_nodes(self):
        for c in self.Cs:
            num_providers = random.randint(1, 2 * int(self.dC))
            func = operator.attrgetter('degree')
            self.Ts.sort(key=func, reverse=True)
            self.Ms.sort(key=func, reverse=True)

            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tC:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    if len(c.regions) == 1:
                        while self.same_region(pt.regions, c.regions) is False:
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
                    if len(c.regions) == 1:
                        while self.same_region(pm.regions, c.regions) is False:
                            im += 1
                            pm = self.Ms[im]
                    c.providers_M.append(pm)
                    c.degree += 1
                    pm.customers_C.append(c)
                    pm.degree += 1
                    im += 1

    # add peering links, PEER_DEGREE & DEGREE
    def add_m_peers(self):
        for m in self.Ms:
            # determine the number of peer links for each M, half it
            # only consider one-direct out peer, but add degree both
            number_peers = random.randint(0, int(1 * self.pM))
            # sort based on peer degree
            func = operator.attrgetter('peer_degree')
            self.Ms.sort(key=func, reverse=True)
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
                if len(m.regions) == 1:
                    while self.same_region(m.regions, pm.regions):
                        im += 1
                        pm = self.Ms[im]

                m.peers_M.append(pm)
                m.peer_degree += 1
                m.degree += 1
                pm.peers_M.append(m)
                pm.peer_degree += 1
                pm.degree += 1
                im += 1

    # select peers in the same region with uniform probability
    def add_cp_peers(self):
        for cp in self.CPs:
            number_peers_m = random.randint(0, int(1 * self.pCP_M))
            number_peers_cp = random.randint(0, int(1 * self.pCP_CP))

            # build relationship
            for i in range(number_peers_m):
                pm = random.choice(self.Ms)
                while pm in cp.providers_M or self.same_region(pm.regions, cp.regions) is False:
                    pm = random.choice(self.Ms)
                cp.peers_M.append(pm)
                pm.peers_CP.append(cp)
                pm.peer_degree += 1
                cp.degree += 1
                pm.degree += 1
            for i in range(number_peers_cp):
                cpp = random.choice(self.CPs)
                while cpp == cp or self.same_region(pm.regions, cp.regions) is False:
                    cpp = random.choice(self.CPs)
                cp.peers_CP.append(cpp)
                cpp.peers_CP.append(cp)
                cp.degree += 1
                cpp.degree += 1

    """
        considering BGP advertisement to providers
    """

    def advertise_c_to_provider(self):
        # c has no peers, no customers, and must be the bottom
        # TODO, from low to high. advertise learned from customer to provider(T, M), M recursion
        for c in self.Cs:
            # destination: c.id
            # advertise itself
            path = []
            path.insert(0, c)
            c.table[c.id].append(path)
            # advertise to its T provider
            for c_provider in c.providers_T:
                path_new = path.copy()
                path_new.insert(0, c_provider)
                c_provider.table[c.id].append(path_new)

            for c_provider in c.providers_M:
                path_new = path.copy()
                path_new.insert(0, c_provider)
                c_provider.table[c.id].append(path_new)
                # continue to advertise this M to provider
                self.advertise_m_to_provider(c_provider)

    def advertise_m_to_provider(self, m):
        # TODO, used for recursion. advertise learned from customer to provider(T, M), M recursion
        for m_provider in m.providers_T:
            # for m'table, add m node, adn advertise to provider
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path.copy()
                    path_new.insert(0, m_provider)
                    m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            m_provider.table[m.id].append(path_self)

        for m_provider in m.providers_M:
            # TODO, when M-M p-c no, not in this loop
            for destination in m.table:
                pathes = m.table[destination]
                for path in pathes:
                    if path is None:
                        path = []
                    path_new = path.copy()
                    path_new.insert(0, m_provider)
                    m_provider.table[destination].append(path_new)
            path_self = []
            path_self.insert(0, m)
            path_self.insert(0, m_provider)
            m_provider.table[m.id].append(path_self)
            self.advertise_m_to_provider(m_provider)

    def advertise_cp_to_provider(self):
        # cp has peers, no customers
        # TODO, from low to high. advertise learned from customer to provider(T, M), M recursion
        for cp in self.CPs:
            # destination: cp.id
            # advertise itself
            path = []
            path.insert(0, cp)
            cp.table[cp.id].append(path)
            # advertise to its T provider
            for cp_provider in cp.providers_T:
                path_new = path.copy()
                path_new.insert(0, cp_provider)
                cp_provider.table[cp.id].append(path_new)

            for cp_provider in cp.providers_M:
                path_new = path.copy()
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
        # TODO, advertise learned from customer to peers
        for t in self.Ts:
            # for each T
            for t_peer in t.peers_T:
                for destination in t.table:
                    if t_peer.table.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_peer)
                        t_peer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_peer)
                t_peer.table_peer[t.id].append(path_self)

    def advertise_m_to_peers(self):
        # TODO, advertise learned from customer to peers, to m, to cp
        for m in self.Ms:
            # for each M
            for m_Mpeer in m.peers_M:
                for destination in m.table:
                    if m_Mpeer.table.get(destination) is not None: continue
                    pathes = m.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
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
                        path_new = path.copy()
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
                        path_new = path.copy()
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
                        path_new = path.copy()
                        path_new.insert(0, cp_CPpeer)
                        cp_CPpeer.table_peer[destination].append(path_new)
                path_self = []
                path_self.insert(0, cp)
                path_self.insert(0, cp_CPpeer)
                cp_CPpeer.table_peer[cp.id].append(path_self)

    # """
    #     considering BGP advertisement to customer
    # """
    #
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
                        path_new = path.copy()
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table[destination].append(path_new)
                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table[t.id].append(path_self)
            print("end C")

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table[t.id].append(path_self)

            print("end CP")

            for t_Mcustomer in t.customers_M:
                for destination in t.table:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Mcustomer.table.get(destination) is not None \
                            or t_Mcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_Mcustomer)
                        t_Mcustomer.table[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Mcustomer)
                t_Mcustomer.table[t.id].append(path_self)

            print("end M")

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
                        path_new = path.copy()
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table[destination].append(path_new)

                for destination in t.table_peer:
                    if t_Ccustomer.table.get(destination) is not None \
                            or t_Ccustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_Ccustomer)
                        t_Ccustomer.table[destination].append(path_new)
                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_Ccustomer)
                t_Ccustomer.table[t.id].append(path_self)
            print("end C")

            for t_CPcustomer in t.customers_CP:
                for destination in t.table:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table[destination].append(path_new)

                for destination in t.table_peer:
                    if t_CPcustomer.table.get(destination) is not None \
                            or t_CPcustomer.table_peer.get(destination) is not None: continue
                    pathes = t.table_peer[destination]
                    for path in pathes:
                        if path is None:
                            path = []
                        path_new = path.copy()
                        path_new.insert(0, t_CPcustomer)
                        t_CPcustomer.table[destination].append(path_new)

                path_self = []
                path_self.insert(0, t)
                path_self.insert(0, t_CPcustomer)
                t_CPcustomer.table[t.id].append(path_self)

            print("end CP")

    def build_topology(self):
        self.add_t_nodes()
        self.add_m_nodes()
        self.add_c_nodes()
        self.add_cp_nodes()
        self.add_m_peers()
        self.add_cp_peers()

        self.advertise_c_to_provider()
        self.advertise_cp_to_provider()
        # advertise for M that has no customer
        for m in self.Ms:
            if len(m.customers_C) == 0:
                self.advertise_m_to_provider(m)
        self.advertise_t_to_peers()
        self.advertise_m_to_peers()
        self.advertise_cp_to_peers()
        self.advertise_t_to_customers()
        self.advertise_m_to_customers()

'''
    TEST CASE
'''

# for m in generator.Cs:
#     for t in m.providers_M:
#         if m.table.get(t.id) is None:
#             print("fuck")

# for c in generator.Cs:
#     print('===========' + str(c.id))
#     for t in c.providers_T:
#         print("T")
#         print(t.table[c.id])
#     for t in c.providers_M:
#         print("M")
#         print(t.table[c.id])


# node = generator.CPs[4]
# print(node.id)
# if len(node.providers_M) > 0:
#     print(node in node.providers_M[0].customers_CP)
# if len(node.providers_T) > 0:
#     print(node in node.providers_T[0].customers_CP)
