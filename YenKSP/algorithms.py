#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  algorithms.py
#  
#  Copyright 2012 Kevin R <KRPent@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# 
from operator import itemgetter
from prioritydictionary import priorityDictionary
from graph import DiGraph

## @package YenKSP
# Computes K-Shortest Paths using Yen's Algorithm.
#
# Yen's algorithm computes single-source K-shortest loopless paths for a graph 
# with non-negative edge cost. The algorithm was published by Jin Y. Yen in 1971
# and implores any shortest path algorithm to find the best path, then proceeds 
# to find K-1 deviations of the best path.

## Computes K paths from a source to a sink in the supplied graph.
#
# @param graph A digraph of class Graph.
# @param start The source node of the graph.
# @param sink The sink node of the graph.
# @param K The amount of paths being computed.
#
# @retval [] Array of paths, where [0] is the shortest, [1] is the next 
# shortest, and so on.
#
def ksp_yen(graph, node_start, node_end, max_k=2):
    distances, previous = dijkstra(graph, node_start)
    A = [{'cost': distances[node_end], 
          'path': path(previous, node_start, node_end)}]
    B = []
    if not A[0]['path']: return A
    
    for k in range(1, max_k):
        #for i in range(0, len(A[-1]['path']) - 1):
        for i in range(len(A[-1]['path']) - 2, -1, -1):
            node_spur = A[-1]['path'][i]
            path_root = A[-1]['path'][:i+1]
            #print node_spur, path_root
            
            #first kind of remove
            edges_removed = []
            for path_k in A:
                curr_path = path_k['path']
                if len(curr_path) > i and path_root == curr_path[:i+1]:
                    cost = graph.remove_edge(curr_path[i], curr_path[i+1])
                    if cost == -1:
                        continue
                    edges_removed.append([curr_path[i], curr_path[i+1], cost])
            #second kind of remove
            for j in range(len(path_root)-1):
                node = path_root[j]
                #remove all edges connecting to j
                for neighbor in graph[node]:
                    cost = graph.remove_edge(node, neighbor)
                    if cost == -1:
                        continue
                    edges_removed.append([node, neighbor, cost])

            path_spur = dijkstra(graph, node_spur, node_end)
            
            if path_spur['path']:
                path_total = path_root[:-1] + path_spur['path']
                dist_total = distances[node_spur] + path_spur['cost']
                potential_k = {'cost': dist_total, 'path': path_total}
           
                #print path_total
                if not (potential_k in B):
                    B.append(potential_k)
            
            for edge in edges_removed:
                graph.add_edge(edge[0], edge[1], edge[2])
        
        if len(B):
            B = sorted(B, key=itemgetter('cost'))
            A.append(B[0])
            B.pop(0)
        else:
            break
    print "end ksp_yen"
    return A

def ksp_xuemei(graph, node_start, node_end):
    distances, previous = dijkstra(graph, node_start)
    A = [{'cost': distances[node_end], 
          'path': path(previous, node_start, node_end)}]
    
    if not A[0]['path']: return A
    
    shortestPath = A[0]['path']
    #print shortestPath
    numMidNodes = len(shortestPath) - 2
    if numMidNodes > 0:
        for i in range(pow(2, numMidNodes)-1, 0, -1):
            #try to remove each combination of middles nodes in shortestPath
            toRemoveNodes = []
            flagNum = i
            kthNode = 1 
            while flagNum > 0:
                if flagNum & 1:
                    #remove the node
                    toRemoveNodes.append(shortestPath[kthNode])
                flagNum = flagNum >> 1
                kthNode += 1

            #remove edges connected to toRemoveNodes
            edges_removed = []
            #print toRemoveNodes
            for toRemoveNode in toRemoveNodes:
                #remove all edges connecting to j
                for neighbor in graph[toRemoveNode]:
                    cost = graph.remove_edge(toRemoveNode, neighbor)
                    if cost == -1:
                        continue
                    edges_removed.append([toRemoveNode, neighbor, cost])

            #dijkstra to get shortest path
            path_spur = dijkstra(graph, node_start, node_end)
            if path_spur['path']:
                A.append(path_spur)

            #restore remove edges
            for edge in edges_removed:
                graph.add_edge(edge[0], edge[1], edge[2])
    else:
        #shortest path is node_start=>node_end
        #no other paths should be added, as shortest_path&other_path = [node_start, node_end]
        pass

    A = sorted(A, key=itemgetter('cost'))
    return A

## Computes the shortest path from a source to a sink in the supplied graph.
#
# @param graph A digraph of class Graph.
# @param node_start The source node of the graph.
# @param node_end The sink node of the graph.
#
# @retval {} Dictionary of path and cost or if the node_end is not specified,
# the distances and previous lists are returned.
#
def dijkstra(graph, node_start, node_end=None):
    distances = {}      
    previous = {}       
    Q = priorityDictionary()
    
    for v in graph:
        distances[v] = graph.INFINITY
        previous[v] = graph.UNDEFINDED
        Q[v] = graph.INFINITY
    
    distances[node_start] = 0
    Q[node_start] = 0
    
    for v in Q:
        if v == node_end: break

        for u in graph[v]:
            cost_vu = distances[v] + graph[v][u]
            
            if cost_vu < distances[u]:
                distances[u] = cost_vu
                Q[u] = cost_vu
                previous[u] = v

    if node_end:
        return {'cost': distances[node_end], 
                'path': path(previous, node_start, node_end)}
    else:
        return (distances, previous)

## Finds a paths from a source to a sink using a supplied previous node list.
#
# @param previous A list of node predecessors.
# @param node_start The source node of the graph.
# @param node_end The sink node of the graph.
#
# @retval [] Array of nodes if a path is found, an empty list if no path is 
# found from the source to sink.
#
def path(previous, node_start, node_end):
    route = []

    node_curr = node_end    
    while True:
        route.append(node_curr)
        if previous[node_curr] == node_start:
            route.append(node_start)
            break
        elif previous[node_curr] == DiGraph.UNDEFINDED:
            return []
        
        node_curr = previous[node_curr]
    
    route.reverse()
    return route
