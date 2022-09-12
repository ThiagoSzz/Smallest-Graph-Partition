import igraph as ig


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


def generate_graph(type, should_plot):
    """Gera um grafo com n_nodes vértices e n_children filhos por vértice

    Args:
        type (str): tipo de grafo a ser gerado
                    possíveis valores: https://igraph.org/c/doc/igraph-Generators.html#igraph_famous
        should_plot (bool): se deve imprimir o grafo gerado

    Returns:
        Graph, lst, dict, int, int: grafo, matriz de distâncias,
                                    lista de adjacência, número de vértices
                                    e de arestas do grafo gerado
    """

    g = ig.Graph.Famous(type)

    distance_matrix = list((g.get_adjacency()))
    adj_list = get_adjacency_list(distance_matrix)
    n_nodes = g.vcount()
    m_edges = g.ecount()

    if should_plot:
        g.vs['label'] = list(range(n_nodes))
        g.vs['label_size'] = 12
        g.vs['color'] = 'tomato'

        ig.plot(g)

    return g, distance_matrix, adj_list, n_nodes, m_edges


def draw_clustered_graph(g, res, n_nodes):
    """Desenha o grafo em que os clusters obtidos
       pelo algoritmo genético são pintados de cores
       diferentes

    Args:
        g (Graph): grafo do módulo iGraph
        res (lst): lista com os clusters do grafo
        n_nodes (int): número de vértices do grafo
    """

    col = ig.drawing.colors.RainbowPalette(len(res))

    i = 0
    for cluster in res:
        for node_n in range(len(cluster)):
            g.vs[cluster[node_n]]['color'] = col.get(i)
        i += 1

    g.vs['label'] = list(range(n_nodes))
    g.vs['label_size'] = 12

    ig.plot(g)