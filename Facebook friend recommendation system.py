# -*- coding: utf-8 -*-
"""21181_samuel_code

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qCIb_RrgA-pf0hit4N83HuLJwSH-51iS
"""

import pandas as pd
import numpy as np
import networkx as nx
#import operator
#from sklearn.cluster import KMeans
from matplotlib.pyplot import figure
from scipy.linalg import eigh
import matplotlib.pyplot as plt
import random
import seaborn as sns
import time

def import_facebook_data(file_path):

    edges = set()

    with open(file_path, "r") as file:
        for line in file:
          node1, node2 = map(int, line.strip().split())
          edges.add((node1, node2))

    return np.array(list(edges))

def import_bitcoin_data(file_path):
  data = pd.read_csv(file_path, usecols=[0, 1])
  return np.unique(data.values, axis=0)

def plot_fiedler_vector(fiedler_vector):

  plt.scatter(range(len(fiedler_vector)), fiedler_vector)
  plt.xlabel('Node Index')
  plt.ylabel('Fiedler Vector Value')
  plt.title('Fiedler Vector Scatterplot')
  plt.show()

def create_adj_mat(edges):
    nodes = set()  # Set to store unique nodes
    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[1])

    num_nodes = len(nodes)
    node_to_index = {node: i for i, node in enumerate(nodes)}
    adjacency_matrix = np.zeros((num_nodes, num_nodes), dtype=int)

    for edge in edges:
        node1, node2 = edge
        node1 = node_to_index[node1]
        node2 = node_to_index[node2]
        adjacency_matrix[node1][node2] = 1
        adjacency_matrix[node2][node1] = 1

    return adjacency_matrix

def createSortedAdjMat(graph_part, nodes_connectivity_list_fb):

  adjacency_matrix = create_adj_mat(nodes_connectivity_list_fb)
  #for facebook data
  #sorted_indices = graph_part[:,0].astype(int)
  #for bitcoin dataset
  sorted_indices = np.argsort(graph_part[:,1].astype(int))
  sorted_adjacency_matrix = adjacency_matrix[sorted_indices][:, sorted_indices]
  """
  plt.figure(figsize=(8, 6))
  plt.spy(sorted_adjacency_matrix, markersize=20, marker='s')

  plt.xlabel("Nodes")
  plt.ylabel("Nodes")
  plt.title("Adjacency Matrix Heatmap")"""


  sns.set()
  plt.figure(figsize=(8, 6))
  #plt.spy(sorted_adjacency_matrix, markersize=20, marker='s')
  sns.heatmap(sorted_adjacency_matrix, cmap="YlGnBu")

# Add labels and title
  plt.xlabel("Nodes")
  plt.ylabel("Nodes")
  plt.title("Adjacency Matrix Heatmap")

# Show the plot
  plt.show()


  return sorted_adjacency_matrix

def visualise_graph(data, adjacency_matrix):
  G = nx.Graph(adjacency_matrix)
  sorted_indices = np.argsort(data[:, 0])
  sorted_data = data[sorted_indices]
  community_assignments = sorted_data[:,1]

# Generate a color map for communities dynamically
  unique_communities = set(community_assignments)
  #print(unique_communities)
  community_colors = {community: "#" + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)) for community in unique_communities}

# Create a list of node colors based on community ID
  node_colors = [community_colors[community_assignments[node]] for node in G.nodes]

# Draw the graph with node colors based on communities
  pos = nx.spring_layout(G)  # You can choose different layout algorithms
  nx.draw(G, pos, with_labels=False, node_color=node_colors)
  plt.show()

def spectralDecomp_OneIter(edges):
    nodes = set()  # Set to store unique nodes
    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[1])

    num_nodes = len(nodes)
    node_to_index = {node: i for i, node in enumerate(nodes)}
    adjacency_matrix = np.zeros((num_nodes, num_nodes), dtype=int)

    for edge in edges:
        node1, node2 = edge
        node1 = node_to_index[node1]
        node2 = node_to_index[node2]
        adjacency_matrix[node1][node2] = 1
        adjacency_matrix[node2][node1] = 1


    degree_matrix = np.diag(np.sum(adjacency_matrix, axis=1))
    laplacian_matrix = degree_matrix - adjacency_matrix

    eigenvalues, eigenvectors = eigh(laplacian_matrix)

    sorted_indices = np.argsort(eigenvalues)
    sorted_eigenvectors = eigenvectors[:, sorted_indices]

    # Select the second smallest eigenvalue and its corresponding eigenvector
    second_smallest_eigenvalue = eigenvalues[1]
    second_smallest_eigenvector = sorted_eigenvectors[:, 1]
    #print(second_smallest_eigenvalue)
    #print(second_smallest_eigenvector)

    partition = [1 if component >= 0 else 0 for component in second_smallest_eigenvector]
    part1_min = 1e9
    part2_min = 1e9
    nodes_list = list(node_to_index.keys())
    for i,part in enumerate(partition):
      if(part == 0):
          part1_min = min(part1_min, nodes_list[i])

      elif(part == 1):
          part2_min = min(part2_min, nodes_list[i])

    graph_partition = np.empty((num_nodes,2))

    for i,part in enumerate(partition):
      if(part == 0):
        graph_partition[i] = [nodes_list[i], int(part1_min)]
      else:
        graph_partition[i] = [nodes_list[i], int(part2_min)]

    return np.sort(second_smallest_eigenvector),adjacency_matrix,graph_partition

