import os
import input
import random

def getDemand(elem):
    return elem[1]


root_path = "/"
# root_path = "/home/melodies/HWcom/SDK/SDK_python/"
data_path = root_path + "data/"
output_path = root_path + "output/"

if __name__ == '__main__':
    '''
    N: number of sites
    M: number of clients
    QoS: configuration for connectivity
    site_bandwidth: [name:band_capacity for name in site_names]
    demands: [[name:demand_t for name in client_names] for t in times (index)]
    graph: bilateral connectivity between sites and clients 
    used: [[band_used_t for t in times] indexed by server name]
    '''
    N, site_bandwidth = input.getSiteInfo(data_path)
    M, demands = input.getClientInfo(data_path)
    QoS = input.getConfig(data_path)
    site_client, client_site = input.buildGraph(data_path, list(demands[0].keys()), QoS)
    site_names = site_bandwidth.keys()
    client_names = demands[0].keys()
    times = len(demands)

    used = dict()  # site:time(index):total_usage, for sake of calculating COST
    for site in site_names:
        used[site] = [0 for t in range(times)]
    assigns = []  # time(index):client:site:band_assigned, for solution

    for time, demand in enumerate(demands):
        # demand form:: client:demand
        cur_client_demand = list(demand.items())  # each element: (client, band demand)
        # cur_client_demand.sort(key=getDemand, reverse=True)  # sort by band
        solved = False
        while not solved:
            random.shuffle(cur_client_demand)
            capacity = site_bandwidth.copy()  # remained capacity for current time
            cur_assign = dict()
            valid = True
            for client, band in cur_client_demand:
                client_assign = cur_assign[client] = dict()
                if band == 0:  # zero requirement
                    continue
                available_sites = client_site[client]
                total_cnt = len(available_sites)  # available sites for current client
                cur_use = dict()
                for site in site_names:
                    cur_use[site] = 0
                while total_cnt > 0 and band > 0:
                    cnt = total_cnt
                    for site in available_sites:
                        avg = max(band // cnt, 1)  # rolling average
                        cur = min(band // cnt, capacity[site])  # real assign
                        if cur == 0:  # this site cannot provide bandwidth
                            total_cnt -= 1
                            cnt -= 1
                            continue
                        capacity[site] -= cur
                        cur_use[site] += cur
                        band -= cur

                        if not client_assign.__contains__(site):
                            client_assign[site] = cur
                        else:
                            client_assign[site] += cur
                        cnt -= 1
                        if cnt == 0:
                            break
                    if total_cnt == 0 and band != 0:
                        valid = False
            if valid:
                assigns.append(cur_assign)
                for site, use in cur_use.items():
                    used[site][time] = use
                solved = True

    total_cost = 0
    pos = int(len(demands) * 0.95)
    for site, usage in used.items():
        usage.sort()
        total_cost += usage[pos]

    output = []
    for assign in assigns:
        for client, client_assign in assign.items():
            cur = client + ":"
            for site, band in client_assign.items():
                cur += "<{},{}>,".format(site, band)
            if cur[-1] == ",":
                cur = cur[:-1]
            output.append(cur)

    with open(os.path.abspath(output_path + "solution.txt"), 'w') as f:
        for row in output:
            f.write(row + "\n")
