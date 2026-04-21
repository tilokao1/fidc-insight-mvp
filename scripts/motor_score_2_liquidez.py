import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# =====================================================
# Configuração
# =====================================================
DATABASE_URL = os.getenv("DATABASE_URL")

# =====================================================
# Função principal – Score 2 (Liquidez Estrutural)
# =====================================================
def calcular_score_2_liquidez():

    print("Iniciando cálculo do Score 2 – Risco de Liquidez (v2)...")

    engine = create_engine(
        os.getenv("DATABASE_URL"),
        poolclass=NullPool,)


    # -------------------------------------------------
    # Leitura da Tabela X_5 – Perfil de Liquidez
    # -------------------------------------------------
    query_x5 = text("""
        SELECT
            "CNPJ_FUNDO_CLASSE",
            "TAB_X_VL_LIQUIDEZ_0",
            "TAB_X_VL_LIQUIDEZ_30",
            "TAB_X_VL_LIQUIDEZ_60",
            "TAB_X_VL_LIQUIDEZ_90",
            "TAB_X_VL_LIQUIDEZ_MAIOR_360"
        FROM "inf_mensal_fidc_tab_X_5"
    """)

    df_x5 = pd.read_sql(query_x5, engine)

    # -------------------------------------------------
    # Leitura da Tabela I – Passivo do Fundo
    # -------------------------------------------------
    query_i = text("""
        SELECT
            "CNPJ_FUNDO_CLASSE",
            "TAB_I2_VL_CARTEIRA" AS valor_carteira,
            "PRAZO_PAGTO_RESGATE"
        FROM "inf_mensal_fidc_tab_I"
    """)

    df_i = pd.read_sql(query_i, engine)

    # -------------------------------------------------
    # Integração das bases
    # -------------------------------------------------
    df = df_x5.merge(df_i, on="CNPJ_FUNDO_CLASSE", how="inner")

    # -------------------------------------------------
    # Cálculo do perfil de maturidade
    # -------------------------------------------------
    df["vl_curto_prazo"] = (
        df["TAB_X_VL_LIQUIDEZ_0"]
        + df["TAB_X_VL_LIQUIDEZ_30"]
        + df["TAB_X_VL_LIQUIDEZ_60"]
        + df["TAB_X_VL_LIQUIDEZ_90"]
    )

    df["pct_curto_prazo"] = (df["vl_curto_prazo"] / df["valor_carteira"]) * 100
    df["pct_longo_prazo"] = (
        df["TAB_X_VL_LIQUIDEZ_MAIOR_360"] / df["valor_carteira"]
    ) * 100

    # -------------------------------------------------
    # Regra de descasamento de liquidez (Blueprint v2)
    # -------------------------------------------------
    df["PRAZO_PAGTO_RESGATE"] = pd.to_numeric(df["PRAZO_PAGTO_RESGATE"], errors="coerce").fillna(0)
    df["flag_risco_liquidez"] = (
        (df["PRAZO_PAGTO_RESGATE"] <= 90)
        & (df["pct_curto_prazo"] < 20)
    ).astype(int)
    # -------------------------------------------------
    # Tabela final do Score 2
    # -------------------------------------------------
    resultado = df[
        [
            "CNPJ_FUNDO_CLASSE",
            "pct_curto_prazo",
            "pct_longo_prazo",
            "PRAZO_PAGTO_RESGATE",
            "flag_risco_liquidez"
        ]
    ]

    print("Gravando tabela score_2_liquidez_v2...")

    resultado.to_sql(
        "score_2_metricas_1_e_2",
        engine,
        if_exists="replace",
        index=False
    )

    print("Criando índices para otimização de JOINS...")
    with engine.begin() as conn:
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_score2_cnpj ON "score_2_metricas_1_e_2" ("CNPJ_FUNDO_CLASSE");'))

    print("Score 2 – Liquidez Estrutural calculado com sucesso!")

# =====================================================
# Execução
# =====================================================
if __name__ == "__main__":
    calcular_score_2_liquidez()