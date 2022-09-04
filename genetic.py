import utils
import copy
from random import randint
import igraph as ig

"""
    TODO:
    - leitura de dados do arquivo
    - considerar a distância máxima D entre os vértices (matriz de distâncias)
    - considerar o tamanho máximo T de subconjuntos
    - arrumar a função de crossover
    - arrumar a função de selection

    LINKS:
    https://igraph.org/python/api/latest/   --> documentação igraph
    https://moodle.inf.ufrgs.br/pluginfile.php/183293/mod_resource/content/1/geneticos.pdf --> slides algoritmos genéticos
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

    new_parent1 = copy.deepcopy(parent1[:index])
    for item in parent2[index:]:
        new_parent1.append(item)

    new_parent2 = copy.deepcopy(parent2[:index])
    for item in parent1[index:]:
        new_parent2.append(item)

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

    min_cluster_size = 0.5

    # itera n_ind indivíduos
    for _ in range(n_ind):
        # gera um grafo com n_nodes vértices
        g = ig.Graph(n=n_nodes)

        # adiciona as arestas ao grafo
        visited = list()

        for node in range(len(adj_list)):
            for nbr in adj_list[node]:
                if (node, nbr) not in visited:
                    g.add_edge(node, nbr)
                    visited.append((nbr, node))

        # efetua a 'clusterização'
        d = ig.Graph.community_fastgreedy(g)

        cluster_size = randint(int(n_nodes*min_cluster_size), n_nodes)
        d = d.as_clustering(cluster_size)
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


def run_ga(g, n, k, m, e):
    """Executa o algoritmo genético e retorna o indivíduo com o menor número de clusters
    
    Args:
        g (int): numero de gerações
        n (int): numero de indivíduos
        k (int): numero de participantes do torneio
        m (float): probabilidade de mutação (entre 0 e 1, inclusive)
        e (bool): se vai haver elitismo

    Returns:
        lst: melhor indivíduo encontrado
    """

    # inicializa a população aleatoriamente
    p = populate(n)

    '''print('populacao: ')
    for i in p:
        print(i)
    print()'''

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
            # seleciona k participantes
            selected_participants = selection(p, k)

            # executa dois torneios com os k participantes
            p1 = tournament(selected_participants)

            # para o segundo torneio, retira o valor de p1
            # que já foi selecionado
            p_nova_linha = copy.deepcopy(selected_participants)
            p_nova_linha.remove(p1)
            p2 = tournament(p_nova_linha)

            # executa o crossover e obtém os dois filhos
            # ponto de cruzamento é aleatório
            # ERRO!!!!
            o1, o2 = crossover(p1, p2, randint(0, min(len(p1), len(p2))))

            # executa a mutação dos dois filhos
            o1 = mutate(o1, m)
            o2 = mutate(o2, m)

            # adiciona os dois filhos na nova população
            p_nova.append(o1)
            p_nova.append(o2)
        
        # atualiza a população original com a população nova
        p = p_nova

    # retorna o melhor indivíduo da população gerada
    return tournament(p)


if __name__ == "__main__":
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

    res = run_ga(1, 200, 50, 0.2, 0)
    print(res)