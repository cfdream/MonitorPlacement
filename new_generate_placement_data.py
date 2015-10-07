import commands
import sys
import string
import re
import time
import random
from sets import Set
from heapq import heappush, heappop
import json
from YenKSP import algorithmAPI
from YenKSP import DiGraph

class GeneratePlacementData:
    INTERNET2_FLOW_NUM = 8000000 #8 million in 5 minutes
    INTERNET2_SWITCH_NUM = 11
    
    MAX_FLOWS_PER_NODE = 1
    
    NUM_CM_TASK_RAND_MIN = -30
    NUM_CM_TASK_RAND_MAX = 5

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
                self.graph[node1_id] = {}
            if node2_id not in self.graph:
                self.graph[node2_id] = {}
            self.graph[node1_id][node2_id] = link_weight
            #self.graph[node1_id].append((node2_id, link_weight))
            if node1_id > self.num_nodes:
                self.num_nodes = node1_id
            if node2_id > self.num_nodes:
                self.num_nodes = node2_id
        #print self.graph
        with open('topo.json', 'w') as fp:
            json.dump(self.graph, fp)
        return self.num_nodes

    def init_graph_other_param(self, times_num_flow):
        self.graph_flow_num = 1.0 * \
            self.num_nodes / GeneratePlacementData.INTERNET2_SWITCH_NUM \
            * GeneratePlacementData.INTERNET2_FLOW_NUM 
        GeneratePlacementData.MAX_FLOWS_PER_NODE = int ( 1.0 * self.graph_flow_num / self.num_nodes / self.num_nodes / 2 * times_num_flow);

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
                for (neigh_id, link_weight) in neighbor_list.items():
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

    #a very small positive real number, used for linearization.
    def output_epsilon(self, out_fname):
        out_file=open(out_fname, 'a')
        out_file.write('#####Declaration of parameters\n')
        out_file.write('param epsilon = 0.0001;\n')
        out_file.close()

    #a very large positive number, used for linearization
    def output_M(self, out_fname):
        out_file=open(out_fname, 'a')
        out_file.write('#####Declaration of parameters\n')
        out_file.write('param M = 999999999;\n')
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

    def output_pair_latency_limit(self, out_fname, pair_latency_limit):
        ##upper limit of latency between one pair of tasks
        #param pair_max_latency;
        out_file=open(out_fname, 'a')
        out_file.write('#upper limit of latency between one pair of tasks\n')
        out_str='param pair_max_latency:= {0};\n' .format(pair_latency_limit)
        out_file.write(out_str)
        out_file.close()

    def read_path_gravity_file(self, gravity_file, path_gravity_info):
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
            #2.1 store the path, gravity ratio infor in path_gravity_info
            path_gravity_info.append({'flowNum': path_flow_num, 'path': path_nodes})
        #print path_gravity_info
    
    def generate_one_path_mapped_tasks(self, path_gravity_info, task_monitor_flow_num, can_assign, task_maps):
        num_tasks = len(task_monitor_flow_num) - 1
        for path_info in path_gravity_info:
            path_flow_num = path_info['flowNum']
            path_nodes = path_info['path']
            #3. get the number of CM tasks per path
            num_path_cm_tasks = random.randint(GeneratePlacementData.NUM_CM_TASK_RAND_MIN, GeneratePlacementData.NUM_CM_TASK_RAND_MAX)
            for i in range(0, num_path_cm_tasks):
                task1_id = num_tasks + 1
                task2_id = num_tasks + 2
                num_tasks += 2
                #task1_id can be assigned to any nodes along the path
                #task1_id monitors all flows along the path
                can_assign.append(path_nodes)
                task_monitor_flow_num.append(path_flow_num)
                #task2_id can be assigned to any nodes along the path
                #task2_id monitors all flows along the path
                can_assign.append(path_nodes)
                task_monitor_flow_num.append(path_flow_num)
                #add a map of tasks
                task_maps.append((task1_id, task2_id))

    def generate_ecmp_paths_mapped_tasks(self, topoJsonFile, path_gravity_info, task_monitor_flow_num, can_assign, task_maps): 
        """
        1 conditionTask-N measurementTask mapping
        where N is the number of ECMP paths
        use getDisjointPaths() to get disjoint paths between each pair of nodes
        the flow number per sub path_k is calculated as follows:
        1/dist_k / sum{1/dist_i}
        """
        num_tasks = len(task_monitor_flow_num) - 1
        G = DiGraph(topoJsonFile)
        for i in range(1, self.num_nodes+1):
            for j in range(1, self.num_nodes+1):
                #print i, j
                if i == j:
                    continue
                paths = algorithmAPI.getDisjointPaths(G, str(i), str(j))
                #ignore one path (same to generate_one_path_mapped_tasks)
                if len(paths) <= 1:
                    continue
                
                #1. get now_path_flow_num for the pair of <i, j>
                #the first path is the shortest path, the same stored for each pair of nodes stored in path_gravity_info
                shortest_path_nodes = paths[0]['path']
                #print 'shortest_path_nodes', shortest_path_nodes
                now_path_flow_num = 0
                for path_gravity in path_gravity_info:
                    path_nodes = path_gravity['path']
                    path_flow_num = path_gravity['flowNum']
                    if len(path_nodes) != len(shortest_path_nodes):
                        continue
                    ii = 0
                    for node in path_nodes:
                        #path_nodes is in format of 'x', while shortest_path_nodes is in format of (int)x
                        if node != int(shortest_path_nodes[ii]):
                            break
                        ii+=1
                    if ii == len(path_nodes):
                        now_path_flow_num = path_flow_num
                        break
                #print i, j, now_path_flow_num
                if now_path_flow_num == 0:
                    continue

                #2. candidate nodes of condition tasks
                # the intersected nodes of all paths
                intersect_set = Set(paths[0]['path'])
                # sum{1/dist_i}
                sum_cost = 0
                for path in paths:
                    now_set = Set(path['path'])
                    intersect_set = intersect_set.intersection(now_set)
                    sum_cost += 1.0 / path['cost']
                ctask_candidate_nodes = list(intersect_set)
                #print 'ctask candidate nodes:', ctask_candidate_nodes
                #3. candidate nodes of measurement tasks <disjoint nodes of each subpath>
                #4. path_flow_num of measurement tasks <ratio of now_path_flow_num of each subpath>
                mtask_subpaths_info = []
                for one_path in paths:
                    #3    
                    candidate_set = Set(one_path['path'])
                    one_set = Set(one_path['path'])
                    for sec_path in paths:
                        if sec_path == one_path:
                            continue
                        sec_set = Set(sec_path['path'])
                        candidate_set = candidate_set.difference(one_set.intersection(sec_set))
                    
                    #4
                    one_path_flow_num_ratio = 1.0 / one_path['cost'] / sum_cost
                    one_path_flow_num = now_path_flow_num * one_path_flow_num_ratio
                    mtask_subpaths_info.append({'flowNum': int(one_path_flow_num), 'nodes': list(candidate_set)})
                if len(mtask_subpaths_info) > 2:
                    print 'mtask candidate nodes:', mtask_subpaths_info

                #5. generate mapped tasks for node <i, j> pair
                num_path_cm_tasks = random.randint(GeneratePlacementData.NUM_CM_TASK_RAND_MIN, GeneratePlacementData.NUM_CM_TASK_RAND_MAX)
                num_ecmp_paths = len(mtask_subpaths_info)
                for ii in range(0, num_path_cm_tasks):
                    #condition task, which monitors all flows of paths between <i,j>
                    num_tasks += 1
                    condition_task_id = num_tasks
                    can_assign.append([int(x) for x in ctask_candidate_nodes])
                    task_monitor_flow_num.append(now_path_flow_num)

                    for sub_path in mtask_subpaths_info:
                        #measurement task, which monitors the flows of sum path between <i,j>
                        one_path_flow_num = sub_path['flowNum']
                        one_path_disjont_nodes = [int(x) for x in sub_path['nodes']]
                        #print one_path_disjont_nodes
                        num_tasks += 1
                        measure_task_id = num_tasks
                        can_assign.append(one_path_disjont_nodes)
                        task_monitor_flow_num.append(one_path_flow_num)

                        #add a map of <condition_task, measure_task>
                        task_maps.append((condition_task_id, measure_task_id))

    def output_mapped_tasks(self, out_fname, task_monitor_flow_num, can_assign, task_maps):        
        num_tasks = len(task_monitor_flow_num)-1
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
        num_mapped_paris = len(task_maps)
        out_file.write('#number of matched tasks\n')
        out_file.write('param num_match = {0};\n' .format(num_mapped_paris))
        
        out_file.write('#num_match * 2 matrix, matched tasks\n')
        out_file.write('param matched_tasks :\n')
        out_file.write('  1 2:=\n')
        for i in range(num_mapped_paris):
            out_file.write('{0} {1} {2}\n' .format(i+1, task_maps[i][0], task_maps[i][1]))
        out_file.write(';\n')

        #5. mapped tasks in another format
        candidate_tasks_match = [[0 for x in range(num_tasks + 1)] for x in range(num_tasks+1)]
        for i in range(num_mapped_paris):
            first_taskid = task_maps[i][0]
            second_taskid = task_maps[i][1]
            candidate_tasks_match[first_taskid][second_taskid] = 1
            candidate_tasks_match[second_taskid][first_taskid] = 1
        out_file.write('#candidate mapping information of tasks\n')
        out_file.write('param candidate_tasks_match :\n')
        out_str = " "
        for i in range(1, num_tasks+1):
            out_str += " {0}" .format(i)
        out_file.write(out_str+':=\n')
        for i in range(1, num_tasks+1):
            out_str = "{0}" .format(i)
            for j in range(1, num_tasks+1):
                out_str += " {0}" .format(candidate_tasks_match[i][j])
            out_file.write(out_str+'\n')
        out_file.write(';\n')
        out_file.close()

        print 'generate_mapped_tasks: {0} pairs of tasks generated\n' .format(num_mapped_paris)

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print "usage: python new_generate_placement_data.py placement.dat topo_weight_file topo_weight_json_file gravity_file times_num_flow[1,2,4,8,16] pair_latency_limit\n"
        exit(0)
    placement_fname = sys.argv[1]
    topo_fname = sys.argv[2]
    topo_json_fname = sys.argv[3]
    gravity_file = sys.argv[4]
    times_num_flow = int(sys.argv[5])
    pair_latency_limit = int(sys.argv[6])

    #remove existing output file
    commands.getstatusoutput('rm {0}' .format(placement_fname))

    random.seed(time.time())

    generator = GeneratePlacementData()
    #alpha
    generator.output_alpha(placement_fname)
    #-------node and topology information-------#
    #read topology and initialize
    generator.read_graph_topo(topo_fname)
    generator.init_graph_other_param(times_num_flow)
    #latency matrix
    generator.get_latency_between_nodes()
    generator.output_latency_to_file(placement_fname)
    #maximum flow per node
    generator.output_maximum_flows_per_node(placement_fname)

    #pair_latency_limit
    generator.output_pair_latency_limit(placement_fname, pair_latency_limit)

    #-------task and mapping information--------#
    #generate mapped tasks from gravity model data
    path_gravity_info = []
    task_monitor_flow_num = [0]
    can_assign = [[]]
    task_maps = []
    generator.read_path_gravity_file(gravity_file, path_gravity_info)
    generator.generate_one_path_mapped_tasks(path_gravity_info, task_monitor_flow_num, can_assign, task_maps)
    generator.generate_ecmp_paths_mapped_tasks(topo_json_fname, path_gravity_info, task_monitor_flow_num, can_assign, task_maps)
    generator.output_mapped_tasks(placement_fname, task_monitor_flow_num, can_assign, task_maps)

    #a very small positive real number, used for linearization.
    generator.output_epsilon(placement_fname)

    #a very large positive number, used for linearization
    generator.output_M(placement_fname)

    print 'new_generate_placement_data succeeded\n'