def spectralDecomposition(edges):
  start_time = time.time()

  fiedler,adjacency_matrix, graph_part = spectralDecomp_OneIter(edges)
  #print(np.shape(graph_part))
  graph_part_1 = graph_part
  con_dif = np.diff(fiedler.reshape(-1))
  con_max = np.max(con_dif)
  dev = np.std(fiedler)
  mod = np.mean(con_dif)
  #if con_max < mod:
    #return graph_part
  for i in range(3):
    parts = np.unique(graph_part[:,1])
    all_partitions = []
    #flag = 0
    for i in parts:
      indices = np.where(graph_part[:,1] == i)
      nodes = set(graph_part[indices][:,0])
      edges2 = []
      for edge1,edge2 in edges:
        if(edge1 in nodes and edge2 in nodes):
          edges2.append((edge1,edge2))

      fiedler_vec,_, temp = spectralDecomp_OneIter(np.array(edges2))
      all_partitions.append(temp)
      #print(np.shape(temp))
      con_dif = np.diff(fiedler.reshape(-1))
      con_max = np.max(con_dif)
      dev = np.std(fiedler)
      mod = np.mean(con_dif)
      #if con_max < 1.5*mod:
        #return np.concatenate(all_partitions)
    combined_array = np.concatenate(all_partitions)
    graph_part = combined_array

  #print(np.unique(graph_part[:,1]))
  if(len(graph_part_1) > len(graph_part)):
      set_difference = np.setdiff1d(graph_part_1[:,0], graph_part[:,0])
      indices = np.where(np.isin(graph_part_1[:, 0], set_difference))
      result_array = graph_part_1[indices]
      #print(np.shape(result_array))
  #combined_array.append(result_array)
  #graph_part = np.concatenate(combined_array)
  #graph_part = combined_array
      lis = []
      lis.append(graph_part)
      lis.append(result_array)
      graph_part = np.concatenate(lis)

  print('Graph Visualisation for multiple clusters\n')
  visualise_graph(graph_part, adjacency_matrix)
  end_time = time.time()

  elapsed_time = end_time - start_time
  print("Elapsed time:", elapsed_time, "seconds")

  return graph_part

def compute_modularity_gain_merge(node_idx, community_label, community_labels, node_degrees, adjacency_matrix_norm):
    community_nodes = np.where(community_labels == community_label)[0]
    total_degree_community = sum(node_degrees[node] for node in community_nodes)
    k_i_in = 2 * np.sum(adjacency_matrix_norm[node_idx, community_nodes])
    k_i = node_degrees[node_idx]
    modularity_gain_merge = k_i_in - 2 * total_degree_community * k_i
    return modularity_gain_merge

def compute_modularity_gain_demerge(node_idx, community_labels, node_degrees, adjacency_matrix_norm):
    C = community_labels[node_idx]
    community_nodes = np.where(community_labels == C)[0]
    total_degree_community = sum(node_degrees[node] for node in community_nodes)
    k_i_out = 2 * np.sum(adjacency_matrix_norm[node_idx, community_nodes])
    k_i = node_degrees[node_idx]
    modularity_gain_demerge = 2 * k_i * total_degree_community - 2 * k_i ** 2 - k_i_out
    return modularity_gain_demerge

def compute_modularity(communities, node_degrees, adjacency_matrix_norm):
    unique_communities = np.unique(communities)
    Q = 0
    for C in unique_communities:
        community_nodes = np.where(communities == C)[0]
        sigma_total = sum(node_degrees[node] for node in community_nodes)
        sigma_in = np.sum(adjacency_matrix_norm[np.ix_(community_nodes, community_nodes)])
        Q += sigma_in - sigma_total ** 2
    return Q

