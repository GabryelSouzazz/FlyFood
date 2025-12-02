import random
import time

def ler_matriz_brazil58(caminho_arquivo):
    ''' Lê o arquivo brazil58.tsp no formato UPPER_ROW e monta a matriz completa. '''
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()
            
        # Separa o cabeçalho dos dados
        linhas = conteudo.split('\n')
        dados_brutos = []
        lendo_secao = False
        
        for linha in linhas:
            linha = linha.strip()
            if linha == "EDGE_WEIGHT_SECTION":
                lendo_secao = True
                continue
            if linha == "EOF":
                break
            
            if lendo_secao and linha:
                # Pega todos os números da linha e adiciona na lista plana
                partes = linha.split()
                for p in partes:
                    # Filtra caso tenha sobrado algum caractere estranho
                    if p.isdigit():
                        dados_brutos.append(int(p))

        # Monta a Matriz 58x58
        dimensao = 58
        matriz = [[0 for _ in range(dimensao)] for _ in range(dimensao)]
        
        contador = 0
        # O formato UPPER_ROW preenche:
        # Linha 0: dist(0,1), dist(0,2)...
        # Linha 1: dist(1,2), dist(1,3)...
        for i in range(dimensao):
            for j in range(i + 1, dimensao):
                if contador < len(dados_brutos):
                    valor = dados_brutos[contador]
                    matriz[i][j] = valor
                    matriz[j][i] = valor # Espelha para a parte de baixo (Simetria)
                    contador += 1
                    
        return matriz

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None

def gerar_populacao_inicial(num_pontos, tamanho_populacao):
    populacao = []

    pontos_entrega = list(range(1, num_pontos))
    
    for _ in range(tamanho_populacao):
        individuo = random.sample(pontos_entrega, len(pontos_entrega))
        populacao.append(individuo)
    return populacao

def calcular_custo(individuo, matriz_distancias):
    custo_total = 0
    primeiro_ponto = individuo[0]
    custo_total += matriz_distancias[0][primeiro_ponto]

    for i in range(len(individuo)-1):
        ponto_atual = individuo[i]
        proximo_ponto = individuo[i+1]
        custo_total += matriz_distancias[ponto_atual][proximo_ponto]

    ultimo_ponto = individuo[-1]
    custo_total += matriz_distancias[ultimo_ponto][0]
    return custo_total

def calcular_fitness(custo):
    if custo == 0: return float('inf')
    return 1 / custo

def escolher_pai(populacao, lista_fitness, num_competidores=3):
    indices = random.sample(range(len(populacao)), num_competidores)
    indice_vencedor = indices[0]
    for i in indices[1:]:
        if lista_fitness[i] > lista_fitness[indice_vencedor]:
            indice_vencedor = i
    return populacao[indice_vencedor]

def criar_filho_ox1(pai_principal, pai_complementar, inicio, fim):
    tamanho = len(pai_principal)
    filho = [-1] * tamanho
    filho[inicio:fim+1] = pai_principal[inicio:fim+1]
    
    posicao_atual = 0
    for gene in pai_complementar:
        if gene not in filho:
            while filho[posicao_atual] != -1:
                posicao_atual += 1
            filho[posicao_atual] = gene
    return filho

def crossover_ordenado(pai1, pai2):
    tamanho = len(pai1)
    ponto_a = random.randint(0, tamanho - 1)
    ponto_b = random.randint(0, tamanho - 1)
    inicio = min(ponto_a, ponto_b)
    fim = max(ponto_a, ponto_b)
    
    f1 = criar_filho_ox1(pai1, pai2, inicio, fim)
    f2 = criar_filho_ox1(pai2, pai1, inicio, fim)
    return (f1, f2)

def mutacao(individuo, taxa_mutacao):
    if random.random() < taxa_mutacao:
        tamanho = len(individuo)
        i1, i2 = random.sample(range(tamanho), 2)
        individuo[i1], individuo[i2] = individuo[i2], individuo[i1]
    return individuo

