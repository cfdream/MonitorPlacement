#1. cdf of flow number monitored by candidate tasks
assigned_tasks=`wc -l input.dat | awk '{print $1}'`
echo $assigned_tasks
awk '{print $2}' input.dat | sort -n > temp
awk -v x=$assigned_tasks 'BEGIN{i=0}{i++; print $1, i/x}' temp > input.dat.FlowNumCDF

#2. cdf of flow number monitored by tasks assigned by placement_max_assigned_pairs
#input: input.dat placement_max_assigned_pairs.output
#input.dat: keep matrix task_monitor_flow_num
#placement_max_assigned_pairs.output: run placement_max_assigned_pairs.run for one time, and just keep matrix g
awk '{if(NF==12){for (i=2;i<=12;i++){if($i==1){a[$1]=1}}} else {if(a[$1]==1){print $2}}}' placement_max_assigned_pairs.output input.dat | sort -n > temp
assigned_tasks=`wc -l temp | awk '{print $1}'`
echo $assigned_tasks
awk -v x=$assigned_tasks 'BEGIN{i=0}{i++; print $1, i/x}' temp > placement_max_assigned_pairs.output.assignedTasksFlowNumCDF

#3. cdf of flow number monitored by tasks assigned by greedy_algorithm 
#input: greedy_algorithm.output
#print flow_num of assigned tasks
assigned_tasks=`wc -l greedy_algorithm.output | awk '{print $1}'`
echo $assigned_tasks
awk -v x=$assigned_tasks 'BEGIN{i=0}{i++; print $1, i/x}' greedy_algorithm.output > greedy_algorithm.output.assignedTasksFlowNumCDF

rm temp
