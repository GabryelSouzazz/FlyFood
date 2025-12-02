# 🚁 FlyFood: Otimização de Rotas para Entrega com Drones

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Concluído-green?style=for-the-badge)


## 📌 Sobre o Projeto

Este projeto foi desenvolvido como parte da disciplina de **Projeto Interdisciplinar de Sistemas de Informação** na **UFRPE**. O objetivo é resolver um problema de logística urbana onde um drone deve entregar produtos em pontos específicos e retornar à base, minimizando o consumo de bateria (distância percorrida).

O problema é uma variação do clássico **Problema do Caixeiro Viajante (TSP)**. Para solucioná-lo, foram implementadas e comparadas duas abordagens algorítmicas distintas:
1.  **Força Bruta (Exata):** Para validação em cenários pequenos.
2.  **Algoritmo Genético (Meta-heurística):** Para viabilidade em cenários de larga escala.

---

## 🎯 Cenários de Teste

O projeto aborda dois tipos de instâncias de problema:

| Cenário | Descrição | Complexidade | Métrica de Distância |
| :--- | :--- | :--- | :--- |
| **FlyFood** | Matriz de grade representando um bairro. | Baixa/Média ($N \le 15$) | Manhattan $( x_1-x_2 ) + (y_1-y_2$) 
| **Brazil58** | Instância oficial da TSPLIB com 58 cidades. | Alta ($58! \approx 10^{78}$) | Pesos Explícitos (Matriz) |

---

## 🧬 Algoritmos Implementados

### 1. Força Bruta (Brute Force)
* **Lógica:** Gera todas as permutações possíveis dos pontos de entrega ($N!$).
* **Complexidade:** $O(N!)$.
* **Resultado:** Garante matematicamente a melhor rota possível.
* **Limitação:** Torna-se inviável computacionalmente para $N > 12$.

### 2. Algoritmo Genético (Genetic Algorithm)
* **Lógica:** Simula o processo de evolução natural com populações de soluções.
* **Componentes:**
    * **Representação:** Permutação de inteiros/strings.
    * **Seleção:** Torneio ($k=3$).
    * **Cruzamento:** Order Crossover (OX1) para evitar duplicação de cidades.
    * **Mutação:** Swap Mutation (Troca de dois genes).
    * **Elitismo:** Preservação da melhor solução global.
* **Vantagem:** Encontra soluções ótimas ou sub-ótimas em tempo polinomial controlado $O(G \cdot P \cdot N)$.

---

## 📊 Resultados e Performance

### Comparativo: Força Bruta vs. Genético (Cenário FlyFood)
Enquanto a Força Bruta sofre com crescimento exponencial, o Algoritmo Genético mantém o tempo de execução estável.

| Pontos ($N$) | Tempo Força Bruta (s) | Tempo Genético (s) |
| :---: | :---: | :---: |
| 5 | 0.002 | ~5.8 |
| 10 | 14.36 | ~4.8 |
| 12 | **3830.84** (1h+) | **~8.12** |

### Escalabilidade (Cenário Brazil58)
Na instância de 58 cidades, onde a força bruta falharia, o Algoritmo Genético obteve:
* **Melhor Custo Encontrado:** 27.006 (Gap de ~6.3% em relação ao ótimo conhecido).
* **Tempo de Execução:** ~4 a 6 minutos.
* **Parâmetros:** População de 1800, 2000 Gerações, Mutação de 5%.

---

## 🚀 Como Executar

### Pré-requisitos
* Python 3.8+
