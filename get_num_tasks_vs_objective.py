import sys
import re
import statistics

class GetNumTasksVsObjective():
    def get_result(self, raw_fname):
        flow_info_pattern = re.compile("^(\d+)\t(\d+)\t([-]*\d+)\t([-]*\d+)")
        sample_map_size_pattern = re.compile("^sample_hashmap_size:(\d+)")
        condition_map_size_pattern = re.compile("^condition_hashmap_size:(\d+)")

        n_pattern = re.compile("^n = (\d+)")
        m_pattern = re.compile("^m = (\d+)")
        #task_ratio_pattern = re.compile("^num_match\/m = (\d+[.\d+]*)")
        #csamp_max_assigned_obj_pattern = re.compile("\(n\*num_match\) = (\d+[.\d+]*)")
        csamp_max_assigned_obj_pattern = re.compile("  \(n\*num_match\) = (\d+[.\d+])")
        max_combine_obj_pattern = re.compile("max_combined_objective = (\d+[.\d+]*)")
        num_pairs_pattern = re.compile("  \],i\]\*g\[matched_tasks\[k\,2\]\,j\] = (\d+)")
        latency_pattern = re.compile("  matched_tasks\[k\,1\]\,i\]\*g\[matched_tasks\[k\,2\]\,j\] = (\d+)")

        num_tasks_vs_obj_map = {}

        in_file = open(raw_fname, 'r')
        lines = in_file.readlines()
        in_file.close()
        num_tasks=0
        obj_value = 0
        last_instance_got = 0
        num_pairs = 0
        latency = 0
        for line in lines:
            #get num of tasks
            match = m_pattern.match(line)
            if match != None:
                num_tasks = int(match.group(1))

            #get object value
            match = csamp_max_assigned_obj_pattern.match(line)
            if match != None:
                obj_value = float(match.group(1))
            match = max_combine_obj_pattern.match(line)
            if match != None:
                obj_value = float(match.group(1))
            
            #get num_pairs
            match = num_pairs_pattern.match(line)
            if match != None:
                num_pairs = int(match.group(1))

            #get latency
            match = latency_pattern.match(line)
            if match != None:
                latency = int(match.group(1))
                last_instance_got = 1
                #print(num_tasks, obj_value, num_pairs, latency)

            #add into map
            if last_instance_got == 1:
                last_instance_got = 0
                #print(num_tasks, obj_value)
                if num_tasks not in num_tasks_vs_obj_map:
                    num_tasks_vs_obj_map[num_tasks] = []
                    num_tasks_vs_obj_map[num_tasks].append([])
                    num_tasks_vs_obj_map[num_tasks].append([])
                    num_tasks_vs_obj_map[num_tasks].append([])
                num_tasks_vs_obj_map[num_tasks][0].append(obj_value)
                num_tasks_vs_obj_map[num_tasks][1].append(num_pairs)
                num_tasks_vs_obj_map[num_tasks][2].append(latency)
        
        #sort num_tasks_vs_obj_map.items() according to key:num_tasks 
        print(sorted(num_tasks_vs_obj_map.keys()))
        avg_obj_str = ""
        stdv_obj_str = ""
        avg_numpairs_str = ""
        stdv_numpairs_str = ""
        avg_latency_str = ""
        stdv_latency_str = ""

        for num_tasks, obj_lists in sorted(num_tasks_vs_obj_map.items()):
            avg_obj = statistics.mean(obj_lists[0])
            stdv_obj =statistics.stdev(obj_lists[0])
            avg_num_pairs = statistics.mean(obj_lists[1])
            stdv_num_pairs = statistics.stdev(obj_lists[1])
            avg_latency = statistics.mean(obj_lists[2])
            stdv_latency = statistics.stdev(obj_lists[2])

            avg_obj_str = "{0} {1}" .format(avg_obj_str, avg_obj)
            stdv_obj_str = "{0} {1}" .format(stdv_obj_str, stdv_obj)
            avg_numpairs_str = "{0} {1}" .format(avg_numpairs_str, avg_num_pairs)
            stdv_numpairs_str = "{0} {1}" .format(stdv_numpairs_str, stdv_num_pairs)
            avg_latency_str = "{0} {1}" .format(avg_latency_str, avg_latency)
            stdv_latency_str = "{0} {1}" .format(stdv_latency_str, stdv_latency)
        print(avg_obj_str)
        print(stdv_obj_str)
        print(avg_numpairs_str)
        print(stdv_numpairs_str)
        print(avg_latency_str)
        print(stdv_latency_str)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage:python3 get_num_tasks_vs_objective.py raw_result.output")
        exit(0)
    result_calculator = GetNumTasksVsObjective()
    result_calculator.get_result(sys.argv[1])
