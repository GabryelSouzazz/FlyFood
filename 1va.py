import itertools

def ler_matriz(nome_arquivo):
    # Abri o arquivo e lê as linhas
    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    # Extrai as dimensões da matriz
    dimensoes_matriz = linhas[0].strip().split()
    qtde_linhas = int(dimensoes_matriz[0])
    qtde_colunas = int(dimensoes_matriz[1])

    # Matriz vazia
    matriz = []

    # Percorre as linhas e adiciona na matriz
    for linha in linhas[1:]:
        elemento = linha.strip().split()
        matriz.append(elemento)

    # Verificação do tamanho da matriz
    if len(matriz) != qtde_linhas or len(matriz[0]) != qtde_colunas:
        print("Observação: As dimensões informadas não correspondem ao tamanho real da matriz!")

    return matriz

def encontrar_pontos(matriz):
    origem = None
    pontos = {}
    
    # Percorre as linhas e os elentos de cada linha
    for i, linha in enumerate(matriz):
        for j, valor in enumerate(linha):
            if valor == "R":
                origem = (i, j)
            elif valor != "0":
                pontos[valor] = (i, j)

    return origem, pontos

def distancia(p1_coord, p2_coord):
    ''' Calcula a distância entre dois pontos na matriz usano apenas movimento na vertical e horizontal(Distância de Manhattan).
    
    Parameters:
        p1_coord (tupla): coordenado o ponto 1.
        p2_coord (tupla): coordenada do ponto 2.
    
    Returns:
        distancia (int): distância do ponto 1 ao ponto 2.
    '''

    # Unpacking das coordenadas
    i1, j1 = p1_coord
    i2, j2 = p2_coord

    # Encontra a Distância de Manhattan a partir da fórmula: |i1 - i2| + |j1 - j2|
    distancia = abs(i1 - i2) + abs(j1 - j2)
    
    return distancia

def matriz_distancias(origem, pontos):
    """ Cria uma matriz(dicionário) com as distâncias entre todos os pontos incluindo a origem.

    Parameters:
        origem (tupla): coordenada do ponto de origem (R).
        pontos (dict): dicionário com os pontos de entrega e suas respectivas coordenadas.

    Returns:
        distancias (dict): dicionário de dicionário com as distâncias entre os pontos calculadas.
    """

    # Junção dos pontos em um dicionário
    todos_pontos = {"R": origem, **pontos}

    distancias = {}

    # Calcula a distância entre todos os pares de pontos
    for p1, coord1 in todos_pontos.items():
        distancias[p1] = {}
        for p2, coord2 in todos_pontos.items():
            if p1 == p2:
                distancias[p1][p2] = 0
            else:
                distancias[p1][p2] = distancia(coord1, coord2)

    return distancias

def calcular_custo(rota, distancias):
    """ Calcula o custo total de uma rota(soma das distâncias entre os pontos).

    Parameters:
        rota (list): lista com os pontos visitados ordenados por visita.
        distancias (dict): dicionário de dicionário com as distâncias entre os pontos.

    Returns:
        custo_total (int): soma das distâncias de cada trecho da rota.
    """

    if not rota:
        return 0
    
    custo_total = 0

    # Custo da partida do R para o primeiro ponto
    ponto_partida = rota[0]
    custo_total += distancias["R"][ponto_partida]

    # Custo dasentregas dos pontos sequencialmente
    for i in range(len(rota)-1):
        p1 = rota[i]
        p2 = rota[i+1]
        custo_total += distancias[p1][p2]
    
    # Custo do último ponto para R 
    ponto_chegada = rota[-1]
    custo_total += distancias[ponto_chegada]["R"] 

    return custo_total

def encontrar_e_exibir_rotas(pontos, matriz_distancias):
    """ Encontra a rota ótima(menor custo), através de todas as permutações dos pontos de entrega.

    O algoritmo imprime a rota apenas quando encontra um custo total MENOR que todas as rotas testadas anteriormente.

    Parameters:
        pontos (dict): dicionário contendo os pontos de entrega e suas respectivas coordenadas
        matriz_distancias (dict): dicionário de dicionário com as distâncias entre todos os pares de ponto

    Returns:
        melhor_rota_str (str): sequência dos pontos da rota ótima
        menor_custo (int): custo total da rota ótima
    """
    # Lista com os pontos de entrega
    lista_pontos_entregas = list(pontos.keys())
    
    # Inicialização
    menor_custo = float("inf")
    melhor_rota_encontrada = None
    
    # Geração das opções(Permutações)
    todas_as_rotas = itertools.permutations(lista_pontos_entregas)

    # Cabeçalho
    print("\n--- Otimização: Progresso de Encontro da Melhor Rota ---")
    print(f"{'Melhor Rota Atual (R -> ... -> R)':<35} | {'Custo Total':>18}")
    print("-" * 63)
    
    # Loop para calcular e encontrar o mínimo
    for permutacao in todas_as_rotas:
        custo_atual = calcular_custo(list(permutacao), matriz_distancias)
        
        if custo_atual < menor_custo:
            menor_custo = custo_atual
            melhor_rota_encontrada = permutacao

            # Exibe a rota apenas se ela for a melhor encontrada até agora
            rota_str_completa = "R -> " + " -> ".join(permutacao) + " -> R"
            print(f"{rota_str_completa:<35} | {custo_atual:>25}")

    melhor_rota_str = " ".join(melhor_rota_encontrada)
    
    return melhor_rota_str, menor_custo

def main():
    nome_arquivo = "matriz.txt"
    print(f"Projeto FlyFood: Roteamento de Drones ({nome_arquivo})")

    # Leitura e montagem da matriz
    matriz = ler_matriz(nome_arquivo)
    if matriz is None:
        return
    
    # Encontra as coordenadas
    origem_R, pontos_dict = encontrar_pontos(matriz)
    if not origem_R or not pontos_dict:
        print(f"Erro: Não foi possível encontrar o ponto de origem R e/ou os pontos de entrega.")
        return
    
    print(f"Ponto de Origem(R): {origem_R}")
    print(f"Pontos de Entrega: {pontos_dict}")


    
    matriz_de_distancias = matriz_distancias(origem_R, pontos_dict)
    
    # Encontra e Exibe a Rota Ótima
    melhor_sequencia_pontos, menor_custo = encontrar_e_exibir_rotas(pontos_dict, matriz_de_distancias)

    # Exibição do Resultado Final
    print("\n--- Resultado Ótimo Final ---")
    print(f"Menor Custo Encontrado: {menor_custo}")
    print(f"Sequência de Entrega: {melhor_sequencia_pontos}")


if __name__ == "__main__":
    main()