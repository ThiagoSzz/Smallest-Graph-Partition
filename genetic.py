import utils
import copy
import igraph as ig
import time
import sys
from random import randint, choice, choices


"""
    TODO:
    - otimização: usar sets ao invés de listas

    LINKS:
    https://igraph.org/python/api/latest/   --> documentação igraph
    https://moodle.inf.ufrgs.br/pluginfile.php/183293/mod_resource/content/1/geneticos.pdf   --> slides algoritmos genéticos
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
        bool: True, caso não tenha nenhum cluster com: distance > D
                    (E)
                    caso para todos os clusters: len(cluster) < T
              False, caso contrário
    """

    eligibility = True

    #print(utils.inc_by_1(individual))
    for v_set in individual:
        if len(v_set) <= T:
            d = 0
            visited = list()
            for vertex_i in range(len(v_set)):
                for vertex_j in range(len(v_set)):
                    if vertex_j != vertex_i:
                        sp = graph.get_shortest_paths(v_set[vertex_i], to=v_set[vertex_j])
                        
                        if set(sp[0]) == set(v_set) and v_set not in visited:
                            #print(f'de {v_set[vertex_i]+1} ate {v_set[vertex_j]+1} o menor caminho eh {utils.inc_by_1(sp)}')
                            visited.append(v_set)
                            d += distance_matrix[v_set[vertex_i]][v_set[vertex_j]]

            #print(len(v_set), d)
            if d > D or (len(v_set) > 1 and d == 0):
                #print('d=', d)
                eligibility = False
                break
        else:
            #print('len=', len(v_set))
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
    
    # escolhe o primeiro indivíduo da lista de participantes como o melhor
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
                
                # duas opções:
                # escolhe indivíduo aleatório da lista de
                # melhores mutações (mais natural)
                #individual = choice(best_list)

                # ou

                # escolhe indivíduo com a mutação
                # que possuir o melhor fitness (mais "forçado")
                best_ind = individual
                best_fitness = evaluate(best_ind)

                for ind in best_list:
                    if evaluate(ind) < best_fitness:
                        best_ind = ind
                        best_fitness = evaluate(best_ind)

                individual = best_ind
    
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

    mca_nn = int(n_nodes*min_cluster_amount)

    # cria o grafo com n_nodes vértices a partir de
    # sua lista de adjacência
    g = utils.create_graph(n_nodes, adj_list, edges_w)

    # itera n_ind indivíduos
    for _ in range(n_ind):
        # gera pesos aleatórios para as arestas
        edges_weight = list()

        for _ in range(m_edges):
            edges_weight.append(randint(min_edge_cost, max_edge_cost))

        # efetua a segmentação
        vd = ig.Graph.community_walktrap(g, weights=edges_weight)
        vd = vd.as_clustering(randint(mca_nn, n_nodes))
        individual = utils.igraph_cluster_to_list(vd)

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

    return sel_participants


def run_ga(g, n, k, m, e, debug='none'):
    """Executa o algoritmo genético e retorna o indivíduo com o menor número de clusters
    
    Args:
        g (int): numero de gerações
        n (int): numero de indivíduos
        k (float): porcentagem de participantes do torneio
        m (float): probabilidade de mutação (entre 0 e 1, inclusive)
        e (bool): se vai haver elitismo
        debug (str): modo debug
                     'all'            --> mostra todos os prints
                     'show_steps'     --> mostra somente o resultado dos passos do algoritmo
                     'show_gen'       --> mostra somente o resultado obtido em cada geração
                     'show_time'      --> mostra o tempo de execução de cada etapa do algoritmo
                     'show_gen+time'  --> show_gen e show_time
                     'none'           --> não mostra nada

    Returns:
        lst: melhor indivíduo encontrado
    """

    t_populate = 0
    t_selection = 0
    t_tournament = 0
    t_crossover = 0
    t_mutate = 0

    # inicializa a população aleatoriamente
    t_start = time.time()

    p = populate(n)
    n_k = int(k*len(p))

    t_elapsed = (time.time() - t_start)
    t_populate += t_elapsed

    last_best = evaluate(tournament(p))
    same_fitness = 0
    last_gen = g

    if debug == 'show_steps' or debug == 'all':
        '''print('populacao:')
        for i in p:
            print(utils.inc_by_1(i), end=' ')
        print()'''

    # para cada geração,
    for n_g in range(g):
        p_nova = []

        if e:
            # se elitismo, inicializa nova população com o melhor indivíduo
            # da população anterior
            p_nova.append(tournament(p))

        # enquanto o número de indivíduos da população for menor que "n"
        while len(p_nova) < n:
            t_start = time.time()

            # seleciona k% participantes
            selected_participants = selection(p, n_k)

            t_elapsed = (time.time() - t_start)
            t_selection += t_elapsed

            if debug == 'show_steps' or debug == 'all':
                print('\nselecao:')
                for i in selected_participants:
                    print(utils.inc_by_1(i), ': ', evaluate(i))
                print()

            t_start = time.time()

            # executa dois torneios com os k participantes
            p1 = tournament(selected_participants)

            # para o segundo torneio, retira o valor de p1
            # que já foi selecionado
            p_nova_linha = copy.deepcopy(selected_participants)
            p_nova_linha.remove(p1)
            p2 = tournament(p_nova_linha)

            t_elapsed = (time.time() - t_start)
            t_tournament += t_elapsed

            if debug == 'show_steps' or debug == 'all':
                print('torneio:')
                print('p1: ', utils.inc_by_1(p1), ': ', evaluate(p1))
                print('p2: ', utils.inc_by_1(p2), ': ', evaluate(p2), '\n')

            t_start = time.time()

            # executa o crossover e obtém os dois filhos
            # ponto de cruzamento é aleatório
            o1, o2 = crossover(p1, p2)

            t_elapsed = (time.time() - t_start)
            t_crossover += t_elapsed

            if debug == 'show_steps' or debug == 'all':
                print('crossover:')
                print('o1: ', utils.inc_by_1(o1))
                print('o2: ', utils.inc_by_1(o2), '\n')

            t_start = time.time()

            # executa a mutação dos dois filhos
            o1 = mutate(o1, m)
            o2 = mutate(o2, m)

            t_elapsed = (time.time() - t_start)
            t_mutate += t_elapsed

            if debug == 'show_steps' or debug == 'all':
                print('mutacao:')
                print('o1: ', utils.inc_by_1(o1))
                print('o2: ', utils.inc_by_1(o2), '\n')

            # adiciona os dois filhos na nova população
            p_nova.append(o1)
            p_nova.append(o2)

            if debug == 'show_steps' or debug == 'all':
                '''print('p_nova: ')
                for i in p_nova:
                    print(utils.inc_by_1(i), end=' ')
                print('\n---------------------------')'''
        
        # atualiza a população original com a população nova
        p = p_nova
        
        # obtém o melhor indivíduo da geração
        best_ind = tournament(p)

        last_gen = n_g+1

        if evaluate(best_ind) == last_best:
            same_fitness += 1

            if(same_fitness == max_fitness_repeat):
                last_gen = n_g+1-max_fitness_repeat

                if debug == 'show_gen' or debug == 'show_gen+time' or debug == 'all' or debug == 'show_last':
                    print(f'Parou de se aprimorar na geracao {last_gen}\n')

                break
        else:
            last_best = evaluate(best_ind)
            same_fitness = 0

        if debug == 'show_gen' or debug == 'show_gen+time' or debug == 'all' or (debug == 'show_last' and n_g == g-1):
            print(f'Geracao {n_g+1}: {utils.inc_by_1(best_ind)} --> {evaluate(best_ind)}\n')

    if debug == 'show_time' or debug == 'show_gen+time':
        print('Populate: {:.4f}s'.format(t_populate))
        print('Selection: {:.4f}s'.format(t_selection))
        print('Tournament: {:.4f}s'.format(t_tournament))
        print('Crossover: {:.4f}s'.format(t_crossover))
        print('Mutate: {:.4f}s\n'.format(t_mutate))

    # retorna o melhor indivíduo da última geração calculada
    return best_ind, last_gen


