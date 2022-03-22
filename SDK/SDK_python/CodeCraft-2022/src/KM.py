import numpy as np

def findPath(x, N, weights, optimal_match, label_x, label_y, visit_x, visit_y, slack):
    visit_x[x] = True

    for y in range(N):
        if visit_y[y]:
            continue
        
        if weights[x][y] == label_x[x] + label_y[y]:
            visit_y[y] = True
            if optimal_match[y] == -1 or findPath(optimal_match[y], N, weights, optimal_match, label_x, label_y, visit_x, visit_y, slack):
                optimal_match[y] = x
                return True
        else:
            slack[y] = min(slack[y], label_x[x] + label_y[y] - weights[x][y])

    return False

def KM(weights):
    '''
    Kuhn-Munkres Algorithm for the optimal matching of bipartite graph
    weights: the weight matrix of the bipartite graph
    '''
    N = len(weights) # the order of weight matrix

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