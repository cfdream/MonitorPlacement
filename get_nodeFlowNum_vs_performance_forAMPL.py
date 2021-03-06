import sys
import re
import statistics

class GetNumTasksVsObjective():
    def get_result(self, raw_fname):
        value_pattern = re.compile(".*= (\d+.*)")

        latencyLimit_nodeFlowNum_vs_performance = {}

        in_file = open(raw_fname, 'r')
        lines = in_file.readlines()
        in_file.close()
        num_nodes = 0
        num_tasks=0
        num_candidate_pairs = 0
        pair_latency_limit = 0
        max_node_flows = 0
        num_success_pairs = 0
        flow_avg_latency = 0
        max_flow_latency = 0
        ith_match = 0
        each_output_num_match = 8
        for line in lines:
            #get each value
            match = value_pattern.match(line)
            if match != None:
                #print(line)
                #print("{0}" .format(line))
                if ith_match % each_output_num_match == 0:
                    num_nodes = int(match.group(1))
                elif ith_match % each_output_num_match == 1:
                    num_tasks = int(match.group(1))
                elif ith_match % each_output_num_match == 2:
                    num_candidate_pairs = int(match.group(1))
                elif ith_match % each_output_num_match == 3:
                    pair_latency_limit = int(float(match.group(1)))
                elif ith_match % each_output_num_match == 4:
                    max_node_flows = int(float(match.group(1)))
                elif ith_match % each_output_num_match == 5:
                    num_success_pairs = int(match.group(1))
                elif ith_match % each_output_num_match == 6:
                    flow_avg_latency = float(match.group(1))
                elif ith_match % each_output_num_match == 7:
                    max_flow_latency = int(match.group(1))
                if ith_match % each_output_num_match == (each_output_num_match-1):
                    #if pair_latency_limit != 16000:
                        #set pair_latency_limit to bigger enough, as here only want to investigate the effect of max_node_flows
                    #    ith_match += 1
                    #    continue
                    #print(max_node_flows, pair_latency_limit)
                    if pair_latency_limit not in latencyLimit_nodeFlowNum_vs_performance:
                        latencyLimit_nodeFlowNum_vs_performance[pair_latency_limit] = {}
                    if max_node_flows not in latencyLimit_nodeFlowNum_vs_performance[pair_latency_limit]:
                        latencyLimit_nodeFlowNum_vs_performance[pair_latency_limit][max_node_flows] = []
                    latencyLimit_nodeFlowNum_vs_performance[pair_latency_limit][max_node_flows].append(
                        (num_nodes, num_tasks, num_candidate_pairs, num_success_pairs, flow_avg_latency, max_flow_latency)
                    )
                
                ith_match += 1
        
        #statistics results
        for latencyLimit, maxNodeFlows_perform_map in sorted(latencyLimit_nodeFlowNum_vs_performance.items(), key=lambda item: item[0]):
            for max_node_flows, perfom_tuples in sorted(maxNodeFlows_perform_map.items(), key=lambda item:item[0]):
                #print(max_node_flows, latencyLimit, len(perfom_tuples))
                list_num_tasks = []
                list_num_candidate_pairs = []
                list_num_succ_pairs = []
                list_flow_avg_latency = []
                all_rounds_max_flow_latency = 0
                for one_tuple in perfom_tuples:
                    list_num_tasks.append(one_tuple[1])
                    list_num_candidate_pairs.append(one_tuple[2])
                    list_num_succ_pairs.append(one_tuple[3])
                    list_flow_avg_latency.append(one_tuple[4])
                    all_rounds_max_flow_latency = max(all_rounds_max_flow_latency, one_tuple[5])
                avg_num_tasks = statistics.mean(list_num_tasks)
                avg_num_candidate_pairs = statistics.mean(list_num_candidate_pairs)
                avg_num_succ_pairs = statistics.mean(list_num_succ_pairs)
                avg_flow_avg_latency = statistics.mean(list_flow_avg_latency)
                stdv_num_tasks = 0
                stdv_num_candidate_pairs = 0
                stdv_num_succ_pairs = 0
                stdv_flow_avg_latency = 0
                if len(perfom_tuples) > 1:
                    stdv_num_tasks = statistics.stdev(list_num_tasks)
                    stdv_num_candidate_pairs = statistics.stdev(list_num_candidate_pairs)
                    stdv_num_succ_pairs = statistics.stdev(list_num_succ_pairs)
                    stdv_flow_avg_latency = statistics.stdev(list_flow_avg_latency)
                print(latencyLimit, max_node_flows, avg_num_tasks, stdv_num_tasks, avg_num_candidate_pairs, stdv_num_candidate_pairs, avg_num_succ_pairs, stdv_num_succ_pairs, avg_flow_avg_latency, stdv_flow_avg_latency, all_rounds_max_flow_latency) 
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage:python3 get_num_tasks_vs_objective.py raw_result.output")
        exit(0)
    result_calculator = GetNumTasksVsObjective()
    result_calculator.get_result(sys.argv[1])
