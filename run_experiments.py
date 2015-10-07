import commands
import sys
import string
import re
import time

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

            #run our approach
            #ampl_str = 'ampl placement_max_conbined_objective.run'
            #ret,output = commands.getstatusoutput(ampl_str)
            #print 'ret:{0}, {1}' .format(ret, output)

            #run csamp
            #ampl_str = 'ampl placement_csamp.run'
            #ret,output = commands.getstatusoutput(ampl_str)
            #print 'ret:{0}, {1}' .format(ret, output)

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
    mapped_condition_monitor_ratio = 1
    #TODO: flow_times_each_node should be decided
    for flow_times_each_node in [1, 2, 4]:
        #for pair_latency_limit in [50, 100, 150, 200, 250, 300]:
        for pair_latency_limit in [5000]:
            for ith_round in range(10):
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

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'usage: python run_experiments.py topo_weight_fname topo_weight_json_fname topo_gravity_fname\n'
        exit(0)
    topo_weight_fname = sys.argv[1]
    topo_weight_json_fname = sys.argv[2]
    topo_gravity_fname = sys.argv[3]
    input_fname = 'input.dat'
    experiment1(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname)
    #experiment2(topo_weight_fname, topo_weight_json_fname, topo_gravity_fname, input_fname)

