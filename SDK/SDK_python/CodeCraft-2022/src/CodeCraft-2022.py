import csv
import numpy as np
import os
import configparser

N = 0
site_bandwidth = []
site_name = []
data_path = "../../../../data/"
with open(os.path.abspath(data_path + "site_bandwidth.csv")) as f:
    reader = csv.reader(f)
    firstLine = True
    name = ""
    bd = 0
    for row in reader:
        if firstLine:
            firstLine = False
        else:
            name, bd = row
            site_name.append(name)
            site_bandwidth.append(int(bd))
    N = len(site_name)

client_name = []
demands = dict()
with open(os.path.abspath(data_path + "demand.csv")) as f:
    reader = csv.reader(f)
    firstLine = True
    M = 0
    for row in reader:
        if firstLine:
            firstLine = False
            M = len(row) - 1
            client_name = row[1:]
        else:
            demands[row[0]] = [int(band) for band in row[1:]]

cf = configparser.ConfigParser()
cf.read(os.path.abspath(data_path + "config.ini"))
QoS = cf.getint("config", "qos_constraint")

graph = dict()
with open(os.path.abspath(data_path + "qos.csv")) as f:
    reader = csv.reader(f)
    firstLine = True
    for s, row in enumerate(reader):
        if firstLine:
            firstLine = False
            continue
        s -= 1
        graph[s] = set()
        for c, q in enumerate(row[1:]):
            if int(q) < QoS:
                c = c + N  # shift of client id
                graph[s].add(c - 1 + N)
                if not graph.__contains__(c):
                    graph[c] = set()
                graph[c].add(s)

used = [[0 for t in range(len(demands))] for _ in range(N)]  # server:time:total
t = 0
assigns = []
for time, demand in demands.items():
    assign = dict()  # client: server:band
    client_demand = [[demand[c], c + N] for c in range(len(demand))]
    client_demand.sort(reverse=True)
    cap = site_bandwidth.copy()
    for band, c in client_demand:
        assign[c] = dict()
        if band == 0:  # zero requirement
            continue
        cnt = len(graph[c])
        while band > 0:
            for site in graph[c]:
                avg = band // cnt
                cur = min(band // cnt, cap[site])
                cap[site] -= cur
                used[site][t] += cur
                band -= cur
                if not assign[c].__contains__(site):
                    assign[c][site] = cur
                else:
                    assign[c][site] += cur
                cnt -= 1
    assigns.append(assign)
    t += 1

total_cost = 0
pos = int(len(demands) * 0.95)
for site in range(N):
    used[site].sort()
    total_cost += used[site][pos]


output = []
for assign in assigns:
    for client in range(M):
        cur = client_name[client] + ":"
        for site, band in assign[client + N].items():
            cur += "<{},{}>,".format(site_name[site], band)
        if cur[-1] == ",":
            cur = cur[:-1]
        output.append(cur)

with open(os.path.abspath("../../output/solution.txt"), 'w') as f:
    for row in output:
        f.write(row + "\n")

check = 0