if __name__ == "__main__":
    # porcentagem do número de vértices que será
    # o limite inferior do número de subconjuntos
    # gerados durante o populate()
    # ex.: com min_cluster_amount = 0.8 e n_nodes = 10,
    #      a função irá gerar indivíduos com 8 a 10 
    #      subconjuntos
    min_cluster_amount = 0.7

    # número máximo que o mesmo fitness pode repetir
    # sem ser considerado inapto a mudar
    max_fitness_repeat = 4

    # nome do arquivo com informações do grafo
    instance_list = ['instance_6_6_4_3.dat',         'instance_20_30_20_3.dat',
                     'instance_20_100_10_5.dat',     'instance_50_75_50_5.dat',
                     'instance_50_750_10_5.dat',     'instance_100_350_50_10.dat',
                     'instance_100_1000_25_15.dat',  'instance_250_3000_20_20.dat',
                     'instance_250_7500_10_25.dat',  'instance_500_2500_50_50.dat',
                     'instance_500_10000_15_50.dat', 'instance_1000_10000_25_50.dat',
                     'instance_1000_50000_10_100.dat']

    res = open('results.txt', 'a')
    res.write('Instância BKV OPT\n')
    res.close()

    for fn in instance_list[3:]:
        # lê o arquivo da instância e coleta os dados
        n_nodes, m_edges, D, T, distance_matrix, dm1, edges_w = \
        utils.read_instance('problema1-instancias/' + fn)

        # gera e plota o grafo a partir da instância lida
        graph, adj_list = utils.generate_graph(n_nodes, dm1, edges_w, False)

        # variáveis do algoritmo genético
        n_gen = int(n_nodes/2)
        n_ind = 500
        selection_ratio = 0.2
        mutation_chance = 0.25
        elitism = False

        print(f'# Instancia {fn}')
        print(f'# Algoritmo genetico com {n_ind} individuos e {n_gen} geracoes.\n')

        time_start = time.time()

        # algoritmo genético
        res_ind, last_gen = run_ga(n_gen, n_ind, selection_ratio, mutation_chance, elitism, 'show_steps')
        
        print(f'*** Geracao {last_gen}: {utils.inc_by_1(res_ind)} --> {evaluate(res_ind)} ***\n')
        
        # calcula o tempo levado para executar o algoritmo genético
        time_elapsed = (int(time.time()) - int(time_start))/60

        # plota o grafo com os vértices coloridos de acordo
        # com o resultado da partição
        #utils.draw_clustered_graph(graph, res_ind, n_nodes)

        res_info = open('results_info.txt', 'a')
        res_info.write(f'Instância \'{fn}\'\n')
        res_info.write(f'n={n_nodes}, m={m_edges}, D={D}, T={T}\n')
        res_info.write(f'Resultado com {last_gen} gerações e {n_ind} indivíduos:\n')
        res_info.write(f'{utils.inc_by_1(res_ind)} --> fitness {evaluate(res_ind)}\n')
        res_info.write('Tempo de execução: {:.3f} minutos\n\n'.format(time_elapsed))
        res_info.close()

        res = open('results.txt', 'a')
        res.write(f'{fn} {evaluate(res_ind)}\n')
        res.close()