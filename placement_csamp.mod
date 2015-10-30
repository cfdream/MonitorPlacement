####----------Declaration of parameters----------####
#number of nodes
param n;
#latency matrix
param latency {1..n, 1..n};
#maximum number of flows each node can hold
param max_node_flows {1..n};

#number of modules
param m;
#number of flows required to be monitored by modules
param module_monitor_flow_num {1..m};
#whether module can be assigned to nodes
param can_assign {1..m, 1..n};

#number of tasks
param kk;
#number of modules each task has
param num_modules_task_has {1..kk};
#whether task k has module s
param task_has_module {1..kk, 1..m};
#whether module s and t are one selector and monitor of one task individually
#if s is a selector and t is a monitor of one task, [s,t] = 1; otherwise [s,t] = 0
param selector_monitor_map {1..m, 1..m};

# lantency constraint between mapped modules
param pair_max_latency;

#a very large positive number, used for linearization
param M;

####----------Declaration of variables----------####
#whether task i assigned to node j
var g {1..m, 1..n} binary;

#latency between selector and monitor pairs, for calculating latency
var selector_monitor_map_latency {s in 1..m, t in 1..m} = selector_monitor_map[s,t] * (sum{i in 1..n, j in 1..n} (g[s,i]*g[t,j]*latency[i,j]));

#whether task assigned or not
var a {k in 1..kk} = (if num_modules_task_has[k] = sum {s in 1..m, i in 1..n} (task_has_module[k,s]*g[s,i]) then 1 else 0 );

####---------Declaration of objective function---------####
#objective1: maximize the number of assigned pairs
maximize max_assigned_pairs: sum {s in 1..m} sum {i in 1..n} g[s,i];

####---------Declaration of Constrains---------####
#1. task_s must be can be assigned to node_i
subject to must_can_assign {s in 1..m, i in 1..n} : g[s,i] <= can_assign[s,i];
#2. task_s can be assigned only once
subject to task_assigned_once {s in 1..m} : sum{i in 1..n} g[s,i] <= 1;
#3. resource constraint in node i
subject to node_capacity_limit {i in 1..n} : sum{s in 1..m} g[s,i] * module_monitor_flow_num[s] <= max_node_flows[i];