def louvain_one_iter(edges):
    start_time = time.time()

    nodes = set()  # Set to store unique nodes

    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[1])

    num_nodes = len(nodes)
    node_to_index = {node: i for i, node in enumerate(nodes)}
    index_to_node = {i: node for i,node in enumerate(nodes)}
    adjacency_matrix = np.zeros((num_nodes, num_nodes), dtype=int)

    for edge in edges:
        node1, node2 = edge
        node1 = node_to_index[node1]
        node2 = node_to_index[node2]
        adjacency_matrix[node1][node2] = 1
        adjacency_matrix[node2][node1] = 1

    adj_norm = adjacency_matrix/(2*len(edges))
    degree = np.sum(adj_norm,axis = 1)

    neighbours = []
    for i in range(num_nodes):
        neighbours.append(np.where(adj_norm[i]!=0)[0])

    communities = np.arange(num_nodes)
    arr = np.arange(num_nodes)

            #np.random.shuffle(arr)
    for i in arr:
                neighbour_communities = np.unique(communities[neighbours[i]])
                Q_demerge = compute_modularity_gain_demerge(i,communities, degree, adj_norm)
                maxQ = 0
                best_community = communities[i]
                for j in neighbour_communities:
                    if j == communities[i]:
                        continue
                    Q_merge = compute_modularity_gain_merge(i,j,communities,degree,adj_norm)
                    delta_Q = Q_demerge + Q_merge
                    if delta_Q > maxQ:
                        maxQ = delta_Q
                        best_community = j
                #print("Iter: ",iteration, " node_i: ",i," merging_com: ", j," Q_demerge: ",Q_demerge, "Q_merge: ",Q_merge, " Q: ",delta_Q)
                if maxQ > 0 and best_community != communities[i]:
                    #print("Node: ",i," is changed from ",self.communities[i]," to ",best_community)
                    communities[i] = best_community

    print(len(np.unique(communities)),compute_modularity(communities,degree,adj_norm))
    graph_part = np.empty((num_nodes,2))

    for i,val in enumerate(communities):
        graph_part[i] = [index_to_node[i],val]

    visualise_graph(graph_part,adjacency_matrix)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Elapsed time for Louvain:", elapsed_time, "seconds")



    return graph_part

import numpy as np

if __name__ == "__main__":

    ############ Answer qn 1-4 for facebook data #################################################

    nodes_connectivity_list_fb = import_facebook_data("/content/facebook_combined.txt")


    fielder_vec_fb, adj_mat_fb, graph_partition_fb = spectralDecomp_OneIter(nodes_connectivity_list_fb)
    #for single iteration I had to do it in main since it is being called multiple times in spectral decomp
    plot_fiedler_vector(fielder_vec_fb)
    print('The following is Graph visualisation for spectral One iteration\n')
    visualise_graph(graph_partition_fb, adj_mat_fb)
    print('The following is Adjacency Matrix sorted according to fiedler vector using both seaborn and plt\n')
    createSortedAdjMat(graph_partition_fb, nodes_connectivity_list_fb)



    graph_partition_fb = spectralDecomposition(nodes_connectivity_list_fb)


    clustered_adj_mat_fb = createSortedAdjMat(graph_partition_fb, nodes_connectivity_list_fb)

    graph_partition_louvain_fb = louvain_one_iter(nodes_connectivity_list_fb)


    ############ Answer qn 1-4 for bitcoin data #################################################
    # Import soc-sign-bitcoinotc.csv
    nodes_connectivity_list_btc = import_bitcoin_data("/content/soc-sign-bitcoinotc (1).csv")

    # Question 1
    fielder_vec_btc, adj_mat_btc, graph_partition_btc = spectralDecomp_OneIter(nodes_connectivity_list_btc)
    #for single iteration I had to do it in main since it is being called multiple times in spectral decomp
    plot_fiedler_vector(fielder_vec_btc)
    print('The following is Graph visualisation for spectral One iteration\n')
    visualise_graph(graph_partition_btc, adj_mat_btc)
    print('The following is Adjacency Matrix sorted according to fiedler vector\n')
    createSortedAdjMat(graph_partition_btc, nodes_connectivity_list_btc)

    # Question 2
    graph_partition_btc = spectralDecomposition(nodes_connectivity_list_btc)

    # Question 3
    clustered_adj_mat_btc = createSortedAdjMat(graph_partition_btc, nodes_connectivity_list_btc)

    # Question 4
    graph_partition_louvain_btc = louvain_one_iter(nodes_connectivity_list_btc)

