import csv
import os
import configparser


def getSiteInfo(data_path):
    N = 0
    site_bandwidth = dict()
    with open(os.path.abspath(data_path + "site_bandwidth.csv")) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            name, bd = row
            site_bandwidth[name] = int(bd)
        N = len(site_bandwidth)
    return N, site_bandwidth


def getClientInfo(data_path):
    client_name = []
    demands = []
    times = []
    with open(os.path.abspath(data_path + "demand.csv")) as f:
        reader = csv.reader(f)
        firstLine = True
        for row in reader:
            if firstLine:
                firstLine = False
                M = len(row) - 1
                client_name = row[1:]
            else:
                cur = dict()
                for index, band in enumerate(row[1:]):
                    cur[client_name[index]] = int(band)
                demands.append(cur)
                times.append(row[0])
    return M, demands, times


def getConfig(data_path):
    cf = configparser.ConfigParser()
    cf.read(os.path.abspath(data_path + "config.ini"))
    QoS = cf.getint("config", "qos_constraint")
    return QoS


def buildGraph(data_path, client_name, QoS):
    site_client = dict()
    client_site = dict()
    graph = dict()
    with open(os.path.abspath(data_path + "qos.csv")) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            site = row[0]
            site_client[site] = set()
            for index, qos in enumerate(row[1:]):
                if int(qos) < QoS:
                    client = client_name[index]
                    site_client[site].add(client)
                    if not client_site.__contains__(client):
                        client_site[client] = set()
                    client_site[client].add(site)
    return site_client, client_site


def writeOutput(output_path, assigns):
    output = []
    for assign in assigns:
        for client, client_assign in assign.items():
            cur = client + ":"
            for site, band in client_assign.items():
                if band > 0:
                    cur += "<{},{}>,".format(site, band)
            if cur[-1] == ",":
                cur = cur[:-1]
            output.append(cur)

    with open(os.path.abspath(output_path + "solution.txt"), 'w') as f:
        for row in output:
            f.write(row + "\n")
