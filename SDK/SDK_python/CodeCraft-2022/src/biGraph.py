# def solveGraph(evaluation):
#     return cost, solution


def moveBandwidth(solution, demands, site_capacity, site_client, client_site):
    """
    :param solution: solution = [assigns, total_cost, used, POS_95]
    :param demands:
    :param site_capacity:
    :param site_client:
    :param client_site:
    Evaluate room for improving for each site by?
    Evaluation: matrix_s_t: the remained capacity/demand for site s and time t
    Use the evaluation result to solve the graph (connection site->time) KM-algorithm
        detail:
        for each feasible assignment sites->times:
            find the total cost of current solution
            set the final solution if it's the best so far
            go to the direction for improving?
    Use the best site->time assignment to update solution
    :return: fine-tuned solution
    """
    return solution
