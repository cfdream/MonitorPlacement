import commands
import sys
import string
import re
import time
import random

class GeneratePlacementData:
    ALPHA = 0.1
    MAX_TASKS_PER_NODE = 2
    CANDIDATE_NODES_FOR_ONE_TASK = 3
    NUM_MAPPED_TASKS = 2

    def __init__(self):
        self.num_nodes = 0
        self.graph = {}     #connection list
        self.distance_graph = []

    def read_topo(self, filename):
        file=open(filename, 'r')
        lines=file.readlines()
        lines=map(lambda x:x[:-1], lines)
        file.close()

        #go through the file to get the graph
        ith_line = 0
        self.num_nodes = 0
        while ith_line < len(lines):
            if lines[ith_line][0]=='#':
                ith_line += 1
                continue
            temp=lines[ith_line].split(' ')
            ith_line += 1
            assert(len(temp) >= 2)
            node1_id = int(temp[0])
            node2_id = int(temp[1])
            if node1_id not in self.graph:
                self.graph[node1_id]=[]
            if node2_id not in self.graph:
                self.graph[node2_id] = []
            self.graph[node1_id].append(node2_id)
            self.graph[node2_id].append(node1_id)
            if node1_id > self.num_nodes:
                self.num_nodes = node1_id
            if node2_id > self.num_nodes:
                self.num_nodes = node2_id
        print self.graph
        return self.num_nodes

    def get_distance_between_nodes(self):
        self.distance_graph.append([])
        for srcid in range(1, self.num_nodes+1):
            self.distance_graph.append([])
            for i in range(self.num_nodes+1):
                self.distance_graph[srcid].append(-1)

            self.distance_graph[srcid][srcid] = 0
            ith=0
            expand_name_list=[srcid]
            while ith < len(expand_name_list):
                now_id = expand_name_list[ith]
                now_dist = self.distance_graph[srcid][now_id]
                neighbor_list = self.graph[now_id]
                for neigh_id in neighbor_list:
                    #for each neighbor_id
                    if self.distance_graph[srcid][neigh_id] >= 0:
                        #already travelled id
                        continue
                    expand_name_list.append(neigh_id)
                    self.distance_graph[srcid][neigh_id] = now_dist+1
                ith+=1

    def output_distance_to_file(self, out_fname): 
        #number of nodes
        #param n := 2;
        #n*n matrix, distance between nodes
        #param distance :1 2:=
        #  1 0 1
        #  2 1 0;
        out_file=open(out_fname, 'a')

        #output number of nodes
        out_file.write('#number of nodes\n')
        out_file.write("param n := {0};\n" .format(self.num_nodes)) 

        #output header
        out_file.write('#n*n matrix, distance between nodes\n')
        out_str = "param distance :\n"
        for i in range(1, self.num_nodes+1):
            out_str += " {0}" .format(i)
        out_str += ":="
        out_file.write(out_str + "\n")

        #output for the distance from each node to other nodes
        for node1_id in range(1, self.num_nodes+1):
            out_str = "{0}" .format(node1_id)
            for node2_id in range(1, self.num_nodes+1):
                out_str += " {0}" .format(self.distance_graph[node1_id][node2_id])
            out_file.write(out_str + "\n")
        out_file.write(";\n");
        out_file.close()
    
    def output_alpha(self, out_fname):
        #####Declaration of parameters
        #param alpha = 0.1;
        out_file=open(out_fname, 'a')
        out_file.write('#####Declaration of parameters\n')
        out_file.write('param alpha = {0};\n' .format(GeneratePlacementData.ALPHA))
        out_file.close()

    def output_maxnum_tasks_per_node(self, out_fname):
        #maximum number of tasks each node can run
        #param max_node_tasks := 1 2 2 2;
        out_file=open(out_fname, 'a')
        out_file.write('#maximum number of tasks each node can run\n')
        out_str='param max_node_tasks :=\n'
        for i in range(1, self.num_nodes+1):
            out_str += '{0} {1} \n' .format(i, GeneratePlacementData.MAX_TASKS_PER_NODE)
        out_file.write(out_str + ';\n')
        out_file.close()

    def generate_tasks_and_candidate_nodes(self, out_fname, num_condition_tasks, num_measure_tasks):
        ##number of tasks
        #param m = 4;
        ##can task i be assigned to task j
        #param can_assign :
        #    1 2 :=
        #1	1 0
        #2   0 1
        #3   1 0
        #4   0 1;
        can_assign=[]
        for i in range(0, num_condition_tasks+num_measure_tasks+1):
            can_assign.append([])
            for j in range(0, self.num_nodes+1):
                can_assign[i].append(0)
        
        for i in range(1, num_condition_tasks+num_measure_tasks+1):
            #foreach task, get CANDIDATE_NODES_FOR_ONE_TASK candidate nodes
            candidate_nodes = {}
            for j in range(GeneratePlacementData.CANDIDATE_NODES_FOR_ONE_TASK):
                rand_nodeid = 0
                while True:
                    rand_nodeid = random.randint(1, self.num_nodes)
                    if rand_nodeid not in candidate_nodes:
                        candidate_nodes[rand_nodeid] = 1
                        break
                #get one rand_nodeid
                can_assign[i][rand_nodeid] = 1
       
        #####output can_assign matrix
        out_file=open(out_fname, 'a')
        #header
        out_file.write('#number of tasks\n')
        out_str='param m = {0};\n' .format(num_condition_tasks + num_measure_tasks)
        out_file.write(out_str)

        out_file.write('#can task i be assigned to task j\n')
        out_file.write('param can_assign :\n')
        out_str = " "
        for i in range(1, self.num_nodes+1):
            out_str += " {0}" .format(i)
        out_file.write(out_str+'\n')
        #body
        for i in range(1, num_condition_tasks+num_measure_tasks+1):
            out_str = "{0}" .format(i)
            for j in range(1, self.num_nodes+1):
                out_str += " {0}" .format(can_assign[i][j])
            out_file.write(out_str+'\n')
        out_file.close()
       
    def generate_mapped_tasks(self, out_fname, num_condition_tasks, num_measure_tasks, condition_mapped_ratio):
        ##number of matched tasks
        #param num_match = 2;
        ##num_match * 2 matrix, matched tasks
        #param matched_tasks :
        #    1 2 :=
        #1	 1 2
        #2   3 4;

        num_mapped_paris = int(num_condition_tasks*condition_mapped_ratio)
        if num_mapped_paris > num_condition_tasks*num_measure_tasks:
            print "FIX IT: num_mapped_paris > num_condition_tasks * num_measure_tasks\n"
            return

        out_file=open(out_fname, 'a')
        out_file.write('#number of matched tasks\n')
        out_file.write('param num_match = {0};\n' .format(num_mapped_paris))
        
        out_file.write('#num_match * 2 matrix, matched tasks\n')
        out_file.write('  1 2\n')
        mapped_pair_map = {}
        for i in range(1, num_mapped_paris+1):
            condition_idx = random.randint(1, num_condition_tasks)
            measure_idx = random.randint(num_condition_tasks+1, num_condition_tasks+num_measure_tasks)
            map_str = '{0}_{1}' .format(condition_idx, measure_idx)
            while map_str in mapped_pair_map:
                condition_idx = random.randint(1, num_condition_tasks)
                measure_idx = random.randint(num_condition_tasks+1, num_condition_tasks+num_measure_tasks)
                map_str = '{0}_{1}' .format(condition_idx, measure_idx)
            mapped_pair_map[map_str] = 1

            out_file.write('{0} {1} {2}\n' .format(i, condition_idx, measure_idx))
        out_file.close()

if __name__ == "__main__":        
    if len(sys.argv) != 6:
        print "usage: python generate_placement_data.py topo_file placement.dat num_condition_tasks num_measure_tasks condition_mapped_ratio\n"
        exit(0)
    topo_fname = sys.argv[1]
    placement_fname = sys.argv[2]
    num_condition_tasks = int(sys.argv[3])
    num_measure_tasks = int(sys.argv[4])
    condition_mapped_ratio = float(sys.argv[5])
    
    #remove existing topo file
    commands.getstatusoutput('rm {0}' .format(placement_fname))

    random.seed(time.time())

    generator = GeneratePlacementData()
    #alpha
    generator.output_alpha(placement_fname)
    #distance matrix
    generator.read_topo(topo_fname)
    generator.get_distance_between_nodes()
    generator.output_distance_to_file(placement_fname)
    #maximum tasks per node
    generator.output_maxnum_tasks_per_node(placement_fname)
    #tasks and can assigned nodes
    generator.generate_tasks_and_candidate_nodes(placement_fname, num_condition_tasks, num_measure_tasks)
    #mapped tasks
    generator.generate_mapped_tasks(placement_fname, num_condition_tasks, num_measure_tasks, condition_mapped_ratio)
