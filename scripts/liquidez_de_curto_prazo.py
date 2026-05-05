# Importa o módulo os, usado para acessar variáveis de ambiente
import os

# Importa a biblioteca pandas, usada para manipulação e análise de dados
import pandas as pd

# Importa a função create_engine do SQLAlchemy, usada para criar conexão com o banco
from sqlalchemy import create_engine

# Importa NullPool para evitar o uso de pool persistente de conexões
from sqlalchemy.pool import NullPool

# Importa numpy, usado para trabalhar com cálculos numéricos e valores nulos
import numpy as np


# Exibe uma mensagem indicando o início da execução da métrica
print("🚀 Iniciando Métrica - Liquidez de Curto Prazo...")


# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")


# Cria a conexão com o banco de dados usando a URL armazenada na variável de ambiente
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


# Define a função responsável por calcular e salvar a métrica de liquidez de curto prazo
def calcular_e_salvar_liquidez_curto_prazo(conexao_engine):

    # Query SQL que seleciona as colunas necessárias da tabela de liquidez dos FIDCs
    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",              -- CNPJ identificador do fundo/classe
        "DENOM_SOCIAL",                   -- Nome/denominação social do fundo
        "DT_COMPTC",                      -- Data de competência da informação
        "TAB_X_VL_LIQUIDEZ_0",            -- Valor com liquidez imediata
        "TAB_X_VL_LIQUIDEZ_30",           -- Valor com liquidez em até 30 dias
        "TAB_X_VL_LIQUIDEZ_60",           -- Valor com liquidez em até 60 dias
        "TAB_X_VL_LIQUIDEZ_90",           -- Valor com liquidez em até 90 dias
        "TAB_X_VL_LIQUIDEZ_180",          -- Valor com liquidez em até 180 dias
        "TAB_X_VL_LIQUIDEZ_360",          -- Valor com liquidez em até 360 dias
        "TAB_X_VL_LIQUIDEZ_MAIOR_360"     -- Valor com liquidez acima de 360 dias
    FROM "inf_mensal_fidc_tab_X_5"
    '''

    # Executa a consulta SQL no banco e carrega o resultado em um DataFrame pandas
    df = pd.read_sql_query(query, conexao_engine)

    # Lista com todas as colunas de liquidez que serão usadas no cálculo
    cols = [
        "TAB_X_VL_LIQUIDEZ_0",
        "TAB_X_VL_LIQUIDEZ_30",
        "TAB_X_VL_LIQUIDEZ_60",
        "TAB_X_VL_LIQUIDEZ_90",
        "TAB_X_VL_LIQUIDEZ_180",
        "TAB_X_VL_LIQUIDEZ_360",
        "TAB_X_VL_LIQUIDEZ_MAIOR_360"
    ]

    # Converte todas as colunas de liquidez para formato numérico
    # Caso algum valor não possa ser convertido, ele vira NaN
    # Em seguida, os valores NaN são substituídos por 0
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Calcula a liquidez de curto prazo
    # Fórmula: liquidez imediata + 30 dias + 60 dias + 90 dias
    df["liquidez_curto_prazo"] = (
        df["TAB_X_VL_LIQUIDEZ_0"] +
        df["TAB_X_VL_LIQUIDEZ_30"] +
        df["TAB_X_VL_LIQUIDEZ_60"] +
        df["TAB_X_VL_LIQUIDEZ_90"]
    )

    # Calcula a liquidez total do fundo
    # Soma todas as faixas de liquidez: 0, 30, 60, 90, 180, 360 e maior que 360 dias
    df["liquidez_total"] = df[cols].sum(axis=1)

    # Calcula a métrica de liquidez de curto prazo
    # Fórmula: liquidez de curto prazo / liquidez total
    # Caso a liquidez total seja 0, retorna NaN para evitar divisão por zero
    df["metrica_liquidez_curto_prazo"] = np.where(
        df["liquidez_total"] > 0,
        df["liquidez_curto_prazo"] / df["liquidez_total"],
        np.nan
    )

    # Limita a métrica entre 0 e 1
    # Isso evita resultados negativos ou acima de 100%
    df["metrica_liquidez_curto_prazo"] = df["metrica_liquidez_curto_prazo"].clip(0, 1)

    # Cria um DataFrame final apenas com as colunas que serão salvas no banco
    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",                 # Identificador do fundo/classe
        "DENOM_SOCIAL",                      # Nome do fundo
        "DT_COMPTC",                         # Data de competência
        "liquidez_curto_prazo",              # Soma dos valores que voltam em até 90 dias
        "liquidez_total",                    # Soma total de todas as faixas de liquidez
        "metrica_liquidez_curto_prazo"       # Resultado da métrica calculada
    ]].copy()

    # Salva o resultado no banco de dados
    df_resultado.to_sql(
        "score_liquidez_curto_prazo",  # Nome da tabela que será criada/substituída
        conexao_engine,                # Conexão com o banco de dados
        if_exists="replace",           # Substitui a tabela caso ela já exista
        index=False                    # Não salva o índice do DataFrame como coluna
    )

    # Exibe uma mensagem confirmando que o processo foi concluído com sucesso
    print("✅ score_liquidez_curto_prazo salvo com sucesso!")


# Executa a função, passando a conexão criada com o banco de dados
calcular_e_salvar_liquidez_curto_prazo(engine)
