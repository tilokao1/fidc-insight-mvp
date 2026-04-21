import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv
import numpy as np

print("🚀 Iniciando Métrica 1.1 - Taxa de Inadimplência Atual...")

# Carrega variáveis de ambiente
load_dotenv()

# Cria conexão com o banco
engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,
)
def calcular_e_salvar_metrica_1_1(conexao_engine):
    print("1. Lendo dados da tabela inf_mensal_fidc_tab_I...")

    query = '''
    SELECT
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_I2_VL_CARTEIRA",
        "TAB_I2A3_VL_CRED_INAD"
    FROM "inf_mensal_fidc_tab_I"
    '''

    df = pd.read_sql_query(query, conexao_engine)

    if df.empty:
        print("Erro: Nenhum dado encontrado na tabela.")
        return

    print("2. Tratando dados...")

    df["TAB_I2_VL_CARTEIRA"] = pd.to_numeric(df["TAB_I2_VL_CARTEIRA"], errors="coerce")
    df["TAB_I2A3_VL_CRED_INAD"] = pd.to_numeric(df["TAB_I2A3_VL_CRED_INAD"], errors="coerce")

    # Evita divisão por zero
    df["TAB_I2_VL_CARTEIRA"] = df["TAB_I2_VL_CARTEIRA"].replace(0, np.nan)

    # Inadimplência nula vira zero
    df["TAB_I2A3_VL_CRED_INAD"] = df["TAB_I2A3_VL_CRED_INAD"].fillna(0)

    # Remove carteiras muito pequenas para evitar ruído
    df = df[df["TAB_I2_VL_CARTEIRA"] > 1000]

    print("3. Calculando métrica 1.1...")

    df["metrica_1_1_taxa_inadimplencia_atual"] = (
        df["TAB_I2A3_VL_CRED_INAD"] / df["TAB_I2_VL_CARTEIRA"]
    )

    # Limita entre 0 e 1
    df["metrica_1_1_taxa_inadimplencia_atual"] = df[
        "metrica_1_1_taxa_inadimplencia_atual"
    ].clip(lower=0, upper=1)

    print("4. Selecionando colunas finais...")

    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",
        "DENOM_SOCIAL",
        "DT_COMPTC",
        "TAB_I2_VL_CARTEIRA",
        "TAB_I2A3_VL_CRED_INAD",
        "metrica_1_1_taxa_inadimplencia_atual"
    ]].copy()

    print("5. Salvando no Supabase...")

    df_resultado.to_sql(
        "score_1_metrica_1",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    print("✅ Métrica 1.1 salva com sucesso na tabela score_1_metrica_1!")

try:
    calcular_e_salvar_metrica_1_1(engine)
except Exception as e:
    print(f"Erro durante a execução: {e}")
