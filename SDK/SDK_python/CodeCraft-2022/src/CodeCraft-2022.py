import IO
import random


# import visualization


def getDemand(elem):
    return elem[1]


def sortByTime(elem):
    return elem[0]


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
    N, site_bandwidth = IO.getSiteInfo(data_path)
    M, demands, time_names = IO.getClientInfo(data_path)
    QoS = IO.getConfig(data_path)
    site_client, client_site = IO.buildGraph(data_path, list(demands[0].keys()), QoS)
    site_names = site_bandwidth.keys()
    client_names = demands[0].keys()
    times = len(demands)

    POS_95 = int(times * 0.95)  # index start by 0
    special_num = times - POS_95 - 2
    special_chance = dict()
    if special_num > 0:
        for site in site_names:
            special_chance[site] = special_num

    used = dict()  # site:time(index):total_usage, for sake of calculating COST
    for site in site_names:
        used[site] = [0 for t in range(times)]
    assigns = []  # time(index):client:site:band_assigned, for solution

    for time, demand in enumerate(demands):
        # demand form:: client:demand
        cur_client_demand = list(demand.items())  # each element: (client, band demand)
        cur_client_demand.sort(key=getDemand, reverse=True)  # sort by band
        solved = False  # mark the solution for current time

        while not solved:  # solve the assignment for ONE TIME
            # reset assignment and sp
            use_special = dict()  # can only use once for current time
            capacity = site_bandwidth.copy()  # remained capacity for current time
            cur_assign = dict()

            for client, band in cur_client_demand:  # handle single client
                valid = True
                client_assign = cur_assign[client] = dict()
                if band == 0:  # zero requirement
                    continue
                available_sites = list(client_site[client])
                random.shuffle(available_sites)
                cur_use = dict()
                for site in site_names:
                    cur_use[site] = 0

                while len(available_sites) > 0 and band > 0:  # assign band to sites
                    for idx, site in enumerate(available_sites):
                        avg = max(1, band // (len(available_sites) - idx))
                        if special_chance[site] > 0 and random.randint(0, 10) < 3:
                            cur = min(capacity[site], band)  # maximize the usage
                            use_special[site] = True
                        else:
                            cur = min(avg, capacity[site])  # real assign

                        if cur == 0:
                            continue
                        capacity[site] -= cur
                        cur_use[site] += cur
                        band -= cur

                        if not client_assign.__contains__(site):
                            client_assign[site] = cur
                        else:
                            client_assign[site] += cur

                        if band == 0:  # checked if demand satisfied
                            break

                    available_sites = [site for site in available_sites if capacity[site] > 0]
                    if len(available_sites) == 0 and band > 0:  # no solution, shuffle and solve again (for all clients)
                        valid = False

                if not valid:
                    break  # jump out current demandS

            if valid:  # copy to final solution
                assigns.append(cur_assign)
                for site, use in cur_use.items():
                    used[site][time] = use
                for site in use_special.keys():
                    special_chance[site] -= 1
                solved = True
            else:
                random.shuffle(cur_client_demand)
                # print("Client: {} {} not satisfied".format(client, band))

    # total_cost = 0
    # plot = []
    # for site, usage in used.items():
    #     usage.sort()
    #     plot.append(usage)
    #     total_cost += usage[POS_95]
    # visualization.draw(plot)

    assigns = [[time_names[i], assigns[i]] for i in range(times)]
    assigns.sort(key=sortByTime)
    assigns = [assigns[i][1:] for i in range(times)]
    IO.writeOutput(output_path, assigns)
