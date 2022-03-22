import IO
import KM
import random

# root_path = "/"
root_path = "/home/melodies/cross-e_CodeCraft2022/SDK/SDK_python/"
data_path = root_path + "data/"
output_path = root_path + "output/"


def getDemand(elem):
    return elem[1]


def sortByTime(elem):
    return elem[0]


def assignOneClient(band, sites, site_capacity):  # fulfill band demand of cur client and return feasibility
    client_assign = dict()
    while len(sites) > 0 and band > 0:  # assign band to sites
        for idx, site in enumerate(sites):
            avg = max(1, band // (len(sites) - idx))
            cur = min(avg, site_capacity[site])  # real assign
            if cur == 0:
                continue
            site_capacity[site] -= cur
            site_band_used[site] = site_band_used.get(site, 0) + cur
            client_assign[site] = client_assign.get(site, 0) + cur
            band -= cur

            if band == 0:  # checked if demand satisfied
                break

        sites = [site for site in sites if site_capacity[site] > 0]  # delete sites with no capacity
        if len(sites) == 0 and band > 0:  # no solution, return for shuffle and solve again (for all clients)
            return False, dict()
    return True, client_assign


def solveDispatch(site_capacity):
    # initialize record for solution of this time
    """
    site_capacity: remained capacity of current time slot
    site_band_used: band usage of each site
    client_site_band: assignment result of each client
    client_assign: result of single client
    """
    for client, band in client_demand_current:  # handle single client
        if band == 0:  # zero requirement
            client_site_band[client] = dict()
            continue

        available_sites = list(client_site[client])
        random.shuffle(available_sites)
        valid, client_assign = assignOneClient(band, available_sites, site_capacity)
        if not valid:
            return False, dict(), dict()
        else:
            client_site_band[client] = client_assign
    return True


if __name__ == '__main__':
    """
    N: number of sites
    M: number of clients
    QoS: configuration for connectivity
    site_bandwidth: [name:band_capacity for name in site_names]
    demands: [[name:demand_t for name in client_names] for t in times (index)]
    graph: bilateral connectivity between sites and clients 
    used: [[band_used_t for t in times] indexed by server name]
    """
    N, site_bandwidth = IO.getSiteInfo(data_path)
    M, demands, time_names = IO.getClientInfo(data_path)
    QoS = IO.getConfig(data_path)
    site_client, client_site = IO.buildGraph(data_path, list(demands[0].keys()), QoS)
    site_names = site_bandwidth.keys()
    client_names = demands[0].keys()
    times = len(demands)

    POS_95 = int(times * 0.95)  # index start by 0
    special_num = times - POS_95 - 2  # TRY

    used = dict()  # site:time(index):total_usage, for sake of calculating COST
    for site in site_names:
        used[site] = [0 for t in range(times)]
    assigns = []  # time(index):client:site:band_assigned, for solution

    # solve demands for all times
    for time, demand in enumerate(demands):
        # demand form:: client:demand
        client_demand_current = list(demand.items())  # each element: (client, band demand)
        client_demand_current.sort(key=getDemand, reverse=True)  # handle client with higher demand first
        solved = False  # mark the solution for current time
        while not solved:  # solve the assignment for ONE TIME
            client_site_band = dict()
            site_band_used = dict()
            solved = solveDispatch(site_bandwidth.copy())
            if solved:  # copy to final solution
                assigns.append(client_site_band)
                for site, use in site_band_used.items():
                    used[site][time] = use
            else:
                random.shuffle(client_demand_current)

    total_cost = 0
    for site, usage in used.items():
        cur = sorted(usage)
        total_cost += usage[POS_95]

    assigns = [[time_names[i], assigns[i]] for i in range(times)]
    assigns.sort(key=sortByTime)
    assigns = [assigns[i][1] for i in range(times)]
    site_chances = [special_num for i in range(N)]
    solution = [assigns, total_cost, used, POS_95, site_chances]
    new_solution = [assigns, total_cost, used, POS_95, site_chances]  # HOW TO DEEPCOPY???
    new_cost = KM.evaluate(new_solution, demands, site_bandwidth, site_client, client_site)

    IO.writeOutput(output_path, new_solution[0])
