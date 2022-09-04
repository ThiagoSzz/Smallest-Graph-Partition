import utils
import copy
import igraph as ig
from math import ceil
from random import randint

"""
    TODO:
    - leitura de dados do arquivo
    - considerar a distância máxima D entre os vértices (matriz de distâncias)
    - considerar o tamanho máximo T de subconjuntos
    - otimização: usar sets ao invés de listas

    LINKS:
    https://igraph.org/python/api/latest/   --> documentação igraph
    https://moodle.inf.ufrgs.br/pluginfile.php/183293/mod_resource/content/1/geneticos.pdf   --> slides algoritmos genéticos
    https://igraph.org/c/doc/igraph-Generators.html#igraph_famous   --> tipos de grafos a gerar
"""

def evaluate(individual):
    """Função de avaliação de um indivíduo

    Args:
        individual (lst): lista com os clusters (subconjuntos) do grafo

    Returns:
        int: quantidade de clusters do grafo
    """

    return len(individual)


def tournament(participants):
    """Recebe uma lista com vários indivíduos e retorna o melhor deles, com relação
       a quantidade de subconjuntos do grafo
    
    Args:
        participants (lst): lista de individuos

    Returns:
        lst: melhor individuo da lista recebida
    """
    
    # assume que o primeiro indivíduo é o melhor da população
    best_individual = participants[0]
    best_fitness = evaluate(best_individual)

    # verifica se tem algum melhor que ele
    for individual in participants:
        eval_ind = evaluate(individual)

        if eval_ind < best_fitness:
            # caso tenha, atualiza o melhor indivíduo
            best_fitness = eval_ind
            best_individual = individual

    return best_individual


def crossover(parent1, parent2, index):
    """

    Args:
        parent1 (lst): indivíduo-pai 1
        parent2 (lst): indivíduo-pai 2
        index (num): inteiro que representa o índice do crossover
    
    Returns:
        <list, list>: indivíduos-filho 1 e 2
    """

    # faz cópia dos pais em nova lista
    new_parent1 = copy.deepcopy(parent1)
    new_parent2 = copy.deepcopy(parent2)

    if len(parent1) == 1 and len(parent2) == 1:
        # escolhe um cluster aleatório do primeiro pai
        cross_pos1 = randint(0, len(parent1)-1)
        cross_cluster1 = parent1[cross_pos1]

        cross_cluster2 = None

        found_cross = False

        # procura no segundo pai um vizinho de um dos nodos do
        # primeiro pai
        for cluster in range(len(parent2)):
            for node in parent2[cluster]:
                for node_1 in parent1[cross_pos1]:
                    for nbr in adj_list[node_1]:
                        if node == nbr:
                            cross_cluster2 = parent2[cluster]

                            found_cross = True
                            break
            
                    if found_cross:
                        break

                if found_cross:
                    break

            if found_cross:
                break

        # remove os nodos do cluster em que se encontra
        # o vizinho no vetor do primeiro pai
        for cluster in new_parent1:
            for value in cross_cluster2:
                if value in cluster:
                    cluster.remove(value)

        # remove os nodos do cluster em que se encontra
        # o primero pai no vetor do segundo pai
        for cluster in new_parent2:
            for value in cross_cluster1:
                if value in cluster:
                    cluster.remove(value)

        new_parent1.append(cross_cluster2)
        new_parent1 = list(filter(lambda x: x, new_parent1))

        new_parent2.append(cross_cluster1)
        new_parent2 = list(filter(lambda x: x, new_parent2))

    return new_parent1, new_parent2


def mutate(individual, m):
    """Recebe um indivíduo e a probabilidade de mutação (m).
       Caso random() < m, agrupa clusters vizinhos.

    Args:
        individual (lst): lista com os clusters do grafo
        m (int): probabilidade de mutação

    Returns:
        lst: indivíduo após mutação (ou intacto, caso a prob. de mutacao nao seja satisfeita)
    """

    # caso random() < m
    if randint(0, 100)/100 <= m:
        # se o indivíduo não tiver apenas um cluster
        if len(individual) != 1:
            found_nbr = False
            mutate_node = None

            # procura o primeiro cluster que não contenha algum vizinho
            # de um dos vértices do cluster
            # ex.: v1 é vizinho de v2 e v3
            #      [..., [v1, v2], ..., [v3, v4], ...]
            #
            #      irá procurar pelo cluster [v1, v2] pois v3 é
            #      vizinho de v1 e não está no mesmo cluster que v1
            for cluster_pos in range(len(individual)):
                for node in individual[cluster_pos]:
                    for nbr in adj_list[node]:
                        if nbr not in individual[cluster_pos]:
                            mutate_node = nbr
                            mutate_pos = cluster_pos

                            found_nbr = True
                            break

                    if found_nbr:
                        break

                if found_nbr:
                    break
            
            found_nbr = False

            # procura o cluster que possui esse vizinho e
            # junta os dois clusters
            # ex.: v1 é vizinho de v2 e v3
            #      [..., [v1, v2], ..., [v3, v4], ...]
            #
            #      irá procurar pelo cluster [v3, v4]
            #      em seguida, irá transformar [v1, v2] em [v1, v2, v3, v4]
            #      por fim, irá remover o antigo cluster [v3, v4]
            for cluster_pos in range(len(individual)):
                for node in individual[cluster_pos]:
                    if node == mutate_node:
                        individual[mutate_pos] += individual[cluster_pos]
                        individual.pop(cluster_pos)

                        found_nbr = True
                        break

                if found_nbr:
                    break

    return individual


