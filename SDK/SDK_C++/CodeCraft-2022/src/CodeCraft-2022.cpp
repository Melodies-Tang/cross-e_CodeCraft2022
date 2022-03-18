#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <set>
using namespace std;

int main() {
    vector<int> site_bandwidth;
    vector<string> site_name;
    ifstream site("../../../data/site_bandwidth.csv");
    

    vector<string> client_name;
    vector<vector<int>> demands;
    map<int, set<int>> graph;
    int QoS = 0;;
	return 0;
}
