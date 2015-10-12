####----------Declaration of parameters----------####
#number of nodes
param n;
#latency matrix
param latency {1..n, 1..n};
#maximum number of flows each node can hold
param max_node_flows {1..n};

#number of tasks
param m;
#number of flows required to be monitored by tasks
param task_monitor_flow_num {1..m};
#whether task can be assigned to nodes
param can_assign {1..m, 1..n};
#candidate mapping information of tasks
param candidate_tasks_match {1..m, 1..m};
#number of matched tasks -- can delete, keep here in order to be compatable with previous input
param num_match;
#num_match * 2 matrix, matched tasks -- can delete, keep here in order to be compatable with previous input
param matched_tasks {1..num_match, 1..2};

# lantency constraint between mapped tasks
param pair_max_latency;

#a very large positive number, used for linearization
param M;

####----------Declaration of variables----------####
#whether task i assigned to node j
var g {1..m, 1..n} binary;
#whether task s and task t are one candidate pair and both are placed successfully
var a {1..m, 1..m} binary;
#binary variable, which is used for linearization
#var u {1..m, 1..m} binary;

####---------Declaration of objective function---------####
#objective1: maximize the number of assigned pairs
maximize max_assigned_pairs: sum {s in 1..m} sum {t in 1..m} a[s,t]/2;

####---------Declaration of Constrains---------####
#1. task_s must be can be assigned to node_i
subject to must_can_assign {s in 1..m, i in 1..n} : g[s,i] <= can_assign[s,i];
#2. task_s can be assigned only once
subject to task_assigned_once {s in 1..m} : sum{i in 1..n} g[s,i] <= 1;
#3. resource constraint in node i
subject to node_capacity_limit {i in 1..n} : sum{s in 1..m} g[s,i] * task_monitor_flow_num[s] <= max_node_flows[i];
#4. a[s,t] can be 1 only when task s and task t are a candidate pair
subject to candidate_pair_limit {s in 1..m, t in 1..m} : a[s,t] <= candidate_tasks_match[s,t];
#5. a[s,t] <= 1 only when task s and t are assigned
subject to both_tasks_assigned_1 {s in 1..m, t in 1..m} : 2 * a[s,t] <= (sum {i in 1..n} g[s,i] + sum {j in 1..n} g[t,j]);
#6. latency constraint: the latency between one assigned pair should <= pair_max_latency
subject to pair_latency_limit_1 {s in 1..m, t in 1..m, i in 1..n, j in 1..n} : a[s,t] * latency[i,j] <= pair_max_latency + M * (2-g[s,i]-g[t,j])
