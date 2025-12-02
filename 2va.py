import random
import time

def converter_para_tsplib(caminho_arquivo_entrada):
    ''' Lê um arquivo de matriz FlyFood em txt e converte para o formato de string TSPLIB.
    
    Parameters:
        caminho_arquivo_entrada (str): caminho do arquivo .txt com a matriz.
    
    Returns:
        conteudo_tsplib (str): Conteúdo completo no formato TSPLIB.
    '''
    # Leitura do arquivo e extração dos pontos
    pontos = []

    try:
        with open(caminho_arquivo_entrada, "r") as arquivo:
            linhas = arquivo.readlines()

            # Pula a primeira linha da matriz
            matriz_bruta = [linha.strip().split() for linha in linhas[1:]]

            # Percorre a matriz e encontra as coordenadas
            for i, linha in enumerate(matriz_bruta):
                for j, valor in enumerate(linha):
                    if valor != "0":
                        pontos.append({"ponto": valor, "coord": (i,j)})

    except FileNotFoundError:
        return "Erro: Arquivo não encontrado."
    
    # Garante que o R será o primeiro e logo sepois as outras letras em ordem alfabetica
    pontos.sort(key=lambda k: (k['ponto'] != 'R', k['ponto']))

    qtde_pontos = len(pontos)

    # Cabeçalho TSPLIB
    tsplib = [
        "NAME: flyfood_instance",
        "TYPE: TSP",
        f"DIMENSION: {qtde_pontos}",
        "EDGE_WEIGHT_TYPE: EXPLICIT",
        "EDGE_WEIGHT_FORMAT: FULL_MATRIX",
        "EDGE_WEIGHT_SECTION"
    ]

    # Matriz de distâncias(distância de Manhattan)
    matriz_texto = []

    for i in range(qtde_pontos):
        linha_distancias = []
        p1 = pontos[i]["coord"]

        for j in range(qtde_pontos):
            p2 = pontos[j]["coord"]

            # Distância de Manhattan: |x1 - x2| + |y1 - y2|
            dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
            linha_distancias.append(str(dist))

        # Adiciona linha_distancias em matriz_texto
        matriz_texto.append(" ".join(linha_distancias))

    # Resultado final
    conteudo_tsplib = "\n".join(tsplib) + "\n" + "\n".join(matriz_texto) + "\nEOF"

    return conteudo_tsplib

def converter_texto_para_matriz(conteudo_tsplib):
    ''' Lê a string no formato TSPLIB e transforma em uma matriz de distâncias (lista de listas).
    
    Parameters:
        conteudo_tsplib (str): O texto completo no formato TSPLIB.
    
    Returns:
        matriz_distancias (list): Uma matriz NxN onde matriz[i][j] é a distância entre o ponto i e o ponto j. 
    '''
    # Quebra o texto em linhas
    linhas = conteudo_tsplib.strip().split('\n')

    matriz_distancias = []
    lendo_matriz = False

    for linha in linhas:
        linha = linha.strip()

        if linha == "EDGE_WEIGHT_SECTION":
            lendo_matriz = True
            continue

        if linha == "EOF":
            break
    
        if lendo_matriz:
            if linha:
                valores = [int(val) for val in linha.split()]
                matriz_distancias.append(valores)
    
    return matriz_distancias
        
def gerar_populacao_inicial(num_pontos, tamanho_populacao):
    ''' Gera uma lista de rotas aleatórias (indivíduos).
    
    Parameters:
        num_pontos (int): Total de pontos (incluindo R).
        tamanho_populacao (int): Quantos indivíduos criar.
    
    Returns:
        populacao (list): Uma lista de listas. Cada sub-lista é uma rota permutada. 
    '''
    populacao = []

    # Criação dos pontos de entrega que serão utilizados
    pontos_entrega = list(range(1, num_pontos))
    
    # Criação dos indivíduos(Obs: uma população é composta por diversos indivíduos)
    for i in range(tamanho_populacao):
        individuo = random.sample(pontos_entrega, len(pontos_entrega))
        populacao.append(individuo)

    return populacao

def calcular_custo(individuo, matriz_distancias):
    ''' Calcula o custo de cada rota(indivíduo).
    
    Parameters:
        individuo (list): Lista de índices dos pontos de entrega.
        matriz_distancias (list): Matriz NxN com as distâncias.
    
    Returns:
        custo_total (int): A distância total de um determinado indivíduo. 
    '''
    custo_total = 0

    # Saída do restaurante até o primeiro ponto de entrega
    primeiro_ponto = individuo[0]
    custo_total += matriz_distancias[0][primeiro_ponto]

    # Caminho entre os pontos de entrega
    for i in range(len(individuo)-1):
        ponto_atual = individuo[i]
        proximo_ponto = individuo[i+1]
        custo_total += matriz_distancias[ponto_atual][proximo_ponto]

    # Caminho do último ponto até a o Restaurante
    ultimo_ponto = individuo[-1]
    custo_total += matriz_distancias[ultimo_ponto][0]

    return custo_total

