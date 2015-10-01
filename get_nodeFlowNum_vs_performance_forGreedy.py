import sys
import re
import statistics

class GetNumTasksVsObjective():
    def get_result(self, raw_fname):
        node_flow_num_vs_performance = {}

        in_file = open(raw_fname, 'r')
        lines = in_file.readlines()
        in_file.close()
        for line in lines:
            #get each value
            line = line[1:-2]
            #print(line)
            items = line.split(', ')
            if len(items) != 8:
                continue
            num_nodes = int(items[0])
            num_tasks = int(items[1])
            num_candidate_pair = int(items[2])
            max_node_flows = int(items[3])
            num_pairs = int(items[4])
            latency = int(items[5])
            flow_avg_latency = int(items[7])

            if max_node_flows not in node_flow_num_vs_performance:
                node_flow_num_vs_performance[max_node_flows] = []
            node_flow_num_vs_performance[max_node_flows].append(
                (num_nodes, num_tasks, num_candidate_pair, num_pairs, latency, flow_avg_latency)
            )
                
        #statistics results
        for max_node_flows, tuples in sorted(node_flow_num_vs_performance.items(), key=lambda item: item[0]):
            list_num_tasks = []
            list_num_candidate_pair = []
            list_num_pairs = []
            list_latency = []
            list_flow_avg_latency = []
            for one_tuple in tuples:
                list_num_tasks.append(one_tuple[1])
                list_num_candidate_pair.append(one_tuple[2])
                list_num_pairs.append(one_tuple[3])
                list_latency.append(one_tuple[4])
                list_flow_avg_latency.append(one_tuple[5])
            avg_num_tasks = statistics.mean(list_num_tasks)
            avg_num_candidate_pair = statistics.mean(list_num_candidate_pair)
            avg_num_pairs = statistics.mean(list_num_pairs)
            avg_latency = statistics.mean(list_latency)
            avg_flow_avg_latency = statistics.mean(list_flow_avg_latency)
            stdv_num_tasks = 0
            stdv_num_candidate_pair = 0
            stdv_num_pairs = 0
            stdv_latency = 0
            stdv_flow_avg_latency = 0
            if len(tuples) > 1:
                stdv_num_tasks = statistics.stdev(list_num_tasks)
                stdv_num_candidate_pair = statistics.stdev(list_num_candidate_pair)
                stdv_num_pairs = statistics.stdev(list_num_pairs)
                stdv_latency = statistics.stdev(list_latency)
                stdv_flow_avg_latency = statistics.stdev(list_flow_avg_latency)
            print(max_node_flows, avg_num_tasks, stdv_num_tasks, avg_num_candidate_pair, stdv_num_candidate_pair, avg_num_pairs, stdv_num_pairs, avg_latency, stdv_latency, avg_flow_avg_latency, stdv_flow_avg_latency) 
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage:python3 get_num_tasks_vs_objective.py raw_result.output")
        exit(0)
    result_calculator = GetNumTasksVsObjective()
    result_calculator.get_result(sys.argv[1])
