import sys
import re
import statistics

class GetNumTasksVsObjective():
    def get_result(self, raw_fname):
        n_pattern = re.compile("^n = (\d+)")
        m_pattern = re.compile("^m = (\d+)")
        value_pattern = re.compile(".*= (\d+)")

        node_flow_num_vs_performance = {}

        in_file = open(raw_fname, 'r')
        lines = in_file.readlines()
        in_file.close()
        num_nodes = 0
        num_candidate_pairs = 0
        num_tasks=0
        max_node_flows = 0
        num_pairs = 0
        latency = 0
        flow_avg_latency = 0
        ith_match = 0
        each_output_num_match = 8
        for line in lines:
            #get each value
            match = value_pattern.match(line)
            if match != None:
                #print("{0}" .format(line))
                if ith_match % each_output_num_match == 0:
                    pass
                elif ith_match % each_output_num_match == 1:
                    num_nodes = int(match.group(1))
                elif ith_match % each_output_num_match == 2:
                    num_tasks = int(match.group(1))
                elif ith_match % each_output_num_match == 3:
                    max_node_flows = int(match.group(1))
                elif ith_match % each_output_num_match == 4:
                    num_pairs = int(match.group(1))
                elif ith_match % each_output_num_match == 5:
                    latency = int(match.group(1))
                elif ith_match % each_output_num_match == 6:
                    flow_avg_latency = int(match.group(1))
                elif ith_match % each_output_num_match == 7:
                    num_candidate_pairs = int(match.group(1))
                
                if ith_match % each_output_num_match == (each_output_num_match-1):
                    if max_node_flows not in node_flow_num_vs_performance:
                        node_flow_num_vs_performance[max_node_flows] = []
                    node_flow_num_vs_performance[max_node_flows].append(
                        (num_nodes, num_tasks, num_pairs, latency, flow_avg_latency, num_candidate_pairs)
                    )
                
                #
                ith_match += 1
        
        #statistics results
        for max_node_flows, tuples in sorted(node_flow_num_vs_performance.items(), key=lambda item: item[0]):
            list_num_tasks = []
            list_num_candidate_pairs = []
            list_num_pairs = []
            list_latency = []
            list_flow_avg_latency = []
            for one_tuple in tuples:
                list_num_tasks.append(one_tuple[1])
                list_num_pairs.append(one_tuple[2])
                list_latency.append(one_tuple[3])
                list_flow_avg_latency.append(one_tuple[4])
                list_num_candidate_pairs.append(one_tuple[5])
            avg_num_tasks = statistics.mean(list_num_tasks)
            avg_num_candidate_pairs = statistics.mean(list_num_candidate_pairs)
            avg_num_pairs = statistics.mean(list_num_pairs)
            avg_latency = statistics.mean(list_latency)
            avg_flow_avg_latency = statistics.mean(list_flow_avg_latency)
            stdv_num_tasks = 0
            stdv_num_candidate_pairs = 0
            stdv_num_pairs = 0
            stdv_latency = 0
            stdv_flow_avg_latency = 0
            if len(tuples) > 1:
                stdv_num_tasks = statistics.stdev(list_num_tasks)
                stdv_num_candidate_pairs = statistics.stdev(list_num_candidate_pairs)
                stdv_num_pairs = statistics.stdev(list_num_pairs)
                stdv_latency = statistics.stdev(list_latency)
                stdv_flow_avg_latency = statistics.stdev(list_flow_avg_latency)
            print(max_node_flows, avg_num_tasks, stdv_num_tasks, avg_num_candidate_pairs, stdv_num_candidate_pairs, avg_num_pairs, stdv_num_pairs, avg_latency, stdv_latency, avg_flow_avg_latency, stdv_flow_avg_latency) 
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage:python3 get_num_tasks_vs_objective.py raw_result.output")
        exit(0)
    result_calculator = GetNumTasksVsObjective()
    result_calculator.get_result(sys.argv[1])
