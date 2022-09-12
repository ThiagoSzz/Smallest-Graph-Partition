import utils
import copy
import igraph as ig
from random import randint, choice


"""
    TODO:
    - leitura de dados do arquivo
    - otimização: usar sets ao invés de listas
    - bug: as vezes um vértice aleatório é colocado em um cluster
           em que não tem vizinhos

    DÚVIDAS:
    - considerar grafos disconexos?
    - casos de teste?
    - podemos usar um grafo gerado aleatoriamente?
        - se não, o grafo dado terá quantos vértices?
    - podemos usar um módulo para fazer a partição do grafo (igraph)?
    - tempo limite de execução?

    LINKS:
    https://igraph.org/python/api/latest/   --> documentação igraph
    https://moodle.inf.ufrgs.br/pluginfile.php/183293/mod_resource/content/1/geneticos.pdf   --> slides algoritmos genéticos
    https://igraph.org/c/doc/igraph-Generators.html#igraph_famous   --> tipos de grafos a gerar
"""


def is_eligible(individual):
    """Verifica se a distância máxima entre os vértices de um
       cluster são menores que a distância máxima permitida
       (E)
       Verifica se o tamanho dos clusters é menor que o tamanho
       máximo permitido

    Args:
        individual (lst): lista dos clusters do grafo

    Returns:
        bool: True, caso não tenha nenhum cluster com distance > D_max_distance (E)
                    caso para todos os clusters len(cluster) < T_set_size
              False, caso contrário
    """

    eligibility = True

    # itera os clusters de um indivíduo
    for v_set in individual:
        distance = 0
        visited = list()
        
        # verifica se é menor que o tamanho máximo permitido
        if len(v_set) <= T_set_size:
            # itera os vértices de um cluster
            for j in range(len(v_set)):
                current = v_set[j]
                visited.append(current)

                # itera os vizinhos do vértice
                for i in adj_list[current]:
                    # se o vizinho estiver no cluster
                    # e se o vértice e seu vizinho estão na lista de vértices visitados
                    if (i in v_set) and (current in visited and i in visited):
                        # soma a distância à distância total entre os vértices do cluster
                        # e adiciona o vizinho à lista de vértices visitados
                        distance += distance_matrix[current][i]
                        visited.append(i)

            # se a distância total entre os vértices do cluster
            # for maior que o permitido
            if distance > D_max_distance:
                # se sim, retorna falso
                eligibility = False
                break
        else:
            #print(v_set, len(v_set))
            # se não, retorna falso
            eligibility = False
            break

    return eligibility


def evaluate(individual):
    """Função de avaliação de um indivíduo

    Args:
        individual (lst): lista com os clusters (subconjuntos) do grafo

    Returns:
        int: quantidade de clusters do grafo
    """

    if not is_eligible(individual):
        fitness = float('inf')
    else:
        fitness = len(individual)

    return fitness


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


