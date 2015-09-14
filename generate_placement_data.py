import commands
import sys
import string
import re
import time
import random
from heapq import heappush, heappop

class GeneratePlacementData:
    INTERNET2_FLOW_NUM = 8000000 #8 million in 5 minutes
    INTERNET2_SWITCH_NUM = 11
    
    MAX_FLOWS_PER_NODE = 1
    
    NUM_CM_TASK_RAND_MIN = -5
    NUM_CM_TASK_RAND_MAX = 1

    ALPHA = 0.1
    CANDIDATE_NODES_FOR_ONE_TASK = 1

    def __init__(self):
        self.num_nodes = 0
        self.graph = {}     #connection list
        self.latency_graph = []
        self.graph_flow_num = 0

    def read_graph_topo(self, filename):
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
            link_weight = int(temp[2])
            if node1_id not in self.graph:
                self.graph[node1_id]=[]
            if node2_id not in self.graph:
                self.graph[node2_id] = []
            self.graph[node1_id].append((node2_id, link_weight))
            self.graph[node2_id].append((node1_id, link_weight))
            if node1_id > self.num_nodes:
                self.num_nodes = node1_id
            if node2_id > self.num_nodes:
                self.num_nodes = node2_id
        #print self.graph
        return self.num_nodes

    def init_graph_other_param(self, times_num_flow):
        self.graph_flow_num = 1.0 * \
            self.num_nodes / GeneratePlacementData.INTERNET2_SWITCH_NUM \
            * GeneratePlacementData.INTERNET2_FLOW_NUM 
        GeneratePlacementData.MAX_FLOWS_PER_NODE = int ( 1.0 * self.graph_flow_num / self.num_nodes / self.num_nodes * times_num_flow);

    def get_latency_between_nodes(self):
        self.latency_graph.append([])
        for srcid in range(1, self.num_nodes+1):
            self.latency_graph.append([])
            for i in range(self.num_nodes+1):
                self.latency_graph[srcid].append(-1)

            priority_queue= []
            priority_queue.append((srcid, 0))
            while len(priority_queue) > 0:
                #1. get the node_id with min dist
                # and this is the min dist for the node_id
                #print "start loop:", priority_queue
                min_node = 0
                min_dist = 999999999
                for node_id, dist in priority_queue:
                    if dist < min_dist:
                        min_dist = dist
                        min_node = node_id
                #1.1 set dist for min_node
                self.latency_graph[srcid][min_node] = min_dist
                #1.2 remove min_node from priority_queue
                priority_queue.remove((min_node, min_dist))

                #2. for neighbor nodes, update dist if necessary
                neighbor_list = self.graph[min_node]
                #print min_node, " neighbor_list:", neighbor_list
                for (neigh_id, link_weight) in neighbor_list:
                    #2.1 for each neighbor_id
                    if self.latency_graph[srcid][neigh_id] >= 0:
                        #already get min_latency for neigh_id
                        continue
                    #2.2 update neighbor dist if smaller from min_node
                    i = 0
                    exist = False
                    for i in range(len(priority_queue)):
                        (node_id, dist) = priority_queue[i]
                        if node_id == neigh_id:
                            exist = True
                            if min_dist + link_weight < dist:
                                priority_queue[i] = (neigh_id, min_dist+link_weight)
                            break
                    if not exist:
                        priority_queue.append((neigh_id, min_dist+link_weight))
                #print "end loop:", priority_queue

    def output_latency_to_file(self, out_fname): 
        #number of nodes
        #param n := 2;
        #n*n matrix, latency between nodes
        #param latency:1 2:=
        #  1 0 1
        #  2 1 0;
        out_file=open(out_fname, 'a')

        #output number of nodes
        out_file.write('#number of nodes\n')
        out_file.write("param n := {0};\n" .format(self.num_nodes)) 

        #output header
        out_file.write('#n*n matrix, latency between nodes\n')
        out_str = "param latency :\n"
        for i in range(1, self.num_nodes+1):
            out_str += " {0}" .format(i)
        out_str += ":="
        out_file.write(out_str + "\n")

        #output for the latency from each node to other nodes
        for node1_id in range(1, self.num_nodes+1):
            out_str = "{0}" .format(node1_id)
            for node2_id in range(1, self.num_nodes+1):
                out_str += " {0}" .format(self.latency_graph[node1_id][node2_id])
            out_file.write(out_str + "\n")
        out_file.write(";\n");
        out_file.close()
    
    def output_alpha(self, out_fname):
        #####Declaration of parameters
        #param alpha = 0.1;
        out_file=open(out_fname, 'a')
        out_file.write('#####Declaration of parameters\n')
        out_file.write('#param alpha = {0};\n' .format(GeneratePlacementData.ALPHA))
        out_file.close()

    def output_maximum_flows_per_node(self, out_fname):
        #maximum number of tasks each node can run
        #param max_node_tasks := 1 2 2 2;
        out_file=open(out_fname, 'a')
        out_file.write('#maximum number of tasks each node can run\n')
        out_str='param max_node_flows :=\n'
        for i in range(1, self.num_nodes+1):
            out_str += '{0} {1} \n' .format(i, GeneratePlacementData.MAX_FLOWS_PER_NODE)
        out_file.write(out_str + ';\n')
        out_file.close()

    def generate_mapped_tasks_from_gravity_model(self, out_fname, gravity_file):
        num_tasks = 0
        task_monitor_flow_num = []
        task_monitor_flow_num.append(0)
        can_assign = []
        can_assign.append([])
        
        file=open(gravity_file, 'r')
        lines=file.readlines()
        lines=map(lambda x:x[:-1], lines)
        file.close()
        #1. generate CM tasks
        for line in lines:
            #1 4 14 45 ;1.13706880384316e-05
            #1 4 7 ;5.21454666967005e-05
            #1 4 14 27 ;5.29518198748518e-05
            temp=line.split(';')
            assert(len(temp) == 2)
            path = temp[0][:-1]
            ratio = float(temp[1])
            #print("path:{0}, ratio:{1}" .format(path, ratio))
            #1. get the nodes in the path
            path_nodes_str = path.split(' ')
            path_nodes = []
            for node_str in path_nodes_str:
                node_id = int(node_str)
                path_nodes.append(node_id)
            #2. get the gravity ratio
            path_flow_num = int(self.graph_flow_num * ratio)
            #3. get the number of CM tasks per path
            num_path_cm_tasks = random.randint(GeneratePlacementData.NUM_CM_TASK_RAND_MIN, GeneratePlacementData.NUM_CM_TASK_RAND_MAX)
            for i in range(0, num_path_cm_tasks):
                task1_id = num_tasks + 1
                task2_id = num_tasks + 2
                num_tasks += 2
                #task1_id can be assigned to any nodes along the path
                can_assign.append(path_nodes)
                #task2_id
                can_assign.append(path_nodes)
                task_monitor_flow_num.append(path_flow_num)
                task_monitor_flow_num.append(path_flow_num)

        out_file=open(out_fname, 'a')
        #2. output CM tasks
        #####output can_assign matrix
        #header
        out_file.write('#number of tasks\n')
        out_str='param m := {0};\n' .format(num_tasks)
        out_file.write(out_str)

        out_file.write('#can task i be assigned to task j\n')
        out_file.write('param can_assign :\n')
        out_str = " "
        for i in range(1, self.num_nodes+1):
            out_str += " {0}" .format(i)
        out_file.write(out_str+':=\n')
        #body
        for i in range(1, num_tasks+1):
            out_str = "{0}" .format(i)
            for j in range(1, self.num_nodes+1):
                if j in can_assign[i]:
                    out_str += " 1"
                else:
                    out_str += " 0"
            out_file.write(out_str+'\n')
        out_file.write(';\n')
        print 'generate_tasks-num_tasks:{0}, and can_assign matrix' .format(num_tasks)
        
        #3 output task_monitor_flow_num
        out_str='param task_monitor_flow_num :=\n'
        for i in range(1, num_tasks+1):
            out_str += '{0} {1} \n' .format(i, task_monitor_flow_num[i])
        out_file.write(out_str + ";\n")

        #4. mapped tasks
        num_mapped_paris = num_tasks/2
        out_file.write('#number of matched tasks\n')
        out_file.write('param num_match = {0};\n' .format(num_mapped_paris))
        
        out_file.write('#num_match * 2 matrix, matched tasks\n')
        out_file.write('param matched_tasks :\n')
        out_file.write('  1 2:=\n')
        for i in range(num_mapped_paris):
            out_file.write('{0} {1} {2}\n' .format(i+1, i*2+1, i*2+2))
        out_file.close()
        print 'generate_mapped_tasks: {0} pairs of tasks generated\n' .format(num_mapped_paris)

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
        out_file.write(out_str+':=\n')
        #body
        for i in range(1, num_condition_tasks+num_measure_tasks+1):
            out_str = "{0}" .format(i)
            for j in range(1, self.num_nodes+1):
                out_str += " {0}" .format(can_assign[i][j])
            out_file.write(out_str+'\n')
        out_file.write(';\n')
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
        out_file.write('param matched_tasks :\n')
        out_file.write('  1 2:=\n')
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
        print 'generate_mapped_tasks: {0} pairs of tasks generated\n' .format(num_mapped_paris)