def populate(n_ind):
    """Gera uma população com indivíduos gerados aleatoriamente

    Args:
        n_ind (num): quantidade de indivíduos a gerar

    Returns:
        lst: lista contendo a população gerada
    """

    lst_individuals = list()

    min_edge_cost = 1
    max_edge_cost = 25

    # itera n_ind indivíduos
    for _ in range(n_ind):
        # gera um grafo com n_nodes vértices
        g = ig.Graph(n=n_nodes)

        # gera pesos aleatórios para as arestas
        edges_weight = list()

        for _ in range(m_edges):
            edges_weight.append(randint(min_edge_cost, max_edge_cost))

        # adiciona as arestas ao grafo
        visited = list()

        for node in range(len(adj_list)):
            for nbr in adj_list[node]:
                if (node, nbr) not in visited:
                    g.add_edge(node, nbr)
                    visited.append((nbr, node))

        # efetua a 'clusterização'
        d = ig.Graph.community_fastgreedy(g, weights=edges_weight)

        cluster_amount = randint(ceil(n_nodes*min_cluster_amount), n_nodes)
        d = d.as_clustering(cluster_amount)
        individual = utils.igraph_cluster_to_list(d)

        # verifica se o indivíduo gerado já existe
        # antes de adicioná-lo à população
        if individual not in lst_individuals:
            lst_individuals.append(individual)

    return lst_individuals


def selection(participants, k):
    """Seleciona k participantes de uma população

    Args:
        participants (lst): população
        k (num): quantidade de participantes a selecionar

    Returns:
        lst: população selecionada
    """

    sel_participants = list()
    
    '''print('participants: ')
    for i in participants:
        print(i)
    print()'''

    for _ in range(k):
        selected = randint(0, len(participants)-1)
        sel_participants.append(participants[selected])

    '''print('selected: ')
    for i in sel_participants:
        print(i)
    print()'''

    return sel_participants


def run_ga(g, n, k, m, e, debug):
    """Executa o algoritmo genético e retorna o indivíduo com o menor número de clusters
    
    Args:
        g (int): numero de gerações
        n (int): numero de indivíduos
        k (float): porcentagem de participantes do torneio
        m (float): probabilidade de mutação (entre 0 e 1, inclusive)
        e (bool): se vai haver elitismo
        debug (bool): modo debug (mostra os prints)

    Returns:
        lst: melhor indivíduo encontrado
    """

    # inicializa a população aleatoriamente
    p = populate(n)

    if debug:
        print('populacao:')
        print(p, '\n')

    # para cada geração,
    for _ in range(g):
        if e:
            # se elitismo, inicializa nova população com o melhor indivíduo
            # da população anterior
            p_nova = list()
            p_nova.append(tournament(p))
        else:
            p_nova = []

        # enquanto o número de indivíduos da população for menor que "n"
        while len(p_nova) < n:
            # seleciona k% participantes
            selected_participants = selection(p, int(len(p)*k))

            if debug:
                print('selecao:')
                print(selected_participants, '\n')

            # executa dois torneios com os k participantes
            p1 = tournament(selected_participants)

            # para o segundo torneio, retira o valor de p1
            # que já foi selecionado
            p_nova_linha = copy.deepcopy(selected_participants)
            p_nova_linha.remove(p1)
            p2 = tournament(p_nova_linha)

            if debug:
                print('torneio:')
                print('p1: ', p1)
                print('p2: ', p2, '\n')

            # executa o crossover e obtém os dois filhos
            # ponto de cruzamento é aleatório
            o1, o2 = crossover(p1, p2, randint(0, min(len(p1), len(p2))))

            if debug:
                print('crossover:')
                print('o1: ', o1)
                print('o2: ', o2, '\n')

            # executa a mutação dos dois filhos
            o1 = mutate(o1, m)
            o2 = mutate(o2, m)

            if debug:
                print('mutacao:')
                print('o1: ', o1)
                print('o2: ', o2, '\n')

            # adiciona os dois filhos na nova população
            p_nova.append(o1)
            p_nova.append(o2)

            if debug:
                print('crossover:')
                print('p_nova: ', p_nova, '\n')
                print('---------------------------')
        
        # atualiza a população original com a população nova
        p = p_nova

    # retorna o melhor indivíduo da população gerada
    return tournament(p)


if __name__ == "__main__":
    '''
    n_nodes = 6
    m_edges = 6
    D_max_distance = 4
    T_set_size = 3

    edges_cost = [2, 5, 4, 3, 1, 3]

    distance_matrix = [[0, 2, 5, 0, 0, 0],
                       [2, 0, 0, 4, 3, 0],
                       [5, 0, 0, 0, 0, 1],
                       [0, 4, 0, 0, 0, 0],
                       [0, 3, 0, 0, 0, 3],
                       [0, 0, 1, 0, 3, 0]]

    adj_list = utils.get_adjacency_list(distance_matrix)
    '''

    # porcentagem mínima do número de nodos
    # que irá gerar o número de clusters
    # ex.: com n_nodes = 10 e min_cluster_amount = 0.5
    #      irá gerar de 5 a 10 clusters
    min_cluster_amount = 0.5

    distance_matrix, adj_list, n_nodes, m_edges = utils.generate_graph('Levi', True)

    # itera o limite superior de max_gen gerações
    max_gen = 20

    for gen in range(max_gen):
        # executa o algoritmo genético
        res = run_ga(gen, 200, 0.8, 0.2, 1, False)
        
        print(f'geracao: {gen} --> fitness: {evaluate(res)}')
        print(f'valor otimo: {res}\n')

        # se atingir o valor ótimo da minimização (fitness == 1), encerra
        if evaluate(res) == 1:
            break
    