def crossover(parent1, parent2):
    """Agrupa um vértice de um cluster do primeiro pai
       com um vértice de um cluster do segundo pai e
       vice-versa. É necessário que os vértices
       tenham vizinhos no cluster para o qual forem trocados,
       para manter a factibilidade da solução.

    Args:
        parent1 (lst): indivíduo-pai 1
        parent2 (lst): indivíduo-pai 2
    
    Returns:
        <list, list>: indivíduos-filho 1 e 2
    """

    # faz cópia dos pais em nova lista
    new_parent1 = copy.deepcopy(parent1)
    new_parent2 = copy.deepcopy(parent2)

    if len(parent1) != 1 and len(parent2) != 1:
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

        # adiciona o cluster da troca nos pais
        # e remove os clusters vazios
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
            mutate_node_l = list()
            mutate_pos_l = list()

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
                            mutate_node_l.append(nbr)
                            mutate_pos_l.append(cluster_pos)

            # procura o cluster que possui esse vizinho e
            # junta os dois clusters
            # ex.: v1 é vizinho de v2 e v3
            #      [..., [v1, v2], ..., [v3, v4], ...]
            #
            #      irá procurar pelo cluster [v3, v4]
            #      em seguida, irá transformar [v1, v2] em [v1, v2, v3, v4]
            #      por fim, irá remover o antigo cluster [v3, v4]
            best_ind = copy.deepcopy(individual)

            if len(mutate_pos_l) != 0:
                best_list = list()

                i = 0

                while i < len(mutate_pos_l):
                    mp_i = mutate_pos_l[i]
                    mn_i = mutate_node_l[i]

                    i += 1

                    found_best = False

                    for cluster_pos in range(len(individual)):
                        for node in individual[cluster_pos]:
                            if node == mn_i:
                                best_ind = copy.deepcopy(individual)
                                best_ind[mp_i] += best_ind[cluster_pos]
                                best_ind.pop(cluster_pos)

                                best_list.append(best_ind)
                                found_best = True
                                break

                        if found_best:
                            break
                
                individual = choice(best_list)
    
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

        # efetua a segmentação
        d = ig.Graph.community_edge_betweenness(g, weights=edges_weight)

        cluster_amount = randint(int(n_nodes*min_cluster_amount), n_nodes)
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

    copy_participants = copy.deepcopy(participants)

    sel_participants = list()
    n_selected = 0

    wait_list = list()
    
    '''print('participants: ')
    for i in copy_participants:
        print(i, evaluate(i))
    print()'''

    # itera k indivíduos
    for _ in range(k):
        selected = randint(0, len(copy_participants)-1)

        if evaluate(copy_participants[selected]) != float('inf'):
            # adiciona o indivíduo na lista de selecionados
            sel_participants.append(copy_participants[selected])
            n_selected += 1
        else:
            wait_list.append(copy_participants[selected])

        # e remove da lista de indivíduos para não selecioná-lo novamente
        copy_participants.pop(selected)

    for inf_individual in range(len(wait_list)):
        sel_participants.append(wait_list[inf_individual])
        n_selected += 1

        if n_selected == k:
            break

    '''print('selected: ')
    for i in sel_participants:
        print(i, evaluate(i))
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
        debug (str): modo debug
                     'all'        --> mostra todos os prints
                     'show_steps' --> mostra somente o resultado dos passos do algoritmo
                     'show_gen'   --> mostra somente o resultado obtido em cada geração

    Returns:
        lst: melhor indivíduo encontrado
    """

    # inicializa a população aleatoriamente
    p = populate(n)
    n_k = int(len(p)*k)

    if debug == 'show_steps' or debug == 'all':
        print('populacao:')
        print(p, '\n')

    # para cada geração,
    for n_g in range(g):
        p_nova = list()

        if e:
            # se elitismo, inicializa nova população com o melhor indivíduo
            # da população anterior
            p_nova.append(tournament(p))

        # enquanto o número de indivíduos da população for menor que "n"
        while len(p_nova) < n:
            # seleciona k% participantes
            selected_participants = selection(p, n_k)

            if debug == 'show_steps' or debug == 'all':
                print('selecao:')
                for i in selected_participants:
                    print(i, ': ', evaluate(i))
                print()

            # executa dois torneios com os k participantes
            p1 = tournament(selected_participants)

            # para o segundo torneio, retira o valor de p1
            # que já foi selecionado
            p_nova_linha = copy.deepcopy(selected_participants)
            p_nova_linha.remove(p1)
            p2 = tournament(p_nova_linha)

            if debug == 'show_steps' or debug == 'all':
                print('torneio:')
                print('p1: ', p1, ': ', evaluate(p1))
                print('p2: ', p2, ': ', evaluate(p2), '\n')

            # executa o crossover e obtém os dois filhos
            # ponto de cruzamento é aleatório
            o1, o2 = crossover(p1, p2)

            if debug == 'show_steps' or debug == 'all':
                print('crossover:')
                print('o1: ', o1)
                print('o2: ', o2, '\n')

            # executa a mutação dos dois filhos
            o1 = mutate(o1, m)
            o2 = mutate(o2, m)

            if debug == 'show_steps' or debug == 'all':
                print('mutacao:')
                print('o1: ', o1)
                print('o2: ', o2, '\n')

            # adiciona os dois filhos na nova população
            p_nova.append(o1)
            p_nova.append(o2)

            if debug == 'show_steps' or debug == 'all':
                print('p_nova: ')
                print(p_nova, '\n')
                print('---------------------------')
        
        # atualiza a população original com a população nova
        p = p_nova
        
        # obtém o melhor indivíduo da geração
        best_ind = tournament(p)

        if debug == 'show_gen' or debug == 'all':
            print(f'melhor da geracao {n_g+1}: {best_ind} --> {evaluate(best_ind)}\n')
            #utils.draw_clustered_graph(graph, best_ind, n_nodes)

    # retorna o melhor indivíduo da última geração calculada
    return best_ind


if __name__ == "__main__":
    '''
    n_nodes = 6
    m_edges = 6

    distance_matrix = [[0, 2, 5, 0, 0, 0],
                       [2, 0, 0, 4, 3, 0],
                       [5, 0, 0, 0, 0, 1],
                       [0, 4, 0, 0, 0, 0],
                       [0, 3, 0, 0, 0, 3],
                       [0, 0, 1, 0, 3, 0]]

    adj_list = utils.get_adjacency_list(distance_matrix)
    '''

    D_max_distance = 3
    T_set_size = 4
    min_cluster_amount = 0.8

    graph, distance_matrix, adj_list, n_nodes, m_edges = \
    utils.generate_graph('Walther', True)

    for _ in range(10):
        #            gen   ind   sel   mut   elit   debug
        res = run_ga(10,   200,  0.20, 0.25, True, 'show_gen')

        utils.draw_clustered_graph(graph, res, n_nodes)