if __name__ == "__main__":        
    if len(sys.argv) != 5:
        print "usage: python generate_placement_data.py placement.dat topo_weight_file gravity_file times_num_flow[1,2,4,8,16]\n"
        exit(0)
    placement_fname = sys.argv[1]
    topo_fname = sys.argv[2]
    gravity_file = sys.argv[3]
    times_num_flow = int(sys.argv[4])

    #remove existing output file
    commands.getstatusoutput('rm {0}' .format(placement_fname))

    random.seed(time.time())

    generator = GeneratePlacementData()
    #alpha
    generator.output_alpha(placement_fname)
    #latency matrix
    generator.read_graph_topo(topo_fname)
    generator.init_graph_other_param(times_num_flow)
    generator.get_latency_between_nodes()
    generator.output_latency_to_file(placement_fname)
    #maximum flow per node
    generator.output_maximum_flows_per_node(placement_fname)
   
    #generate mapped tasks from gravity model data
    generator.generate_mapped_tasks_from_gravity_model(placement_fname, gravity_file)

    #old#tasks and can assigned nodes
    #generator.generate_tasks_and_candidate_nodes(placement_fname, num_condition_tasks, num_measure_tasks)
    #old#mapped tasks
    #generator.generate_mapped_tasks(placement_fname, num_condition_tasks, num_measure_tasks, condition_mapped_ratio)

    #print 'generate_placement_data for {0} condition monitors, {1} measure monitors succeeded\n' .format(num_condition_tasks, num_measure_tasks)
    print 'generate_placement_data succeeded\n'
