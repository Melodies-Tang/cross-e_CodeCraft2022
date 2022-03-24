import numpy as np
import os
from typing import Tuple, List


cname, sname, qos, qos_lim = None, None, None, None
client_demand = None
bandwidth = None
time_label = None
cname_map = {}
sname_map = {}


class IOFile():
    suffix = '_ori'
    demand = f'data{suffix}/demand.csv'
    qos = f'data{suffix}/qos.csv'
    bandwidth = f'data{suffix}/site_bandwidth.csv'
    config = f'data{suffix}/config.ini'
    output = 'output/solution.txt'


def read_demand() -> Tuple[List[str], List[int]]:
    fname = IOFile.demand
    with open(fname) as f:
        data = f.read().splitlines()
    client_name = data[0].split(',')[1:]
    client_demand = []
    time_label = []
    for each in data[1:]:
        d = each.split(',')
        time_label.append(d[0])
        client_demand.append(list(map(int, d[1:])))
    return time_label, client_name, client_demand


def read_server_bandwidth() -> Tuple[List[str], List[int]]:
    fname = IOFile.bandwidth
    with open(fname) as f:
        data = f.read().splitlines()
    server_name = []
    server_bandwidth = []
    for each in data[1:]:
        a, b = each.split(',')
        server_name.append(a)
        server_bandwidth.append(int(b))
    return server_name, server_bandwidth


def read_qos() -> Tuple[List[str], List[str], List[List[int]]]:
    fname = IOFile.qos
    with open(fname) as f:
        data = f.read().splitlines()
    client_name = data[0].split(',')[1:]
    server_name = []
    qos_array = []
    for each in data[1:]:
        d = each.split(',')
        server_name.append(d[0])
        qos_array.append(list(map(int, d[1:])))
    return client_name, server_name, qos_array


def read_qos_limit() -> int:
    fname = IOFile.config
    with open(fname) as f:
        data = f.read().splitlines()
    qos_lim = int(data[1].split('=')[1])
    return qos_lim


def get_input_data():
    global cname, sname, qos, qos_lim, bandwidth, client_demand, time_label, cname_map, sname_map
    cname, sname, qos = read_qos()
    for idx, name in enumerate(cname):
        cname_map[name] = idx
    for idx, name in enumerate(sname):
        sname_map[name] = idx
    qos = np.array(qos)
    time_label, client_name, client_demand = read_demand()
    client_idx_list = []
    for c in cname:
        idx = client_name.index(c)
        client_idx_list.append(idx)
    client_demand = np.array(client_demand)[:, client_idx_list]
    server_name, server_bandwidth = read_server_bandwidth()
    bandwidth = []
    for s in sname:
        idx = server_name.index(s)
        bandwidth.append(server_bandwidth[idx])
    qos_lim = read_qos_limit()
    bandwidth = np.array(bandwidth)

def get_available_sites():
    global qos, qos_lim
    available_sites = {}
    for c in cname:
        ci = cname_map[c]
        available_sites[c] = []
        for s in sname:
            si = sname_map[s]
            if qos[si][ci] < qos_lim:
                available_sites[c].append(s)
    return available_sites


