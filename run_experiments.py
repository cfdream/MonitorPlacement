import commands
import sys
import string
import re
import time
from new_generate_placement_data import GeneratePlacementData

def experiment_new(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname):
    '''
    compare optimal algorithm with greddy
    tradeoff is included here as well
    '''
    #1) X axis: node capacity, Y1: #assigned tasks, Y2: avg(avg latency of task). Y3: avg(max latency of task)
    for ith_round in range(20):
        generator = GeneratePlacementData(input_fname, topo_weight_fname, topo_weight_json_fname, topo_gravity_fname)
        generator.read_topology_data()
        #def generate_mapped_tasks(self, task_times, one_selector_x_monitors, single_path_task_path_num, multi_path_task_path_num):
        generator.generate_mapped_tasks(2, 1, 55, 55)
        
        #get input scale param
        num_nodes = generator.num_nodes 
        num_tasks = len(generator.task_info_list)
        num_modules = len(generator.module_monitor_flow_num)
        for node_capacity in [25000, 50000, 100000, 200000, 400000, 800000, 1600000, 3200000, 10000000000]:
            #-----1. run placement_max_task_num_with_latency_constrain. run with different latency constraint
            for pair_latency_limit in [1000, 2000, 1000000]:
                #-----1.1 generate data file with different node_capacity, pair_latency_limit
                #remove existing output file
                commands.getstatusoutput('rm {0}' .format(input_fname))
                generator.assign_varied_variables(node_capacity, pair_latency_limit)
                generator.output_all_data_to_file()
                print('new_generate_placement_data succeeded\n')
                
                #-----1.2 run algorithm
                start_ms = 1000 * time.time()
                ampl_str = 'ampl placement_max_task_num_with_latency_constrain.run'
                ret,output = commands.getstatusoutput(ampl_str)
                print('ret:{0}, {1}' .format(ret, output))
                end_ms = 1000 * time.time()
                time_len = end_ms - start_ms
                print("max_task_number-M-N:{num_nodes}-{num_tasks}-{num_modules}, time:{time}ms" .format(num_nodes=num_nodes, num_tasks=num_tasks, num_modules=num_modules, time=time_len))

            #-----2. run max #module algorithm
            start_ms = 1000 * time.time()
            ampl_str = 'ampl placement_csamp.run'
            ret,output = commands.getstatusoutput(ampl_str)
            print('ret:{0}, {1}' .format(ret, output))
            end_ms = 1000 * time.time()
            time_len = end_ms - start_ms
            print("max_module_number-M-N:{num_nodes}-{num_tasks}-{num_modules}, time:{time}ms" .format(num_nodes=num_nodes, num_tasks=num_tasks, num_modules=num_modules, time=time_len))

def experiment1(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname):
    '''
    compare optimal algorithm with greddy
    tradeoff is included here as well
    '''
    #1) X axis: #task, Y axis: objective value. Given mapping ratio.
    mapped_condition_monitor_ratio = 1
    pair_latency_limit = 999999999
    #for flow_times_each_node in [1, 2, 4, 8, 16, 32, 64, 128]:
    for ith_round in range(20):
        generator = GeneratePlacementData(input_fname, topo_weight_fname, topo_weight_json_fname, topo_gravity_fname)
        generator.read_topology_data()
        generator.generate_mapped_tasks()
        #for flow_times_each_node in [1, 2, 4, 8, 16]:
        #for node_capacity in [25000, 50000, 100000, 200000, 400000, 800000, 1600000, 3200000, 10000000000]:
        for node_capacity in [10000000000]:
            #1. run placement_max_assigned_pairs_with_latency_constrain.run with different latency constraint
            #for pair_latency_limit in [1000, 2000, 1000000]:
            for pair_latency_limit in [1000]:
                #1.1 generate data file
                #remove existing output file
                commands.getstatusoutput('rm {0}' .format(input_fname))
                generator.assign_varied_variables(node_capacity, pair_latency_limit)
                generator.output_all_data_to_file()
                print('new_generate_placement_data succeeded\n')
                
                #1.2 run algorithm
                start_ms = 1000*time.time()
                ampl_str = 'ampl placement_max_assigned_pairs_with_latency_constrain.run'
                ret,output = commands.getstatusoutput(ampl_str)
                print('ret:{0}, {1}' .format(ret, output))
                end_ms = 1000*time.time()
                print("placement_max_assigned_pairs_with_latency_constrain time:{0}ms" .format(end_ms-start_ms))

            #2. run greedy algorithm
            greedy_str = 'python greedy_algorithm.py input.dat >> greedy_algorithm.output'
            ret,output = commands.getstatusoutput(greedy_str)
            print("greedy_algorithm finished")

def experiment2(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname):
    '''
    placement_max_assigned_pairs_with_latency_constrain
    '''
    #1) X axis: #task, Y axis: objective value. Given mapping ratio.
    #different curve: different flow_times_each_node
    mapped_condition_monitor_ratio = 1
    for ith_round in range(20):
        generator = GeneratePlacementData(input_fname, topo_weight_fname, topo_weight_json_fname, topo_gravity_fname)
        generator.read_topology_data()
        generator.generate_mapped_tasks()
        #for each round, generate the same tasks, just change the flow_times_each_node, pair_latency_limit
        for flow_times_each_node in [1, 4, 16, 32, 10000]:
            #for topology with 11 nodes
            for pair_latency_limit in [250, 500, 1000, 2000, 3000, 4000]:
                #1. generate data file
                #remove existing output file
                commands.getstatusoutput('rm {0}' .format(input_fname))
                generator.assign_varied_variables(flow_times_each_node, pair_latency_limit)
                generator.output_all_data_to_file()
                print('new_generate_placement_data succeeded\n')

                #2. run placement_max_assigned_pairs_with_latency_constrain.run
                start_ms = 1000*time.time()
                ampl_str = 'ampl placement_max_assigned_pairs_with_latency_constrain.run'
                ret,output = commands.getstatusoutput(ampl_str)
                print('ret:{0}, {1}' .format(ret, output))
                end_ms = 1000*time.time()
                print("placement_max_assigned_pairs_with_latency_constrain flow_times_each_node:{0}, pair_latency_limit:{1}, time:{2}ms" .format(flow_times_each_node, pair_latency_limit, end_ms-start_ms))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: python run_experiments.py topo_weight_fname topo_weight_json_fname topo_gravity_fname\n')
        exit(0)
    topo_weight_fname = sys.argv[1]
    topo_weight_json_fname = sys.argv[2]
    topo_gravity_fname = sys.argv[3]
    input_fname = 'input.dat'
    experiment_new(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname)