def algoritmo_genetico(matriz_distancias, tamanho_populacao, taxa_mutacao, num_geracoes):
    ''' Executa o ciclo evolutivo do Algoritmo Genético com ELITISMO.

    Parameters:
        matriz_distancias (list): Matriz NxN com as distâncias.
        tamanho_populacao (int): Quantos indivíduos vivem em cada geração.
        taxa_mutacao (float): Chance de um filho sofrer mutação.
        num_geracoes (int): Quantidade de vezes que o ciclo se repete.
    
    Returns:
        melhor_rota (list): A melhor sequência de pontos encontrados.
        menor_custo (int): O custo da melhor rota.
    '''
    num_pontos = len(matriz_distancias)
    
    # Criação da primeira geração
    populacao = gerar_populacao_inicial(num_pontos, tamanho_populacao)
    
    melhor_rota = None
    menor_custo = float("inf")
    
    # Histórico para acompanhar
    historico_custos = []

    # Loop das gerações
    for geracao in range(num_geracoes):
        lista_fitness = []
        
        for individuo in populacao:
            custo = calcular_custo(individuo, matriz_distancias)
            
            # Atualiza o Recorde Global se necessário
            if custo < menor_custo:
                menor_custo = custo
                melhor_rota = list(individuo)
            
            # Calcula fitness (1/custo)
            fitness = calcular_fitness(custo)
            lista_fitness.append(fitness)
            
        # Log de progresso a cada 100 gerações (para não poluir o terminal)
        if geracao % 100 == 0:
            print(f"Geração {geracao}: Melhor custo global -> {menor_custo}")
            historico_custos.append(menor_custo)

        # Formação da Nova Geração
        nova_populacao = []
        
        # ELITISMO: Identifica e salva o melhor da geração ATUAL
        indice_elite = lista_fitness.index(max(lista_fitness))
        elite = populacao[indice_elite]
        
        # Adiciona o campeão intacto na nova população
        nova_populacao.append(list(elite))
        
        # Preenche o resto da população com filhos
        while len(nova_populacao) < tamanho_populacao:
            
            # Seleção
            pai1 = escolher_pai(populacao, lista_fitness)
            pai2 = escolher_pai(populacao, lista_fitness)
            
            # Cruzamento
            filho1, filho2 = crossover_ordenado(pai1, pai2)
            
            # Mutação
            filho1 = mutacao(filho1, taxa_mutacao)
            filho2 = mutacao(filho2, taxa_mutacao)
            
            # Adiciona Filho 1
            nova_populacao.append(filho1)
            
            # Adiciona Filho 2 
            if len(nova_populacao) < tamanho_populacao:
                nova_populacao.append(filho2)
        
        # A nova geração assume o controle
        populacao = nova_populacao

    return melhor_rota, menor_custo

if __name__ == "__main__":
    arquivo = "brazil58.tsp"
    print(f"--- Solução Brazil58 via Algoritmo Genético ---")
    
    # Lê a matriz UPPER_ROW
    matriz_distancias = ler_matriz_brazil58(arquivo)
    
    if matriz_distancias:
        print(f"Matriz carregada com sucesso! Dimensão: {len(matriz_distancias)}x{len(matriz_distancias)}")
        
        start_time = time.time()
        
        melhor_rota, menor_custo = algoritmo_genetico(
            matriz_distancias,
            tamanho_populacao=1800,
            taxa_mutacao=0.05,
            num_geracoes=2000
        )
        
        end_time = time.time()
        
        print("\n" + "="*50)
        print("RESULTADO FINAL")
        print("="*50)
        print(f"Melhor Custo Encontrado: {menor_custo}")
        print(f"Melhor Custo Conhecido (Ótimo): 25395")
        
        diferenca = menor_custo - 25395
        gap = (diferenca / 25395) * 100
        print(f"Diferença do ótimo: {diferenca} (Gap: {gap:.2f}%)")
        print(f"Tempo de Execução: {end_time - start_time:.2f} segundos")
        
        # Formata a rota para exibição (ex: 0 -> 5 -> 10...)
        rota_completa = [0] + melhor_rota + [0]
        rota_str = " -> ".join(str(c) for c in rota_completa)
        print(f"\nRota (Cidades ID):\n{rota_str}")