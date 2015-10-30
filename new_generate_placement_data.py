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
    NUM_CM_TASK_RAND_MAX = 8

    ALPHA = 0.1
    CANDIDATE_NODES_FOR_ONE_TASK = 1

    def __init__(self, placement_fname, topo_fname, topo_json_fname, gravity_file):
        self.num_nodes = 0
        self.graph = {}     #connection list
        self.latency_graph = []
        self.graph_flow_num = 0
        self.module_monitor_flow_num = []
        self.can_assign = []
        self.task_info_list = [] #each element (taskid, selector_moduleid, [monitor_moduleid])
        self.placement_fname = placement_fname
        self.topo_fname = topo_fname
        self.topo_json_fname = topo_json_fname
        self.gravity_file = gravity_file

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
        
        #calculate flow number in the graph, based on the method in CSAMP
        self.graph_flow_num = 1.0 * \
            self.num_nodes / GeneratePlacementData.INTERNET2_SWITCH_NUM \
            * GeneratePlacementData.INTERNET2_FLOW_NUM 

        return self.num_nodes


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

    def output_nodes_info_to_file(self, out_fname): 
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

    #a very large positive number, used for linearization
    def output_M(self, out_fname):
        out_file=open(out_fname, 'a')
        out_file.write('#####Declaration of parameters\n')
        out_file.write('param M = 999999999;\n')
        out_file.close()

    def output_maximum_flows_per_node(self, out_fname):
        #maximum number of flows each node can run
        out_file=open(out_fname, 'a')
        out_file.write('#maximum number of flows each node can run\n')
        out_str='param max_node_flows :=\n'
        for i in range(1, self.num_nodes+1):
            out_str += '{0} {1} \n' .format(i, GeneratePlacementData.MAX_FLOWS_PER_NODE)
        out_file.write(out_str + ';\n')
        out_file.close()

    def output_pair_latency_limit(self, out_fname):
        ##upper limit of latency between one pair of modules
        #param pair_max_latency;
        out_file=open(out_fname, 'a')
        out_file.write('#upper limit of latency between one pair of modules\n')
        out_str='param pair_max_latency:= {0};\n' .format(self.pair_latency_limit)
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
    
    def generate_one_path_tasks(self, path_gravity_info, task_times, one_selector_x_monitors):
        for ith_path in range(len(path_gravity_info)):
            path_info = path_gravity_info[ith_path]
            #-----for odd path, we generate single path tasks
            ith_path += 1
            if (ith_path % 2) == 0:
                continue

            path_flow_num = path_info['flowNum']
            path_nodes = path_info['path']
            #-----ignore OD pair whose O and D are the same
            if path_nodes[0] == path_nodes[len(path_nodes)-1]:
                continue
            #print path_nodes
            #-----one path has task_times tasks
            for i in range(0, task_times):
                #-----each task only one selector
                selector_id = len(self.module_monitor_flow_num) + 1
                #selector_id monitors all flows along the path
                self.module_monitor_flow_num.append(path_flow_num)
                #selector_id can be assigned to any nodes along the path
                self.can_assign.append(path_nodes)

                monitor_id_list = []
                #-----each task has x monitors
                for ith_monitor in range(one_selector_x_monitors):
                    #one monitor
                    monitor_id = len(self.module_monitor_flow_num) + 1
                    monitor_id_list.append(monitor_id)
                    #monitor_id monitor all flow along the path
                    self.module_monitor_flow_num.append(path_flow_num)
                    #monitor_id can be assigned to any nodes along the path
                    self.can_assign.append(path_nodes)

                #-----add the task info
                task_id = len(self.task_info_list) + 1
                self.task_info_list.append((task_id, selector_id, monitor_id_list))
        print "single path tasks:", len(self.task_info_list), "modules:", len(self.module_monitor_flow_num)

    def generate_multi_paths_tasks(self, path_gravity_info, task_times, one_selector_x_monitors):
        print "num_paths in topology:", len(path_gravity_info)
        for ith_path in range(len(path_gravity_info)):
            path_info = path_gravity_info[ith_path]
            #-----for even path, we generate single path tasks
            if (ith_path % 2) == 1:
                continue

            path_flow_num = path_info['flowNum']
            path_nodes = path_info['path']
            #-----ignore OD pair whose O and D are the same
            if path_nodes[0] == path_nodes[len(path_nodes)-1]:
                continue
            #print path_nodes
            #-----this path has task_times tasks
            for i in range(0, task_times):
                #-----each task only one selector
                selector_id = len(self.module_monitor_flow_num) + 1
                #selector_id monitors all flows along the path
                self.module_monitor_flow_num.append(path_flow_num)
                #selector_id can be assigned to any nodes along the path
                self.can_assign.append(path_nodes)

                #-----each task has x monitors, each on x random other paths
                monitor_id_list = []
                other_path_id_list = []
                for ith_monitor in range(one_selector_x_monitors):
                    #-----get one other path that does not appear in other_path_id_list
                    other_path_id = 0
                    while True:
                        other_path_id = random.randint(0, len(path_gravity_info)-1)
                        if other_path_id in other_path_id_list:
                            continue
                        else:
                            break
                    other_path_id_list.append(other_path_id)
                    #print "two paths:", ith_path, other_path_id

                    #-----get the other path info
                    other_path_info = path_gravity_info[other_path_id]
                    other_path_flow_number = other_path_info['flowNum']
                    other_path_nodes = other_path_info['path']
                    #-----assign one monitor to the path
                    monitor_id = len(self.module_monitor_flow_num) + 1
                    monitor_id_list.append(monitor_id)
                    #monitor_id monitor all flow along the the other path
                    self.module_monitor_flow_num.append(other_path_flow_number)
                    #monitor_id can be assigned to any nodes along the other path
                    self.can_assign.append(other_path_nodes)

                #-----add the task info
                task_id = len(self.task_info_list) + 1
                self.task_info_list.append((task_id, selector_id, monitor_id_list))
        print "multi path tasks:", len(self.task_info_list), "modules:", len(self.module_monitor_flow_num)

    def output_tasks_info_to_file(self, out_fname):        
        out_file=open(out_fname, 'a')

        #-----get number of modules
        num_modules = len(self.module_monitor_flow_num)
        print "num_modules:", num_modules

        #-----get candidate_tasks_match
        selector_monitor_match = [[0 for x in range(num_modules + 1)] for x in range(num_modules+1)]
        for task_info in self.task_info_list:
            selector_id = task_info[1]
            for monitor_id in task_info[2]:
                #print selector_id, monitor_id
                selector_monitor_match[selector_id][monitor_id] = 1
                selector_monitor_match[monitor_id][selector_id] = 1

        #-----output number of modules
        out_file.write('#number of modules\n')
        out_str='param m := {0};\n' .format(num_modules)
        out_file.write(out_str)

        #-----output module_monitor_flow_num
        out_str='param module_monitor_flow_num :=\n'
        for i in range(1, num_modules+1):
            out_str += '{0} {1} \n' .format(i, self.module_monitor_flow_num[i-1])
        out_file.write(out_str + ";\n")

        #-----output can_assign
        out_file.write('#can module i be assigned to node j\n')
        out_file.write('param can_assign :\n')
        out_str = " "
        for i in range(1, self.num_nodes+1):
            out_str += " {0}" .format(i)
        out_file.write(out_str+':=\n')
        #body
        for i in range(1, num_modules+1):
            out_str = "{0}" .format(i)
            for j in range(1, self.num_nodes+1):
                if j in self.can_assign[i-1]:
                    out_str += " 1"
                else:
                    out_str += " 0"
            out_file.write(out_str+'\n')
        out_file.write(';\n')

        #-----output number of tasks
        num_tasks = len(self.task_info_list)
        out_file.write('#number of tasks\n')
        out_str='param kk := {0};\n' .format(num_tasks)
        out_file.write(out_str)
        
        #-----output num_modules_task_has
        out_str='param num_modules_task_has :=\n'
        for i in range(1, num_tasks+1):
            #one selector
            task_num_modules = 1
            #monitor list
            task_num_modules += len(task_info[2])
            out_str += '{0} {1} \n' .format(i, task_num_modules)
        out_file.write(out_str + ";\n")

        #-----output task_has_module
        #param task_has_module {1..kk, 1..m};
        out_file.write('#whether task k has module s\n')
        out_file.write('param task_has_module :\n')
        out_str = ''
        for s in range(1, num_modules+1):
            out_str += " {0}" .format(s)
        out_file.write(out_str+':=\n')
        #body
        for k in range(1, num_tasks+1):
            task_info = self.task_info_list[k-1]
            out_str = "{0}" .format(k)
            for s in range(1, num_modules+1):
                if s == task_info[1] or (s in task_info[2]):
                    out_str += " 1"
                else:
                    out_str += " 0"
            out_file.write(out_str+'\n')
        out_file.write(';\n')

        #-----output selector_monitor_map
        out_file.write('#whether module s and t are one selector and monitor of one task individually\n')
        out_file.write('#if s is a selector and t is a monitor of one task, [s,t] = 1; otherwise [s,t] = 0\n')
        out_file.write('param selector_monitor_map :\n')
        out_str = " "
        for i in range(1, num_modules+1):
            out_str += " {0}" .format(i)
        out_file.write(out_str+':=\n')
        for i in range(1, num_modules+1):
            out_str = "{0}" .format(i)
            for j in range(1, num_modules+1):
                out_str += " {0}" .format(selector_monitor_match[i][j])
            out_file.write(out_str+'\n')
        out_file.write(';\n')
        out_file.close()

        print 'generate_mapped_tasks: {0} tasks, {1} modules\n' .format(num_tasks, num_modules)

    def read_topology_data(self):
        #-------node and topology information-------#
        #read topology
        self.read_graph_topo(self.topo_fname)
        #calculate latency matrix
        self.get_latency_between_nodes()

    def generate_mapped_tasks(self, task_times, one_selector_x_monitors):
        #-------task and mapping information--------#
        #generate mapped tasks from gravity model data
        random.seed(time.time())
        
        path_gravity_info = []
        self.read_path_gravity_file(self.gravity_file, path_gravity_info)
        self.generate_one_path_tasks(path_gravity_info, task_times, one_selector_x_monitors)
        self.generate_multi_paths_tasks(path_gravity_info, task_times, one_selector_x_monitors)

    def assign_varied_variables(self, node_capacity, pair_latency_limit):
        #maximum flow per node
        GeneratePlacementData.MAX_FLOWS_PER_NODE = node_capacity
        #latency constraint
        self.pair_latency_limit = pair_latency_limit

    def output_all_data_to_file(self):
        #-----output nodes
        self.output_nodes_info_to_file(self.placement_fname)

        #-----output varied variables, constant
        #node capacity
        self.output_maximum_flows_per_node(self.placement_fname)
        #pair_latency_limit
        self.output_pair_latency_limit(self.placement_fname)
        #a very large positive number, used for linearization
        self.output_M(self.placement_fname)
        
        #-----output tasks
        self.output_tasks_info_to_file(self.placement_fname)


if __name__ == "__main__":
    if len(sys.argv) != 9:
        print "usage: python new_generate_placement_data.py placement.dat topo_weight_file topo_weight_json_file gravity_file task_times[times to #OD pairs] pair_latency_limit node_capacity one_selector_x_monitors[1,2,3,...]\n"
        exit(0)
    placement_fname = sys.argv[1]
    topo_fname = sys.argv[2]
    topo_json_fname = sys.argv[3]
    gravity_file = sys.argv[4]
    task_times = int(sys.argv[5])
    pair_latency_limit = int(sys.argv[6])
    node_capacity = int(sys.argv[7])
    one_selector_x_monitors = int(sys.argv[8])
    print "pair_latency_limit:", pair_latency_limit, "task_times:", task_times, "one_selector_x_monitors:", one_selector_x_monitors

    commands.getstatusoutput('rm {0}' .format(placement_fname))

    generator = GeneratePlacementData(placement_fname, topo_fname, topo_json_fname, gravity_file)
    generator.read_topology_data()
    generator.generate_mapped_tasks(task_times, one_selector_x_monitors)
    generator.assign_varied_variables(node_capacity, pair_latency_limit)
    generator.output_all_data_to_file()
