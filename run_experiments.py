import commands
import sys
import string
import re
import time
from new_generate_placement_data import GeneratePlacementData

def experiment1(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname):
    '''
    compare optimal algorithm with greddy
    '''
    #1) X axis: #task, Y axis: objective value. Given mapping ratio.
    mapped_condition_monitor_ratio = 1
    pair_latency_limit = 999999999
    #for flow_times_each_node in [1, 2, 4, 8, 16, 32, 64, 128]:
    for flow_times_each_node in [1]:
        for ith_round in range(1):
            #generate data file
            generate_str = 'python new_generate_placement_data.py {input_fname} {topo_weight_fname} {topo_weight_json_fname} {topo_gravity_fname} {flow_times_each_node} {pair_latency_limit}' .format(input_fname=input_fname, topo_weight_fname=topo_weight_fname, topo_weight_json_fname=topo_weight_json_fname, topo_gravity_fname=topo_gravity_fname, flow_times_each_node=flow_times_each_node, pair_latency_limit=pair_latency_limit)
            ret,output = commands.getstatusoutput(generate_str)
            print 'ret:{0}, {1}' .format(ret, output)

            #run placement_max_assigned_pairs_with_latency_constrain.run
            start_ms = 1000*time.time()
            ampl_str = 'ampl placement_max_assigned_pairs_with_latency_constrain.run'
            ret,output = commands.getstatusoutput(ampl_str)
            print 'ret:{0}, {1}' .format(ret, output)
            end_ms = 1000*time.time()
            print "placement_max_assigned_pairs_with_latency_constrain time:{0}ms" .format(end_ms-start_ms)

            #run greedy algorithm
            greedy_str = 'python greedy_algorithm.py input.dat >> greedy_algorithm.output'
            ret,output = commands.getstatusoutput(greedy_str)
            print "greedy_algorithm finished"

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
                generator.calculate_params_basedOn_input(flow_times_each_node, pair_latency_limit)
                generator.output_all_data_to_file()
                print 'new_generate_placement_data succeeded\n'

                #2. run placement_max_assigned_pairs_with_latency_constrain.run
                start_ms = 1000*time.time()
                ampl_str = 'ampl placement_max_assigned_pairs_with_latency_constrain.run'
                ret,output = commands.getstatusoutput(ampl_str)
                print 'ret:{0}, {1}' .format(ret, output)
                end_ms = 1000*time.time()
                print "placement_max_assigned_pairs_with_latency_constrain flow_times_each_node:{0}, pair_latency_limit:{1}, time:{2}ms" .format(flow_times_each_node, pair_latency_limit, end_ms-start_ms)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'usage: python run_experiments.py topo_weight_fname topo_weight_json_fname topo_gravity_fname\n'
        exit(0)
    topo_weight_fname = sys.argv[1]
    topo_weight_json_fname = sys.argv[2]
    topo_gravity_fname = sys.argv[3]
    input_fname = 'input.dat'
    #experiment1(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname)
    experiment2(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname)
