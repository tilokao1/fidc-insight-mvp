# Importa o módulo os, usado para acessar variáveis de ambiente
import os

# Importa a biblioteca pandas, usada para manipulação e análise de dados em tabelas
import pandas as pd

# Importa a função create_engine do SQLAlchemy, usada para criar a conexão com o banco
from sqlalchemy import create_engine

# Importa NullPool para evitar o uso de pool persistente de conexões
from sqlalchemy.pool import NullPool

# Importa numpy, usado para cálculos numéricos e tratamento de valores nulos
import numpy as np


# Exibe uma mensagem indicando o início da execução da métrica
print("🚀 Iniciando Métrica - Desvio de Desempenho...")


# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")


# Cria a conexão com o banco usando a URL armazenada na variável de ambiente
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


# Define a função responsável por calcular e salvar a métrica de desvio de desempenho
def calcular_e_salvar_desvio_desempenho(conexao_engine):

    # Exibe uma mensagem informando que os dados serão lidos da tabela de origem
    print("1. Lendo dados da tabela inf_mensal_fidc_tab_X_6...")

    # Query SQL que seleciona as colunas necessárias para o cálculo da métrica
    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",        -- CNPJ identificador do fundo/classe
        "DENOM_SOCIAL",             -- Nome/denominação social do fundo
        "DT_COMPTC",                -- Data de competência da informação
        "TAB_X_PR_DESEMP_ESPERADO", -- Percentual de desempenho esperado
        "TAB_X_PR_DESEMP_REAL"      -- Percentual de desempenho real
    FROM "inf_mensal_fidc_tab_X_6"
    '''

    # Executa a query no banco de dados e carrega o resultado em um DataFrame pandas
    df = pd.read_sql_query(query, conexao_engine)

    # Verifica se a consulta retornou algum dado
    # Caso o DataFrame esteja vazio, interrompe a execução da função
    if df.empty:
        print("Erro: Nenhum dado encontrado.")
        return

    # Exibe uma mensagem indicando o início do tratamento dos dados
    print("2. Tratando dados...")

    # Converte a coluna de desempenho esperado para formato numérico
    # Valores inválidos viram NaN e depois são substituídos por 0
    df["TAB_X_PR_DESEMP_ESPERADO"] = pd.to_numeric(
        df["TAB_X_PR_DESEMP_ESPERADO"],
        errors="coerce"
    ).fillna(0)

    # Converte a coluna de desempenho real para formato numérico
    # Valores inválidos viram NaN e depois são substituídos por 0
    df["TAB_X_PR_DESEMP_REAL"] = pd.to_numeric(
        df["TAB_X_PR_DESEMP_REAL"],
        errors="coerce"
    ).fillna(0)

    # Exibe uma mensagem indicando o início do cálculo da métrica
    print("3. Calculando desvio de desempenho...")

    # Calcula o desvio absoluto entre o desempenho real e o desempenho esperado
    # Fórmula: |desempenho real - desempenho esperado|
    df["desvio_desempenho"] = (
        df["TAB_X_PR_DESEMP_REAL"] - df["TAB_X_PR_DESEMP_ESPERADO"]
    ).abs()

    # Calcula o percentil 95 dos desvios de desempenho
    # Esse valor será usado como referência para normalizar a métrica entre 0 e 1
    p95 = df["desvio_desempenho"].quantile(0.95)

    # Caso o percentil 95 seja zero, define como 1 para evitar divisão por zero
    if p95 == 0:
        p95 = 1

    # Calcula a métrica normalizada de desvio de desempenho
    # Fórmula: desvio de desempenho / percentil 95 dos desvios
    # O resultado é limitado entre 0 e 1
    df["metrica_desvio_desempenho"] = (
        df["desvio_desempenho"] / p95
    ).clip(0, 1)

    # Exibe uma mensagem indicando que as colunas finais serão selecionadas
    print("4. Selecionando colunas finais...")

    # Cria um DataFrame final apenas com as colunas que serão salvas no banco
    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",              # Identificador do fundo/classe
        "DENOM_SOCIAL",                   # Nome do fundo
        "DT_COMPTC",                      # Data de competência
        "TAB_X_PR_DESEMP_ESPERADO",       # Desempenho esperado
        "TAB_X_PR_DESEMP_REAL",           # Desempenho real
        "desvio_desempenho",              # Diferença absoluta entre real e esperado
        "metrica_desvio_desempenho"       # Métrica normalizada entre 0 e 1
    ]].copy()

    # Exibe uma mensagem indicando que o resultado será salvo no banco
    print("5. Salvando no banco de dados...")

    # Salva o resultado no banco de dados
    df_resultado.to_sql(
        "score_desvio_desempenho",  # Nome da tabela que será criada/substituída
        conexao_engine,             # Conexão com o banco de dados
        if_exists="replace",        # Substitui a tabela caso ela já exista
        index=False                 # Não salva o índice do DataFrame como coluna
    )

    # Exibe mensagem confirmando que a tabela foi salva com sucesso
    print("✅ score_desvio_desempenho salvo com sucesso!")


# Executa a função dentro de um bloco try/except
# Isso permite capturar e exibir erros sem quebrar a execução de forma brusca
try:
    calcular_e_salvar_desvio_desempenho(engine)

# Caso aconteça algum erro durante a execução, exibe a mensagem do erro
except Exception as e:
    print(f"Erro durante a execução: {e}")
