import time as tt


def sortByPotential(elem):
    return elem[1]


def greedyAssign(valueMat, chances):
    N, T = len(valueMat[0]), len(valueMat)
    ret = [-1 for i in range(T)]
    for time in range(N):
        current_sites = sorted(enumerate(valueMat[time]), key=sortByPotential, reverse=True).__iter__()
        skew_site_idx, potential = next(current_sites, -1)
        while chances[skew_site_idx] == 0 and skew_site_idx != -1:
            skew_site_idx, potential = next(current_sites, (-1, -1))
        if skew_site_idx != -1:
            ret[time] = skew_site_idx
            chances[skew_site_idx] -= 1
    return ret


def reassign(N, T, time, add_to_site_idx, bandwidth, site_name, site_client, time_client_site_band, demands, site_time_used, POS_95):
    # reassign
    add_to_site_name = site_name[add_to_site_idx % N]
    client_cnt = len(site_client[add_to_site_name])
    potential = bandwidth - site_time_used[add_to_site_name][time]
    for i, client in enumerate(site_client[add_to_site_name]):
        client_avg_add = potential // (client_cnt - i)
        current_assign = time_client_site_band[time][client].get(add_to_site_name, 0)  # to add_to_site
        add = min(client_avg_add, demands[time][client] - current_assign)
        time_client_site_band[time][client][add_to_site_name] = current_assign + add
        site_time_used[add_to_site_name][time] += add
        potential -= add
        while add > 0:
            relative_site_cnt = len(time_client_site_band[time][client]) - 1
            j = 0
            del_site = []
            for site, band in time_client_site_band[time][client].items():
                if site != add_to_site_name:
                    site_avg_minus = add // (relative_site_cnt - j)
                    if site_avg_minus * (relative_site_cnt - j) < add:
                        site_avg_minus += 1
                    minus = min(site_avg_minus, band)
                    time_client_site_band[time][client][site] -= minus
                    if time_client_site_band[time][client][site] == 0:
                        del_site.append(site)
                    site_time_used[site][time] -= minus
                    add -= minus
                    j += 1
            for site in del_site:
                time_client_site_band[time][client].pop(site)

    total_cost = 0
    for site, usage in site_time_used.items():
        cur = sorted(usage)
        total_cost += cur[POS_95]
    return total_cost


def evaluate(solution, demands, site_bandwidth, site_client, client_site):
    start = tt.time()

    site_time_used = solution[2]
    site_chances = solution[-1]
    time_client_site_band = solution[0]
    POS_95 = solution[3]
    N = len(site_bandwidth)
    site_name = [site for site in site_bandwidth.keys()]  # idx->site name
    T = len(demands)  # number of slots
    chance = max(site_chances)
    total_chance = chance * N
    evaluation = [[0 for i in range(T)] for j in range(N)]
    # evaluate pair site_change<->time
    for site_idx in range(N):
        site = site_name[site_idx]
        for time in range(T):
            # current_use = site_time_used[site][time]
            # site_gap = site_bandwidth[site] - current_use
            # demand_gap = 0
            # for client in site_client[site]:
            #     demand_gap += demands[time][client]
            # demand_gap -= current_use
            # evaluation[time][site_idx] = min(demand_gap, site_gap)
            evaluation[time][site_idx] = reassign(N, T, time, site_idx, site_bandwidth[site], site_name, site_client.copy(), time_client_site_band.copy(), demands, site_time_used.copy(), POS_95)

    time_site = greedyAssign(evaluation, site_chances)  # time_site[i]: the site(idx) that time_i use the max
    end = tt.time()
    print(end - start)
    print(time_site)

    # reassign
    for time in range(T):
        add_to_site_idx = time_site[time]
        if add_to_site_idx == -1:
            continue
        add_to_site_name = site_name[add_to_site_idx % N]
        potential = evaluation[add_to_site_idx][time]
        # if potential is tiny, discard it
        # site_chances[add_to_site_idx % N] -= 1
        client_cnt = len(site_client[add_to_site_name])
        for i, client in enumerate(site_client[add_to_site_name]):
            client_avg_add = potential // (client_cnt - i)
            current_assign = time_client_site_band[time][client].get(add_to_site_name, 0)  # to add_to_site
            add = min(client_avg_add, demands[time][client] - current_assign)
            time_client_site_band[time][client][add_to_site_name] = current_assign + add
            site_time_used[add_to_site_name][time] += add
            potential -= add
            while add > 0:
                relative_site_cnt = len(time_client_site_band[time][client]) - 1
                j = 0
                del_site = []
                for site, band in time_client_site_band[time][client].items():
                    if site != add_to_site_name:
                        site_avg_minus = add // (relative_site_cnt - j)
                        if site_avg_minus * (relative_site_cnt - j) < add:
                            site_avg_minus += 1
                        minus = min(site_avg_minus, band)
                        time_client_site_band[time][client][site] -= minus
                        if time_client_site_band[time][client][site] == 0:
                            del_site.append(site)
                        site_time_used[site][time] -= minus
                        add -= minus
                        j += 1
                for site in del_site:
                    time_client_site_band[time][client].pop(site)

    total_cost = 0
    for site, usage in site_time_used.items():
        cur = sorted(usage)
        total_cost += cur[POS_95]
    return total_cost
