import igraph as ig
import numpy as np


def inc_by_1(ind):
    """Incrementa os valores dos labels dos
       vértices em 1. Isso por que o processamento
       das listas, matrizes e dicionários é feito de
       '0' a 'n-1', porém a definição do problema
       especifica que os vértices são numerados
       de '1' a 'n'.

    Args:
        ind (lst): lista que representa o indivíduo (subconjuntos)

    Returns:
        lst: lista entrada com valores incrementados em 1
    """

    if type(ind[0]) is list:
        return [[x+1 for x in y] for y in ind]
    else:
        return [x+1 for x in ind]


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


def create_graph(n_nodes, adj_list, edges_cost):
    """Cria o grafo com n_nodes vértices a partir
       de sua lista de adjacência

    Args:
        n_nodes (int): número de vértices do grafo
        adj_list (dict): lista de adjacência do grafo

    Returns:
        Graph: grafo do módulo iGraph
    """

    # Referência: https://stackoverflow.com/questions/50224502/python-igraph-how-to-add-edges-with-weight

    edge = list()
    weights = list()

    for i in range(len(edges_cost)):
        for j in range(2):
            edge.append(edges_cost[i][j])
        weights.append(edges_cost[i][2])

    edges = [(i-1, j-1) for i, j in zip(edge[::2], edge[1::2])]

    edge_list = list()
    for i in range(len(edges)):
        edge_list.append((int(edges[i][0]), int(edges[i][1])))

    g=ig.Graph()
    g.add_vertices(n=n_nodes)
    g.add_edges(edge_list)
    g.es['weight'] = weights

    return g


def generate_graph(n_nodes, distance_matrix, edges_cost, should_plot):
    """Gera o grafo com n_nodes vértices a partir de sua
       matriz de distâncias. Permite mostrar o grafo.

    Args:
        n_nodes (int): número de vértices do grafo
        distance_matrix (lst): matriz de distâncias do grafo
        edges_cost (lst): lista de tuplas contendo as arestas do grafo
        should_plot (bool): True, para 'plotar' o grafo
                            False, caso contrário

    Returns:
        Graph: grafo do módulo iGraph
    """

    adj_list = get_adjacency_list(distance_matrix)

    g = create_graph(n_nodes, adj_list, edges_cost)

    if should_plot:
        g.vs['label'] = inc_by_1(list(range(n_nodes)))
        g.vs['label_size'] = 12
        g.vs['color'] = 'tomato'

        g.es['label'] = g.es['weight']

        ig.plot(g)

    return g, adj_list


def draw_clustered_graph(g, res, n_nodes):
    """Desenha o grafo em que os clusters obtidos
       pelo algoritmo genético são pintados de cores
       diferentes

    Args:
        g (Graph): grafo do módulo iGraph
        res (lst): lista com os clusters do grafo
        n_nodes (int): número de vértices do grafo
        edges_cost (lst): lista de tuplas contendo as arestas do grafo
    """

    col = ig.drawing.colors.RainbowPalette(len(res))

    i = 0
    for cluster in res:
        for node_n in range(len(cluster)):
            g.vs[cluster[node_n]]['color'] = col.get(i)
        i += 1

    g.vs['label'] = [x+1 for x in list(range(n_nodes))]
    g.vs['label_size'] = 12

    g.es['label'] = g.es['weight']

    ig.plot(g)


def read_instance(file_name, should_plot):
    """Lê o arquivo de uma instância do problema e
       coleta os dados necessários para resolver o
       problema. São eles:
       n -> número de vértices
       m -> número de arestas
       D -> distância máxima entre os vértices de um subconjunto
       T -> número máximo de vértices em um subconjunto

    Args:
        file_name (str): nome do arquivo

    Returns:
        int, int, int, int, lst, lst: dados coletados
    """

    # abre o arquivo
    file = open(file_name)

    # lê os valores n, m, D e T do grafo
    n, m, D, T = file.readline().split()
    n, m, D, T = int(n), int(m), int(D), int(T)

    # lê os pesos das arestas do grafo
    costs = list()

    for _ in range(m):
        line = file.readline().split()
        costs_vec = list()

        for i in range(3):
            costs_vec.append(int(line[i]))

        costs.append(costs_vec)
        
    # lê a matriz de distâncias do grafo
    distance_matrix = [[int(num) for num in line.split(' ')] for line in file]
    cost_tuples = [tuple(l) for l in costs]

    file.close()

    graph, adj_list = generate_graph(n, distance_matrix, cost_tuples, should_plot)

    return n, m, D, T, distance_matrix, cost_tuples, graph, adj_list