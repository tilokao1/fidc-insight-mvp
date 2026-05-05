# Importa o módulo os, usado para acessar variáveis de ambiente
import os

# Importa a biblioteca pandas, usada para manipulação e análise de dados em tabelas
import pandas as pd

# Importa a função create_engine do SQLAlchemy, usada para criar a conexão com o banco
from sqlalchemy import create_engine

# Importa NullPool para evitar o uso de pool persistente de conexões
from sqlalchemy.pool import NullPool

# Importa numpy, usado para trabalhar com cálculos numéricos e valores nulos
import numpy as np


# Exibe uma mensagem indicando o início da execução da métrica
print("🚀 Iniciando Métrica - Exposição de Longo Prazo...")


# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")


# Cria a conexão com o banco usando a URL armazenada na variável de ambiente
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


# Define a função responsável por calcular e salvar a métrica de exposição de longo prazo
def calcular_e_salvar_prazo_longo(conexao_engine):

    # Query SQL que seleciona as colunas necessárias da tabela de prazo dos direitos creditórios
    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",                    -- CNPJ identificador do fundo/classe
        "DENOM_SOCIAL",                         -- Nome/denominação social do fundo
        "DT_COMPTC",                            -- Data de competência da informação
        "TAB_V_A_VL_DIRCRED_PRAZO",             -- Valor total da carteira de direitos creditórios por prazo
        "TAB_V_A7_VL_PRAZO_VENC_360",           -- Valor com prazo de vencimento em até 360 dias
        "TAB_V_A8_VL_PRAZO_VENC_720",           -- Valor com prazo de vencimento em até 720 dias
        "TAB_V_A9_VL_PRAZO_VENC_1080",          -- Valor com prazo de vencimento em até 1080 dias
        "TAB_V_A10_VL_PRAZO_VENC_MAIOR_1080"    -- Valor com prazo de vencimento acima de 1080 dias
    FROM "inf_mensal_fidc_tab_V"
    '''

    # Executa a query no banco de dados e carrega o resultado em um DataFrame pandas
    df = pd.read_sql_query(query, conexao_engine)

    # Lista com as colunas numéricas que serão usadas no cálculo
    cols = [
        "TAB_V_A_VL_DIRCRED_PRAZO",
        "TAB_V_A7_VL_PRAZO_VENC_360",
        "TAB_V_A8_VL_PRAZO_VENC_720",
        "TAB_V_A9_VL_PRAZO_VENC_1080",
        "TAB_V_A10_VL_PRAZO_VENC_MAIOR_1080"
    ]

    # Converte as colunas selecionadas para valores numéricos
    # Caso algum valor não possa ser convertido, ele vira NaN
    # Em seguida, os valores NaN são substituídos por 0
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Substitui o valor total igual a 0 por NaN
    # Isso evita divisão por zero no cálculo da métrica
    df["TAB_V_A_VL_DIRCRED_PRAZO"] = df["TAB_V_A_VL_DIRCRED_PRAZO"].replace(0, np.nan)

    # Calcula o valor da carteira exposta ao longo prazo
    # Fórmula: 360 + 720 + 1080 + maior que 1080 dias
    df["prazo_longo"] = (
        df["TAB_V_A7_VL_PRAZO_VENC_360"] +
        df["TAB_V_A8_VL_PRAZO_VENC_720"] +
        df["TAB_V_A9_VL_PRAZO_VENC_1080"] +
        df["TAB_V_A10_VL_PRAZO_VENC_MAIOR_1080"]
    )

    # Calcula a métrica de exposição de longo prazo
    # Fórmula: prazo longo / total da carteira por prazo
    # O resultado é limitado entre 0 e 1
    df["metrica_prazo_longo"] = (
        df["prazo_longo"] / df["TAB_V_A_VL_DIRCRED_PRAZO"]
    ).clip(0, 1)

    # Cria um DataFrame final apenas com as colunas que serão salvas no banco
    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",             # Identificador do fundo/classe
        "DENOM_SOCIAL",                  # Nome do fundo
        "DT_COMPTC",                     # Data de competência
        "TAB_V_A_VL_DIRCRED_PRAZO",      # Valor total da carteira por prazo
        "prazo_longo",                   # Valor exposto ao longo prazo
        "metrica_prazo_longo"            # Resultado da métrica calculada
    ]].copy()

    # Salva o resultado no banco de dados
    df_resultado.to_sql(
        "score_prazo_longo",  # Nome da tabela que será criada/substituída
        conexao_engine,       # Conexão com o banco de dados
        if_exists="replace",  # Substitui a tabela caso ela já exista
        index=False           # Não salva o índice do DataFrame como coluna
    )

    # Exibe mensagem confirmando que a tabela foi salva com sucesso
    print("✅ score_prazo_longo salvo com sucesso!")


# Executa a função, passando a conexão criada com o banco de dados
calcular_e_salvar_prazo_longo(engine)