def calcular_fitness(custo):
    ''' Transforma o custo em uma nota de aptidão(fitness), quanto menor o custo, maior a nota.
    
    Parameters:
        custo (int): A distância total de um determinado indivíduo(rota).
    
    Returns:
        fitness (float): Nota utilizada para selecionar os pais no AG.
    '''
    # Caso ocorra divisão por zero
    if custo == 0:
        return float('inf')
    
    fitness = 1 / custo
    return fitness

def escolher_pai(populacao, lista_fitness, num_competidores=3):
    '''Seleciona um indivíduo pai através de uma "competição" aleatória.
    
    Parameters:
        populacao (list): Lista de todos os indivíduos (rotas).
        lista_fitness (list): Lista com a nota de cada indivíduo (índices sincronizados com a lista de populacao).
        num_competidores (int): Quantos indivíduos sorteamos para comparar (padrão 3).
    
    Returns:
        pai (list): Rota do indivíduo vencedor
    '''
    # Sorteio dos índices dos indivíduos
    indices_competidores = random.sample(range(len(populacao)), num_competidores)

    # Inicialização(vencedor temporário)
    indice_vencedor = indices_competidores[0]
    fitness_vencedor = lista_fitness[indice_vencedor]

    # Comparação com os outros sorteados para ver quem é o melhor
    for i in indices_competidores[1:]:
        if lista_fitness[i] > fitness_vencedor:
            indice_vencedor = i
            fitness_vencedor = lista_fitness[i]
    
    # Indivíduo(rota) campeão
    pai = populacao[indice_vencedor]
    return pai

def criar_filho_ox1(pai_principal, pai_complementar, inicio, fim):
    '''Cria um filho utilizando a lógica do Crossover Ordenado(OX1). A função preserva uma fatia genética do pai
    principal e preenche os genes restantes seguindo a ordem dos genes do pai auxiliar.
    
    Parameters:
        pai_principal (list): Indivíduo do qual a fatia fixa será copiada.
        pai_complementar (list): Indivíduo usado para preencher os espaços vazios.
        inicio (int): Índice inicial do corte (fatia).
        fim (int): Índice final do corte (fatia).
    
    Returns:
        filho (list): Nova rota gerada pela combinação dos pais
    '''
    tamanho = len(pai_principal)
    filho = [-1] * tamanho

    # Filho compiando a fatia genética do pai principal
    filho[inicio:fim+1] = pai_principal[inicio:fim+1]

    # Preenche as posições vazias(-1) com os genes do pai coplementar
    posicao_atual = 0

    for gene in pai_complementar:
        if gene not in filho:
            # Procura lugar vazio
            while filho[posicao_atual] != -1:
                posicao_atual += 1

            # Coloca o gene no lugar vazio
            filho[posicao_atual] = gene

    return filho

def crossover_ordenado(pai1, pai2):
    ''' Realiza o cruzamento genético entre dois pais para gerar dois filhos.

    Parameters:
        pai1 (list): Rota do primeiro pai selecionado.
        pai2 (list): Rota do segundo pai selecionado.
    
    Returns:
        filhos (tuple): Tupla contendo as duas novas listas (filho1, filho2).
    '''
    tamanho = len(pai1)

    # Sorteio dos pontos para definir o trecho em que haverá um corte
    ponto_a = random.randint(0, tamanho - 1)
    ponto_b = random.randint(0, tamanho - 1)

    inicio = min(ponto_a, ponto_b)
    fim = max(ponto_a, ponto_b)

    # Gera os filhos chamando a função criar_filho_ox1
    filho1 = criar_filho_ox1(pai1, pai2, inicio, fim)
    filho2 = criar_filho_ox1(pai2, pai1, inicio, fim)

    return (filho1, filho2)

def mutacao(individuo, taxa_mutacao):
    ''' Aplica uma pequena alteração aleatória na rota para manter a diversidade genética. A mutação ocorre baseada 
    na taxa informada. Se ocorrer, dois pontos de entrega são escolhidos aleatoriamente e trocados de posição.

    Parameters:
        individuo (list): A rota que pode sofrer mutação
        taxa_mutacao (float): Probabilidade de ocorrer a mutação(varia entre 0 e 1).
    
    Returns:
        individuo (list): Retorna a rota mutada ou não.
    '''
    # Sorteia um número entre 0 e 1, o número sorteado tem que ser menor do que a taxa de mutação
    if random.random() < taxa_mutacao:
        tamanho = len(individuo)

        # Escolhe duas posições diferentes que vão ser trocadas
        i1, i2 = random.sample(range(tamanho), 2)

        # Troca dos pontos
        individuo[i1], individuo[i2] = individuo[i2], individuo[i1]

    return individuo
    
