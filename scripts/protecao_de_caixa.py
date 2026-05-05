# Importa o módulo os, usado para acessar variáveis de ambiente
import os

# Importa a biblioteca pandas, usada para manipulação e análise de dados em formato de tabela
import pandas as pd

# Importa a função create_engine do SQLAlchemy, usada para criar conexão com o banco de dados
from sqlalchemy import create_engine

# Importa NullPool para evitar reutilização de conexões no pool do SQLAlchemy
from sqlalchemy.pool import NullPool

# Importa numpy, usado aqui para trabalhar com valores nulos numéricos, como np.nan
import numpy as np


# Exibe uma mensagem no terminal indicando o início da execução da métrica
print("🚀 Iniciando Métrica - Proteção de Caixa...")

# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria a conexão com o banco usando a URL armazenada em variável de ambiente
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)

def calcular_e_salvar_protecao_caixa(conexao_engine):
    # Query SQL que seleciona as colunas necessárias da tabela de informações mensais dos FIDCs
    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",  -- CNPJ identificador do fundo/classe
        "DENOM_SOCIAL",       -- Nome/denominação social do fundo
        "DT_COMPTC",          -- Data de competência da informação
        "TAB_I1_VL_DISP",     -- Valor disponível em caixa/disponibilidades
        "TAB_I_VL_ATIVO"      -- Valor total do ativo do fundo
    FROM "inf_mensal_fidc_tab_I"
    '''

    # Executa a query no banco de dados e carrega o resultado em um DataFrame pandas
    df = pd.read_sql_query(query, conexao_engine)

    # Converte a coluna de disponibilidades para número
    # Caso haja erro na conversão, transforma em NaN e depois substitui por 0
    df["TAB_I1_VL_DISP"] = pd.to_numeric(
        df["TAB_I1_VL_DISP"],
        errors="coerce"
    ).fillna(0)

    # Converte a coluna de ativo total para número
    # Caso haja erro na conversão, transforma em NaN
    # Em seguida, substitui valores 0 por NaN para evitar divisão por zero
    df["TAB_I_VL_ATIVO"] = pd.to_numeric(
        df["TAB_I_VL_ATIVO"],
        errors="coerce"
    ).replace(0, np.nan)

    # Calcula a métrica de proteção de caixa
    # Fórmula: disponibilidades / ativo total
    # O resultado é limitado entre 0 e 1 usando clip
    df["metrica_protecao_caixa"] = (
        df["TAB_I1_VL_DISP"] / df["TAB_I_VL_ATIVO"]
    ).clip(lower=0, upper=1)

    # Cria um novo DataFrame apenas com as colunas que serão salvas no banco
    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",       # Identificador do fundo/classe
        "DENOM_SOCIAL",            # Nome do fundo
        "DT_COMPTC",               # Data de competência
        "TAB_I1_VL_DISP",          # Valor disponível em caixa
        "TAB_I_VL_ATIVO",          # Valor total do ativo
        "metrica_protecao_caixa"   # Resultado da métrica calculada
    ]].copy()

    # Salva o resultado no banco de dados em uma nova tabela
    df_resultado.to_sql(
        "score_protecao_caixa",  # Nome da tabela que será criada/substituída
        conexao_engine,          # Conexão com o banco
        if_exists="replace",     # Substitui a tabela caso ela já exista
        index=False              # Não salva o índice do DataFrame como coluna
    )

    # Exibe mensagem confirmando que a tabela foi salva com sucesso
    print("✅ score_protecao_caixa salvo com sucesso!")


# Executa a função, passando a conexão com o banco de dados
calcular_e_salvar_protecao_caixa(engine)
