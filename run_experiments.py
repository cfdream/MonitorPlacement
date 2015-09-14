import commands
import sys
import string
import re

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'usage: python run_experiments.py topo_weight_fname topo_gravity_fname\n'
        exit(0)
    topo_weight_fname = sys.argv[1]
    topo_gravity_fname = sys.argv[2]
    input_fname = 'input.dat'
    
    #experiment 1
    #1) X axis: #task, Y axis: objective value. Given mapping ratio.
    mapped_condition_monitor_ratio = 1
    for flow_times_each_node in [1, 2, 4, 8, 16]:
        for ith_round in range(30):
            #generate data file
            generate_str = 'python generate_placement_data.py {input_fname} {topo_weight_fname} {topo_gravity_fname} {flow_times_each_node}' .format(input_fname=input_fname, topo_weight_fname=topo_weight_fname, topo_gravity_fname=topo_gravity_fname, flow_times_each_node=flow_times_each_node)
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

            #run placement_max_assigned_pairs.run
            ampl_str = 'ampl placement_max_assigned_pairs.run'
            ret,output = commands.getstatusoutput(ampl_str)
            print 'ret:{0}, {1}' .format(ret, output)

    #experiment 2
    
