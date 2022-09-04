def get_adjacency_list(distance_matrix):
    """Obtém a lista de adjacência do grafo a partir de
       uma matriz de distâncias entre os vértices

    Args:
        distance_matrix (lst): matriz de distâncias

    Returns:
        dict: lista de adjacência (dicionário de listas)
    """

    graph_size = len(distance_matrix)

    adj_list = dict()

    for i in range(graph_size):
        adj_list[i] = list()

    for i in range(graph_size):
        for j in range(graph_size):
            if distance_matrix[i][j] != 0:
                adj_list[i].append(j)

    return adj_list


def igraph_cluster_to_list(d):
    """Converte o retorno da função as_clustering() para
       uma lista de clusters

    Args:
        d (str): string contendo as listas de clusters

    Returns:
        lst: lista contendo os clusters
    """

    set_list = list()

    for i in d:
        set_list.append(i)

    return set_list


def get_path_fitness(v_set, adj_list, distance_matrix):
    """Calcula o valor da soma das arestas contidas entre
       os vértices de um cluster

    Args:
        v_set (lst): cluster
        adj_list (dict): lista de adjacência dos vértices
        distance_matrix (lst): matriz contendo as distâncias entre
                               os vértices

    Returns:
        int: soma das arestas entre os vértices do cluster
    """

    fitness = 0
    visited = list()

    for j in range(len(v_set)):
        current = v_set[j]
        visited.append(current)

        for i in adj_list[current]:
            if (i in v_set) and (current in visited and i in visited):
                fitness += distance_matrix[current][i]
                visited.append(i)

    return fitness