class Resolver():
    def __init__(self, client_demand, bandwidth) -> None:
        global time_label, sname, cname
        self.T = len(time_label)
        self.M = len(cname)
        self.N = len(sname)
        self.client_demand = client_demand
        self.bandwidth_at_time = [ list(bandwidth) for t in range(self.T) ]
        self.available_sites = get_available_sites()
        self.skew_max_limit = max(self.T // 20 - 1, self.T // self.N)
        self.skew_limit = min(self.T // 20 - 1, self.T // self.N)
        self.skew_record = {} # sname - [time_1, ...]
        for s in sname:
            self.skew_record[s] = []
        
        self.record = np.zeros((self.T, self.M, self.N), dtype=np.int32)

    def assgin(self, time, cname, sname, bandwidth):
        global cname_map, sname_map
        ci, si = cname_map[cname], sname_map[sname]
        self.client_demand[time][ci] -= bandwidth
        self.bandwidth_at_time[time][si] -= bandwidth
        self.record[time][ci][si] += bandwidth

    def unassign(self, time, cname, sname, bandwidth):
        global cname_map, sname_map
        ci, si = cname_map[cname], sname_map[sname]
        self.client_demand[time][ci] += bandwidth
        self.bandwidth_at_time[time][si] += bandwidth
        self.record[time][ci][si] -= bandwidth

    def do_skew(self, time, cname, sname) -> int:
        global cname_map, sname_map
        ci, si = cname_map[cname], sname_map[sname]
        if time not in self.skew_record[sname]:
            self.skew_record[sname].append(time)
        bandwidth = min(self.bandwidth_at_time[time][si], rs.client_demand[time][ci])
        remained_bandwidth = self.bandwidth_at_time[time][si] - bandwidth
        self.assgin(time, cname, sname, bandwidth)
        return remained_bandwidth

    def undo_skew(self, time, cname, sname):
        pass
        # i = 0
        # for record in skew_record[sname]:
        #     if record[1] == cname:
        #         break
        #     i += 1
        # self.skew_record[sname] = self.skew_record[sname][:i] + self.skew_record[sname][i+1:]
        # self.unassgin(time, cname, sname, bandwidth)

    def can_skew(self, time, cname, sname):
        global cname_map, sname_map
        ci, si = cname_map[cname], sname_map[sname]
        if time not in self.skew_record[sname] and len(self.skew_record[sname]) == self.skew_limit:
            return False
        remained_bandwidth = self.bandwidth_at_time[time][si]
        if remained_bandwidth > 0 and rs.client_demand[time][ci] > 0:
            return True
        return False

    def can_skew_max(self, time, cname, sname):
        global cname_map, sname_map
        ci, si = cname_map[cname], sname_map[sname]
        if time not in self.skew_record[sname] and len(self.skew_record[sname]) == self.skew_max_limit:
            return False
        remained_bandwidth = self.bandwidth_at_time[time][si]
        if remained_bandwidth > 0 and rs.client_demand[time][ci] > 0:
            return True
        return False

    def output(self):
        global cname, sname
        content = ''
        for t in range(self.T):     
            for ci in range(self.M):
                content += f'{cname[ci]}:'
                groups = []
                for si in range(self.N):
                    if self.record[t][ci][si] > 0:
                        groups.append((sname[si], self.record[t][ci][si]))
                for i in range(len(groups)):
                    content += f'<{groups[i][0]},{groups[i][1]}>'
                    if i < len(groups) - 1:
                        content +=  ','
                content += '\r\n'
        fname = IOFile.output
        if not os.path.exists('output'):
            os.mkdir('output')
        with open(fname, mode='w') as f:
            f.write(content)
             

def make_skew_plan(rs):
    global cname, sname
    skew_size = max(1, rs.N // (rs.T // rs.skew_limit))
    skew_by_time = {}
    for t in range(rs.T):
        skew_by_time[t] = []
        skew_site = set()
        ci = 0
        while ci < rs.M:
            for s in rs.available_sites[cname[ci]]:
                if len(skew_site) < skew_size and rs.can_skew(t, cname[ci], s):
                    remained_bandwidth = rs.do_skew(t, cname[ci], s)
                    # print(ci, s, remained_bandwidth)
                    cii = ci
                    while cii + 1 < rs.M and remained_bandwidth > 0:
                        cii += 1
                        if s in rs.available_sites[cname[cii]] and rs.can_skew(t, cname[cii], s):
                            remained_bandwidth = rs.do_skew(t, cname[cii], s)
                            # print(cii, s, remained_bandwidth)
                    skew_site.add(s)
            ci += 1
        skew_by_time[t] = skew_site
    print(rs.skew_record)
    for t in range(rs.T):
        # print(t)
        if len(skew_by_time[t]) == 0:
            skew_site = set()
            ci = 0
            while ci < rs.M:
                for s in rs.available_sites[cname[ci]]:
                    if len(skew_site) < skew_size and rs.can_skew_max(t, cname[ci], s):
                        remained_bandwidth = rs.do_skew(t, cname[ci], s)
                        # print(ci, s, remained_bandwidth)
                        cii = ci
                        while cii + 1 < rs.M and remained_bandwidth > 0:
                            cii += 1
                            if s in rs.available_sites[cname[cii]] and rs.can_skew_max(t, cname[cii], s):
                                remained_bandwidth = rs.do_skew(t, cname[cii], s)
                                # print(cii, s, remained_bandwidth)
                        skew_site.add(s)
                ci += 1
    print(rs.skew_record)


def make_average_plan(rs):
    global cname_map, sname_map
    for t in range(rs.T):
        # print(t)
        for c in cname:
            # print(c)
            available_sites = []
            bandwidths = []
            for s in rs.available_sites[c]:
                if rs.can_skew_max(t, c, s):
                    rs.do_skew(t, c, s)
                elif rs.bandwidth_at_time[t][sname_map[s]] > 0:  
                    available_sites.append(s)
                    bandwidths.append(rs.bandwidth_at_time[t][sname_map[s]])
            ci = cname_map[c]
            demand = rs.client_demand[t][ci]
            total_bandwidth = np.sum(bandwidths)
            bandwidths_to_assign = list(map(lambda b: int(demand * b / total_bandwidth), bandwidths))
            bandwidths_to_assign[-1] = demand - np.sum(bandwidths_to_assign[:-1])
            # print(demand, bandwidths_to_assign, np.sum(bandwidths_to_assign))
            for i in range(len(available_sites)):
                rs.assgin(t, c, available_sites[i], bandwidths_to_assign[i])
            

if __name__ == '__main__':
    get_input_data()
    rs = Resolver(client_demand, bandwidth)
    make_skew_plan(rs)
    make_average_plan(rs)
    # for t in range(rs.T):
        # for ci in range(rs.M):
            # print(rs.record[t][ci][0])
    rs.output()




# def assignOneClient(band, sites, site_capacity):  # fulfill band demand of cur client and return feasibility
#     client_assign = dict()
#     while len(sites) > 0 and band > 0:  # assign band to sites
#         for idx, site in enumerate(sites):
#             avg = max(1, band // (len(sites) - idx))
#             cur = min(avg, site_capacity[site])  # real assign
#             if cur == 0:
#                 continue
#             site_capacity[site] -= cur
#             site_band_used[site] = site_band_used.get(site, 0) + cur
#             client_assign[site] = client_assign.get(site, 0) + cur
#             band -= cur

#             if band == 0:  # checked if demand satisfied
#                 break

#         sites = [site for site in sites if site_capacity[site] > 0]  # delete sites with no capacity
#         if len(sites) == 0 and band > 0:  # no solution, return for shuffle and solve again (for all clients)
#             return False, dict()
#     return True, client_assign


# def solveDispatch(site_capacity):
#     # initialize record for solution of this time
#     """
#     site_capacity: remained capacity of current time slot
#     site_band_used: band usage of each site
#     client_site_band: assignment result of each client
#     client_assign: result of single client
#     """
#     for client, band in client_demand_current:  # handle single client
#         if band == 0:  # zero requirement
#             client_site_band[client] = dict()
#             continue

#         available_sites = list(client_site[client])
#         random.shuffle(available_sites)
#         valid, client_assign = assignOneClient(band, available_sites, site_capacity)
#         if not valid:
#             return False, dict(), dict()
#         else:
#             client_site_band[client] = client_assign
#     return True


# if __name__ == '__main__':
#     """
#     N: number of sites
#     M: number of clients
#     QoS: configuration for connectivity
#     site_bandwidth: [name:band_capacity for name in site_names]
#     demands: [[name:demand_t for name in client_names] for t in times (index)]
#     graph: bilateral connectivity between sites and clients 
#     used: [[band_used_t for t in times] indexed by server name]
#     """
#     N, site_bandwidth = IO.getSiteInfo(data_path)
#     M, demands, time_names = IO.getClientInfo(data_path)
#     QoS = IO.getConfig(data_path)
#     site_client, client_site = IO.buildGraph(data_path, list(demands[0].keys()), QoS)
#     site_names = site_bandwidth.keys()
#     client_names = demands[0].keys()
#     times = len(demands)

#     POS_95 = int(times * 0.95)  # index start by 0
#     special_num = times - POS_95 - 2  # TRY

#     used = dict()  # site:time(index):total_usage, for sake of calculating COST
#     for site in site_names:
#         used[site] = [0 for t in range(times)]
#     # assigns = []  # [time]client:site:band_assigned, for solution
#     #
#     # # solve demands for all times
#     # for time, demand in enumerate(demands):
#     #     # demand form:: client:demand
#     #     client_demand_current = list(demand.items())  # each element: (client, band demand)
#     #     client_demand_current.sort(key=getDemand, reverse=True)  # handle client with higher demand first
#     #     solved = False  # mark the solution for current time
#     #     while not solved:  # solve the assignment for ONE TIME
#     #         client_site_band = dict()
#     #         site_band_used = dict()
#     #         solved = solveDispatch(site_bandwidth.copy())
#     #         if solved:  # copy to final solution
#     #             assigns.append(client_site_band)
#     #             for site, use in site_band_used.items():
#     #                 used[site][time] = use
#     #         else:
#     #             random.shuffle(client_demand_current)

#     total_cost = 0
#     for site, usage in used.items():
#         cur = sorted(usage)
#         total_cost += usage[POS_95]

#     empty = {}.fromkeys(client_names, dict())
#     assigns = [empty.copy() for t in range(times)]
#     # assigns = [[time_names[i], assigns[i]] for i in range(times)]
#     # assigns.sort(key=sortByTime)
#     # assigns = [assigns[i][1] for i in range(times)]
#     site_chances = [special_num for i in range(N)]
#     solution = [assigns, total_cost, used, POS_95, site_chances]
#     new_solution = [assigns, total_cost, used, POS_95, site_chances]  # HOW TO DEEPCOPY???
#     new_cost = KM.evaluate(new_solution, demands, site_bandwidth, site_client, client_site)

#     IO.writeOutput(output_path, new_solution[0])
