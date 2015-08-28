import commands
import sys
import string
import re

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'usage: python run_experiments.py topo_fname num_nodes_in_topo\n'
        exit(0)
    topo_fname = sys.argv[1]
    num_nodes = int(sys.argv[2])
    input_fname = 'input.dat'
    
    #experiment 1
    #1) X axis: #task, Y axis: objective value. Given mapping ratio.
    mapped_condition_monitor_ratio = 1
    #for task_ratio in [0.5, 1, 2, 4, 8]:
    for task_ratio in [0.5]:
        for ith_round in range(1):
            num_condition_tasks = int(num_nodes * task_ratio)
            num_measure_tasks = num_condition_tasks
            
            #generate data file
            generate_str = 'python generate_placement_data.py {topo_fname} {input_fname} {num_condition_tasks} {num_measure_tasks} {mapped_ratio}' .format(topo_fname=topo_fname, input_fname=input_fname, num_condition_tasks=num_condition_tasks, num_measure_tasks=num_measure_tasks, mapped_ratio=mapped_condition_monitor_ratio)
            ret,output = commands.getstatusoutput(generate_str)
            print 'ret:{0}, {1}' .format(ret, output)

            #run our approach
            ampl_str = 'ampl placement_max_conbined_objective.run'
            ret,output = commands.getstatusoutput(ampl_str)
            print 'ret:{0}, {1}' .format(ret, output)

            #run csamp
            ampl_str = 'ampl placement_csamp.run'
            ret,output = commands.getstatusoutput(ampl_str)
            print 'ret:{0}, {1}' .format(ret, output)

    #experiment 2
    
