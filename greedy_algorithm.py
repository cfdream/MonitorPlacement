import commands
import sys
import string
import re
import time
import random
from sets import Set
from heapq import heappush, heappop

class GreedyAlgorithm:
    def __init__(self):
        #topology
        self.num_nodes = 0  #node_id starts from 1
        self.latency = [[]]
        self.max_node_flows = [0]
        self.node_used_flows = [0]
        #task
        self.num_tasks = 0  #task_id starts from 1
        self.task_can_assign = [[]]
        self.task_monitor_flow_num = [0]
        self.task_assigned_node = [None]
        #matched tasks
        self.num_match = 0
        self.match_tasks = [[]]
    
    def readFromInput(self, input_fname):
        ##topology
        #self.num_nodes = 0  #node_id starts from 1
        #self.latency = [[]]
        #self.max_node_flows = [0]
        ##task
        #self.num_tasks = 0  #task_id starts from 1
        #self.task_can_assign = [[]]
        #self.task_monitor_flow_num = [0]
        ##matched tasks
        #self.num_match = 0
        #self.match_tasks = []

        round_start_pattern = re.compile("=====time-(\d+) milliseconds=====")
        num_nodes_pattern = re.compile("param n := (\d+);")
        num_tasks_pattern = re.compile("param m := (\d+)")
        num_match_pattern = re.compile('param num_match = (\d+);')

        file=open(input_fname, 'r')
        lines=file.readlines()
        lines=map(lambda x:x[:-1], lines)
        file.close()

        #go through the file to get param
        nodes_infor = False
        task_infor = False
        match_task_info = False
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            match = num_nodes_pattern.match(line)
            if match != None:
                nodes_infor = True
                task_infor = False
                match_task_info = False
                self.num_nodes = int(match.group(1))
                continue
            match = num_tasks_pattern.match(line)
            if match != None:
                nodes_infor = False
                task_infor = True
                match_task_info = False
                self.num_tasks = int(match.group(1))
                continue
            match = num_match_pattern.match(line)
            if match != None:
                nodes_infor = False
                task_infor = False
                match_task_info = True
                self.num_match = int(match.group(1))
                continue
            if nodes_infor:
                #---start nodes information ---
                #self.latency = [[]]
                #self.max_node_flows = [0]
                items = line.split(' ')
                if len(items) == self.num_nodes+1:
                    if items[0] == '':
                        continue
                    #latency information
                    self.latency.append([int(x) for x in items])
                if len(items) == 3:
                    if items[0] == 'param':
                        continue
                    #max_node_flows information
                    self.max_node_flows.append(int(items[1]))
            if task_infor:
                #---start task information---
                #self.num_tasks = 0  #task_id starts from 1
                #self.task_can_assign = [[]]
                #self.task_monitor_flow_num = [0]
                items = line.split(' ')
                if len(items) == self.num_nodes+1:
                    if items[0] == '':
                        continue
                    #task_can_assign
                    self.task_can_assign.append([int(x) for x in items])
                if len(items) == 3:
                    if items[0] == 'param':
                        continue
                    #task_monitor_flow_num
                    self.task_monitor_flow_num.append(int(items[1]))
            if match_task_info:
                #---start match_task_information---
                #self.num_match = 0
                #self.match_tasks = []
                items = line.split(' ')
                if len(items) == 3:
                    if items[0] == '' or items[0]=='param':
                        continue
                    #match_tasks
                    self.match_tasks.append([int(x) for x in items])
        #print self.latency
        #print self.max_node_flows
        #print self.task_can_assign
        #print self.task_monitor_flow_num
        #print self.match_tasks

    def initialOtherParam(self):
        ##topology
        self.node_used_flows = [0]*(self.num_nodes+1)
        ##task
        self.task_assigned_node = [0]*(self.num_tasks+1)
        pass

    def greedyAlgorithm(self):
        ##topology
        #self.num_nodes = 0  #node_id starts from 1
        #self.latency = [[]]
        #self.max_node_flows = [0]
        #self.node_used_flows = [0]
        ##task
        #self.num_tasks = 0  #task_id starts from 1
        #self.task_can_assign = [[]]
        #self.task_monitor_flow_num = [0]
        #self.task_assigned_node = [None]
        ##matched tasks
        #self.num_match = 0
        #self.match_tasks = []
        while True:
            #1. get task_1 with maximum matched_tasks
            #constraints: at least the tasks and one of its matched tasks can be assigned to node (max_node_flows constraint)
            max_valid_mapped_tasks = 0
            taskid_with_max_valid_mapped_tasks = 0
            for taskid in range(1, self.num_tasks+1):
                #1.1 check whether taskid can be assigned to candidate nodes
                task_can_assign = self.task_can_be_assigned(taskid)
                if not task_can_assign:
                    continue
                #1.2 check whether mapped tasks of taskid, record the valid mapped task number
                num_valid_mapped_tasks = 0
                #1.2.1 whether mapped task can assigned or not
                for matchid in range(1, self.num_match+1):
                    map_taskid1 = self.match_tasks[matchid][1]
                    map_taskid2 = self.match_tasks[matchid][2]
                    if map_taskid1 != taskid and map_taskid2 != taskid:
                        #taskid is not included in this pair of tasks
                        continue
                    map_taskid = 0
                    if map_taskid1==taskid:
                        map_taskid = map_taskid2 
                    else:
                        map_taskid = map_taskid1
                    task_can_assign = self.task_can_be_assigned(map_taskid)
                    if not task_can_assign:
                        continue
                    num_valid_mapped_tasks += 1
                #1.2.2 update taskid_with_max_valid_mapped_tasks
                if num_valid_mapped_tasks > max_valid_mapped_tasks:
                    max_valid_mapped_tasks = num_valid_mapped_tasks
                    taskid_with_max_valid_mapped_tasks = taskid

            #if taskid_with_max_valid_mapped_tasks==0, means no mapped tasks can be assigned already, break
            if not taskid_with_max_valid_mapped_tasks:
                break
            #2. randomly select a can_assign location for task_1 
            self.assign_oneCanBeAssignedTask(taskid_with_max_valid_mapped_tasks)
            #3. for matched_tasks, select a near location to task_1 in order to achiever smaller latency
            for matchid in range(1, self.num_match+1):
                map_taskid1 = self.match_tasks[matchid][1]
                map_taskid2 = self.match_tasks[matchid][2]
                if map_taskid1 != taskid_with_max_valid_mapped_tasks and map_taskid2 != taskid_with_max_valid_mapped_tasks:
                    #taskid_with_max_valid_mapped_tasks is not included in this pair of tasks
                    continue
                map_taskid = 0
                if map_taskid1==taskid_with_max_valid_mapped_tasks:
                    map_taskid = map_taskid2 
                else:
                    map_taskid = map_taskid1
                task_can_assign = self.task_can_be_assigned(map_taskid)
                if not task_can_assign:
                    continue
                self.assign_oneCanBeAssignedTask_to_MatchMappedTask(map_taskid, taskid_with_max_valid_mapped_tasks)
                
    def task_can_be_assigned(self, taskid):
        #1.1.1 taskid assigned or not
        if self.task_assigned_node[taskid]:
            #task already assigned
            return False
        #1.1.2 taskid can be assigned to one node or not
        task_can_assign = False
        task_flow = self.task_monitor_flow_num[taskid]
        for nodeid in range(1, self.num_nodes+1):
            if self.task_can_assign[taskid][nodeid]:
                rest_flow_num = self.max_node_flows[nodeid] - self.node_used_flows[nodeid]
                if rest_flow_num >= task_flow:
                    task_can_assign = True
                    break
        return task_can_assign

    def assign_oneCanBeAssignedTask(self, taskid):
        task_flow = self.task_monitor_flow_num[taskid]
        for nodeid in range(1, self.num_nodes+1):
            if self.task_can_assign[taskid][nodeid]:
                rest_flow_num = self.max_node_flows[nodeid] - self.node_used_flows[nodeid]
                if rest_flow_num >= task_flow:
                    #taskid can be assigned to nodeid, and nodeid has the capacity to hold all flows monitored by taskid
                    #assign the taskid
                    self.node_used_flows[nodeid] += task_flow
                    self.task_assigned_node[taskid] = nodeid

    def assign_oneCanBeAssignedTask_to_MatchMappedTask(self, taskid, assigned_map_taskid):
        nodeid_of_assigned_map_taskid = self.task_assigned_node[assigned_map_taskid]
        
        task_flow = self.task_monitor_flow_num[taskid]
        best_nodeid_to_assign = 0
        smallest_latency = 9999999999
        if nodeid_of_assigned_map_taskid <= 0:
            print "Error, nodeid_of_assigned_map_taskid <= 0"
            return
        for nodeid in range(1, self.num_nodes+1):
            if self.task_can_assign[taskid][nodeid]:
                rest_flow_num = self.max_node_flows[nodeid] - self.node_used_flows[nodeid]
                if rest_flow_num >= task_flow:
                    #taskid can be assigned to nodeid, and nodeid has the capacity to hold all flows monitored by taskid
                    latency = self.latency[nodeid][nodeid_of_assigned_map_taskid];
                    if latency < smallest_latency:
                        smallest_latency = latency
                        best_nodeid_to_assign = nodeid

        if best_nodeid_to_assign:
            #assign the taskid
            self.node_used_flows[best_nodeid_to_assign] += task_flow
            self.task_assigned_node[taskid] = best_nodeid_to_assign

    def getAlgorithmResult(self):
        num_assigned_pair = 0
        latency = 0
        for matchid in range(1, self.num_match+1):
            map_taskid1 = self.match_tasks[matchid][1]
            map_taskid2 = self.match_tasks[matchid][2]
            taskid1_node = self.task_assigned_node[map_taskid1]
            taskid2_node = self.task_assigned_node[map_taskid2]
            #self.task_monitor_flow_num = [0]
            if taskid1_node and taskid2_node:
                taskid1_monitor_flow = self.task_monitor_flow_num[taskid1_node]
                taskid2_monitor_flow = self.task_monitor_flow_num[taskid2_node]
                num_assigned_pair += 1
                latency += self.latency[taskid1_node][taskid2_node] * min(taskid1_monitor_flow, taskid2_monitor_flow)
        return (num_assigned_pair, latency)

if __name__ == '__main__':
    if len(sys.argv) !=2:
        print("usage: python greedyAlgorithm.py input.dat")
        exit(0)
    input_fname = sys.argv[1]
    greedyAlgorithm = GreedyAlgorithm()
    greedyAlgorithm.readFromInput(input_fname)
    greedyAlgorithm.initialOtherParam()
    greedyAlgorithm.greedyAlgorithm()
    print greedyAlgorithm.getAlgorithmResult()
    print greedyAlgorithm.max_node_flows
    print greedyAlgorithm.node_used_flows
