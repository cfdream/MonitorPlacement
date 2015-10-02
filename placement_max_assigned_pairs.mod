#####Declaration of parameters
#number of nodes
param n;
#n*n matrix, latency between nodes
param latency {1..n, 1..n};
#maximum number of flows each node can hold
param max_node_flows {1..n};

#number of tasks
param m;
#number of flows each task monitor
param task_monitor_flow_num {1..m};
#can task i be assigned to task j
param can_assign {1..m, 1..n};

#number of matched tasks
param num_match;
#num_match * 2 matrix, matched tasks
param matched_tasks {1..num_match, 1..2};

#latency constrain
param pair_max_latency;

#####Declaration of variables
#whether task i assigned to node j
var g{1..m, 1..n} binary;
#var g{1..m, 1..n}  integer >=0 <=1;

#####Declaration of objective function
#objective1: maximize the number of pairs of assigned monitors
maximize max_assigned_pairs: sum {k in 1..num_match} sum {i in 1..n} sum {j in 1..n} 
	g[matched_tasks[k,1],i]*g[matched_tasks[k,2],j];

#####Declaration of Constrains
#1. task_i must can be assigned to node_j
subject to must_can_assign {i in 1..m, j in 1..n} : g[i,j] <= can_assign[i,j];
#2. task_i can only be assigned to one node
subject to task_limit {i in 1..m}: sum {j in 1..n} g[i,j] <= 1;
#3. node_j can only monitor at most max_node_flows[j] flows
subject to node_limit {j in 1..n}: sum {i in 1..m} g[i,j] * task_monitor_flow_num[i] <= max_node_flows[j];
