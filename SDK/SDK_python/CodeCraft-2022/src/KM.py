def findPath(x, N, weights, optimal_match, label_x, label_y, visit_x, visit_y, slack):
    visit_x[x] = True

    for y in range(N):
        if visit_y[y]:
            continue

        if weights[x][y] == label_x[x] + label_y[y]:
            visit_y[y] = True
            if optimal_match[y] == -1 or findPath(optimal_match[y], N, weights, optimal_match, label_x, label_y,
                                                  visit_x, visit_y, slack):
                optimal_match[y] = x
                return True
        else:
            slack[y] = min(slack[y], label_x[x] + label_y[y] - weights[x][y])

    return False


def evaluate(solution, demands, site_bandwidth, site_client, client_site):
    site_time_used = solution[2]
    site_chances = solution[-1]
    time_client_site_band = solution[0]
    POS_95 = solution[3]
    N = len(site_bandwidth)
    site_name = [site for site in site_bandwidth.keys()]  # idx->site name
    T = len(demands)  # number of slots
    chance = max(site_chances)
    total_chance = chance * N
    matrix_size = max(T, total_chance)  # row:site_chance_idx  col:time_idx
    evaluation = [[0 for i in range(matrix_size)] for j in range(matrix_size)]  # fill with 0
    row = 0
    zeros = [0 for i in range(T)]
    client_time_gap = dict()
    # evaluate pair site_change<->time
    for site_idx in range(N):
        site = site_name[site_idx]
        site_potential_list = [0 for i in range(T)]
        for time in range(T):
            current_use = site_time_used[site][time]
            site_gap = site_bandwidth[site] - current_use
            demand_gap = 0
            for client in site_client[site]:
                demand_gap += demands[time][client]
            demand_gap -= current_use
            site_potential_list[time] = min(demand_gap, site_gap)
        for i in range(chance):
            evaluation[row][:T] = site_potential_list.copy() if i < site_chances[site_idx] else zeros.copy()
            row += 1

    time_site = KM(evaluation)  # time_site[i]: the site(idx) that time_i use the max
    # reassign
    for time in range(T):
        add_to_site_idx = time_site[time]
        add_to_site_name = site_name[add_to_site_idx % N]
        potential = evaluation[add_to_site_idx][time]
        # if potential is tiny, discard it
        site_chances[add_to_site_idx % N] -= 1
        client_cnt = len(site_client[add_to_site_name])
        for i, client in enumerate(site_client[add_to_site_name]):
            client_avg_add = potential // (client_cnt - i)
            add = min(client_avg_add, demands[time][client] - time_client_site_band[time][client][add_to_site_name])
            time_client_site_band[time][client][add_to_site_name] += add
            site_time_used[add_to_site_name][time] += add
            potential -= add
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
        total_cost += usage[POS_95]
    return total_cost


def KM(weights):
    """
    MATCH ONCE
    Kuhn-Munkres Algorithm for the optimal matching of bipartite graph
    weights: the weight matrix of the bipartite graph
    """
    N = len(weights)  # the order of weight matrix

    # Initialization
    optimal_match = [-1 for i in range(N)]
    label_y = [0 for i in range(N)]
    label_x = []
    for weight in weights:
        label_x.append(max(weight))

    for x in range(N):
        slack = [float("inf") for i in range(N)]

        while True:
            visit_x = [False for i in range(N)]
            visit_y = [False for i in range(N)]

            if findPath(x, N, weights, optimal_match, label_x, label_y, visit_x, visit_y, slack):
                break

            temp = float("inf")
            for y in range(N):
                if not visit_y[y] and slack[y] < temp:
                    temp = slack[y]

            if temp == float("inf"):
                print("There is no solution")
                return

            for i in range(N):
                if visit_x[i]:
                    label_x[i] -= temp
                if visit_y[i]:
                    label_y[i] += temp
                else:
                    slack[i] -= temp

    return optimal_match


if __name__ == '__main__':
    a = [[2, 3, 0, 3, 4],
         [0, 4, 2, 0, 5],
         [2, 6, 0, 0, 6],
         [0, 8, 7, 9, 4],
         [1, 0, 7, 0, 9]]
    # a = [[2, 4], [2, 4]]
    ans = KM(a)
    print(ans)
