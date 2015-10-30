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
#whether module i assigned to node j
var g {1..m, 1..n} binary;
#whether task i is placed or not
var a {1..kk} binary;

#latency between selector and monitor pairs, for calculating latency
var selector_monitor_map_latency {s in 1..m, t in 1..m} = selector_monitor_map[s,t] * (sum{i in 1..n, j in 1..n} (g[s,i]*g[t,j]*latency[i,j]));

####---------Declaration of objective function---------####
#objective1: maximize the number of assigned pairs
maximize max_assigned_tasks: sum {k in 1..kk} a[k];

####---------Declaration of Constrains---------####
#1. module_s must be can be assigned to node_i
subject to must_can_assign {s in 1..m, i in 1..n} : g[s,i] <= can_assign[s,i];
#2. module_s can be assigned only once
subject to module_assigned_once {s in 1..m} : sum{i in 1..n} g[s,i] <= 1;
#3. resource constraint in node i
subject to node_capacity_limit {i in 1..n} : sum{s in 1..m} g[s,i] * module_monitor_flow_num[s] <= max_node_flows[i];
#4. a[kk] <= 1 only when all its modules are assigned
subject to all_modules_assigned {k in 1..kk}: num_modules_task_has[k] * a[k] <= sum {s in 1..m, i in 1..n} (task_has_module[k,s]*g[s,i]);
#5. latency constraint: the latency between one assigned pair should <= pair_max_latency
subject to pair_latency_limit {s in 1..m, t in 1..m, i in 1..n, j in 1..n} : selector_monitor_map[s,t] * latency[i,j] <= pair_max_latency + M * (2-g[s,i]-g[t,j]);

