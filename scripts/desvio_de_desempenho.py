import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import numpy as np
import os

print("🚀 Iniciando Métrica - Aderência ao Desempenho Esperado...")


# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")


# Cria a conexão com o banco usando a URL armazenada na variável de ambiente
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


def calcular_e_salvar_aderencia_desempenho(conexao_engine):
    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_X_PR_DESEMP_ESPERADO",
        "TAB_X_PR_DESEMP_REAL"
    FROM "inf_mensal_fidc_tab_X_6"
    '''

    df = pd.read_sql_query(query, conexao_engine)

    df["TAB_X_PR_DESEMP_ESPERADO"] = pd.to_numeric(
        df["TAB_X_PR_DESEMP_ESPERADO"], errors="coerce"
    )

    df["TAB_X_PR_DESEMP_REAL"] = pd.to_numeric(
        df["TAB_X_PR_DESEMP_REAL"], errors="coerce"
    )

    df = df.dropna(subset=[
        "TAB_X_PR_DESEMP_ESPERADO",
        "TAB_X_PR_DESEMP_REAL"
    ])

    # Diferença absoluta entre o desempenho real e o esperado
    df["desvio_desempenho"] = (
        df["TAB_X_PR_DESEMP_REAL"] - df["TAB_X_PR_DESEMP_ESPERADO"]
    ).abs()

    # Regra simples e entendível:
    # até 5 pontos de diferença = bom
    # 20 pontos ou mais = muito ruim
    limite_bom = 5
    limite_ruim = 20

    df["score_aderencia_desempenho"] = 100 - (
        (df["desvio_desempenho"] - limite_bom) / (limite_ruim - limite_bom) * 100
    )

    df["score_aderencia_desempenho"] = df["score_aderencia_desempenho"].clip(0, 100)

    df["classificacao_desempenho"] = np.select(
        [
            df["score_aderencia_desempenho"] >= 80,
            df["score_aderencia_desempenho"] >= 60,
            df["score_aderencia_desempenho"] >= 40
        ],
        [
            "Muito aderente",
            "Aderente",
            "Atenção"
        ],
        default="Fora do esperado"
    )

    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_X_PR_DESEMP_ESPERADO",
        "TAB_X_PR_DESEMP_REAL",
        "desvio_desempenho",
        "score_aderencia_desempenho",
        "classificacao_desempenho"
    ]].copy()

    df_resultado.to_sql(
        "score_aderencia_desempenho",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    print("✅ score_aderencia_desempenho salvo com sucesso!")

try:
    calcular_e_salvar_aderencia_desempenho(engine)
except Exception as e:
    print(f"Erro durante a execução: {e}")
