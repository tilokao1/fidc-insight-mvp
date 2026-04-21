import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import numpy as np
import os

print("🚀 Iniciando Métrica 1.3 - Nível de Garantia...")

# Cria conexão com o banco
engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,
)

def calcular_e_salvar_metrica_1_3(conexao_engine):
    print("1. Lendo dados da tabela inf_mensal_fidc_tab_I...")

    query_base = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_I2_VL_CARTEIRA"
    FROM "inf_mensal_fidc_tab_I"
    '''

    df_base = pd.read_sql_query(query_base, conexao_engine)

    if df_base.empty:
        print("Erro: Nenhum dado encontrado na tabela base.")
        return

    print("2. Lendo dados da tabela inf_mensal_fidc_tab_X_7...")

    query_garantia = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",
        "DT_COMPTC",
        "TAB_X_VL_GARANTIA_DIRCRED",
        "TAB_X_PR_GARANTIA_DIRCRED"
    FROM "inf_mensal_fidc_tab_X_7"
    '''

    df_garantia = pd.read_sql_query(query_garantia, conexao_engine)

    print("3. Tratando dados...")

    df_base["TAB_I2_VL_CARTEIRA"] = pd.to_numeric(df_base["TAB_I2_VL_CARTEIRA"], errors="coerce")
    df_base["TAB_I2_VL_CARTEIRA"] = df_base["TAB_I2_VL_CARTEIRA"].replace(0, np.nan)

    df_garantia["TAB_X_VL_GARANTIA_DIRCRED"] = pd.to_numeric(
        df_garantia["TAB_X_VL_GARANTIA_DIRCRED"], errors="coerce"
    )
    df_garantia["TAB_X_PR_GARANTIA_DIRCRED"] = pd.to_numeric(
        df_garantia["TAB_X_PR_GARANTIA_DIRCRED"], errors="coerce"
    )

    # Remove ruído de carteiras muito pequenas
    df_base = df_base[df_base["TAB_I2_VL_CARTEIRA"] > 1000]

    print("4. Agregando garantias por CNPJ...")

    df_garantia_agg = df_garantia.groupby("CNPJ_FUNDO_CLASSE", as_index=False).agg({
        "TAB_X_VL_GARANTIA_DIRCRED": "mean",
        "TAB_X_PR_GARANTIA_DIRCRED": "mean"
    })

    print("5. Fazendo merge com a base principal...")

    df = df_base.merge(
        df_garantia_agg,
        on="CNPJ_FUNDO_CLASSE",
        how="left"
    )

    # Garantia nula vira zero
    df["TAB_X_VL_GARANTIA_DIRCRED"] = df["TAB_X_VL_GARANTIA_DIRCRED"].fillna(0)
    df["TAB_X_PR_GARANTIA_DIRCRED"] = df["TAB_X_PR_GARANTIA_DIRCRED"].fillna(0)

    print("6. Calculando métrica 1.3...")

    df["metrica_1_3_nivel_garantia_coobrigacao"] = (
        df["TAB_X_VL_GARANTIA_DIRCRED"] / df["TAB_I2_VL_CARTEIRA"]
    )

    # Limita entre 0 e 1
    df["metrica_1_3_nivel_garantia_coobrigacao"] = df[
        "metrica_1_3_nivel_garantia_coobrigacao"
    ].clip(lower=0, upper=1)

    print("7. Selecionando colunas finais...")

    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_I2_VL_CARTEIRA",
        "TAB_X_VL_GARANTIA_DIRCRED",
        "TAB_X_PR_GARANTIA_DIRCRED",
        "metrica_1_3_nivel_garantia_coobrigacao"
    ]].copy()

    print("8. Salvando no Supabase...")

    df_resultado.to_sql(
        "score_1_metrica_3",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    print("✅ Métrica 1.3 salva com sucesso na tabela score_1_metrica_3!")

try:
    calcular_e_salvar_metrica_1_3(engine)
except Exception as e:
    print(f"Erro durante a execução: {e}")