def algoritmo_genetico(conteudo_tsplib, tamanho_populacao=100, taxa_mutacao=0.01, num_geracoes=500):
    ''' Executa o ciclo evolutivo do Algoritmo Genético

    Parameters:
        conteudo_tsplib (str): O texto do arquivo de entrada no formato TSPLIB.
        tamanho_populacao (int): Quantos indivíduos vivem em cada geração.
        taxa_mutacao (float): Chance de um filho sofrer mutação.
        num_geracoes (int): Quantidade de vezes que o ciclo se repete.
    
    Returns:
        melhor_rota (list): A melhor sequência de pontos encontrados em todas as gerações.
        menor_custo (int): O custo da melhor rota.
    '''
    # Conversão do texto em formato TSPLIB para uma matriz númerica
    matriz_distancias = converter_texto_para_matriz(conteudo_tsplib)
    num_pontos = len(matriz_distancias)

    # Criação da primeira geração
    populacao = gerar_populacao_inicial(num_pontos, tamanho_populacao)

    melhor_rota = None
    menor_custo = float("inf")

    # Loop das gerações
    for geracao in range(num_geracoes):
        lista_fitness = []

        for individuo in populacao:
            custo = calcular_custo(individuo, matriz_distancias)
            fitness = calcular_fitness(custo)
            lista_fitness.append(fitness)

            # Verifica se o custo encontrad é o menor
            if custo < menor_custo:
                menor_custo = custo
                melhor_rota = list(individuo)

        # Nova Geração
        nova_populacao = []

        # Loop roda até a nova população ser preenchida
        while len(nova_populacao) < tamanho_populacao:
            # Seleção dos pais
            pai1 = escolher_pai(populacao, lista_fitness)
            pai2 = escolher_pai(populacao, lista_fitness)

            # Cruzamento
            filho1, filho2 = crossover_ordenado(pai1, pai2)

            # Mutação
            filho1 = mutacao(filho1, taxa_mutacao)
            filho2 = mutacao(filho2, taxa_mutacao)

            # Adiciona os filhos na nova população
            nova_populacao.append(filho1)
            nova_populacao.append(filho2)
    
        # Nova geração se torna a primeira
        populacao = nova_populacao

    return melhor_rota, menor_custo

def listar_pontos_ordenados(caminho_arquivo):
    ''' Lê o arquivo e retorna uma lista dos nomes dos pontos já ordenada.

    A ordenação segue a regra do AG (Restaurante 'R' no índice 0, seguido 
    pelos demais pontos em ordem alfabética), servindo de índice para tradução.

    Parameters:
        caminho_arquivo (str): Arquivo .txt contendo a matriz.

    Returns:
        pontos (list): Lista ordenada
    '''
    pontos = []

    try:
        with open(caminho_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
            matriz_bruta = [linha.strip().split() for linha in linhas[1:]]

            for linha in matriz_bruta:
                for valor in linha:
                    if valor != "0":
                        pontos.append(valor)
        
        # Ordenação "R" no começo e os pontos restnates em orddem alfabética
        pontos.sort(key=lambda k: (k != 'R', k))
        return pontos

    except FileNotFoundError:
        return []
    
if __name__ == "__main__":
    arquivo_matriz = "matriz.txt"
    
    print(f"\n=== Projeto FlyFood: Algoritmo Genético ===")
    print(f"Lendo instância do arquivo: {arquivo_matriz}")

    # Recupera os nomes reais (R, A, B...)
    mapeamento_nomes = listar_pontos_ordenados(arquivo_matriz)
    
    if not mapeamento_nomes:
        print("Erro: Arquivo não encontrado ou vazio. Verifique o nome do arquivo.")
        exit()

    print(f"Pontos identificados (Ordem Interna): {mapeamento_nomes}")
    

    # Prepara os dados para a conversão da Matriz txt para Texto TSPLIB
    texto_tsplib = converter_para_tsplib(arquivo_matriz)
    
    # Executa o Algoritmo Genético com cronômetro
    print("\nIniciando Evolução... (Aguarde)")
    start_time = time.time()
    
    # Ajustes dos parâmetros
    melhor_rota_indices, menor_custo = algoritmo_genetico(
        texto_tsplib, 
        tamanho_populacao=300,
        taxa_mutacao=0.05,
        num_geracoes=1000
    )
    
    end_time = time.time()
    tempo_execucao = end_time - start_time

    # Exibição dos Resultados Finais
    rota_completa_indices = [0] + melhor_rota_indices + [0]
    
    # Traduz os números de volta para letras usando nossa lista ordenada
    rota_letras = [mapeamento_nomes[i] for i in rota_completa_indices]
    
    # Ajuste do formato: "R -> B -> A -> C -> R"
    rota_formatada = " -> ".join(rota_letras)

    print("-" * 60)
    print("RESULTADO FINAL (Otimização Genética)")
    print("-" * 60)
    print(f"Melhor Custo Encontrado: {menor_custo}")
    print(f"Melhor Rota: {rota_formatada}")
    print(f"Tempo de Execução: {tempo_execucao:.5f} segundos")
    print("-" * 60)
