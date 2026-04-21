import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import numpy as np
import os

print("🚀 Iniciando Métrica 1.4 - Risco Oculto...")

# Conexão
engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,
)

def calcular_e_salvar_metrica_1_4(conexao_engine):
    print("1. Lendo dados da tabela inf_mensal_fidc_tab_X_3...")

    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_X_VL_RENTAB_MES"
    FROM "inf_mensal_fidc_tab_X_3"
    '''

    df = pd.read_sql_query(query, conexao_engine)

    if df.empty:
        print("Erro: Nenhum dado encontrado.")
        return

    print("2. Tratando dados...")

    df["TAB_X_VL_RENTAB_MES"] = pd.to_numeric(
        df["TAB_X_VL_RENTAB_MES"], errors="coerce"
    )

    df["TAB_X_VL_RENTAB_MES"] = df["TAB_X_VL_RENTAB_MES"].fillna(0)

    print("3. Calculando proxy de risco...")

    # valor absoluto da rentabilidade
    df["rentabilidade_absoluta"] = df["TAB_X_VL_RENTAB_MES"].abs()

    print("4. Normalizando (percentil 95)...")

    p95 = df["rentabilidade_absoluta"].quantile(0.95)

    # evita divisão por zero
    if p95 == 0:
        p95 = 1

    df["metrica_1_4_risco_oculto"] = df["rentabilidade_absoluta"] / p95

    # limita entre 0 e 1
    df["metrica_1_4_risco_oculto"] = df[
        "metrica_1_4_risco_oculto"
    ].clip(lower=0, upper=1)

    print("5. Selecionando colunas finais...")

    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_X_VL_RENTAB_MES",
        "rentabilidade_absoluta",
        "metrica_1_4_risco_oculto"
    ]].copy()

    print("6. Salvando no Supabase...")

    df_resultado.to_sql(
        "score_1_metrica_4",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    print("✅ Métrica 1.4 salva com sucesso na tabela score_1_metrica_4!")

try:
    calcular_e_salvar_metrica_1_4(engine)
except Exception as e:
    print(f"Erro durante a execução: {e}")
