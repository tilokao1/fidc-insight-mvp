import os
import pandas as pd
from sqlalchemy import create_engine, text

# =====================================================
# Configuração
# =====================================================
DATABASE_URL = os.getenv("DATABASE_URL")

# =====================================================
# Função principal – Score 2 (Liquidez Estrutural)
# =====================================================
def calcular_score_2_liquidez():

    print("Iniciando cálculo do Score 2 – Risco de Liquidez (v2)...")

    engine = create_engine(DATABASE_URL)

    # -------------------------------------------------
    # Leitura da Tabela X_5 – Perfil de Liquidez
    # -------------------------------------------------
    query_x5 = text("""
        SELECT
            cnpj_fundo_classe,
            tab_x_vl_liquidez_0,
            tab_x_vl_liquidez_30,
            tab_x_vl_liquidez_60,
            tab_x_vl_liquidez_90,
            tab_x_vl_liquidez_maior_360
        FROM "inf_mensal_fidc_tab_X_5"
    """)

    df_x5 = pd.read_sql(query_x5, engine)

    # -------------------------------------------------
    # Leitura da Tabela I – Passivo do Fundo
    # -------------------------------------------------
    query_i = text("""
        SELECT
            cnpj_fundo_classe,
            tab_i2_vl_carteira AS valor_carteira,
            prazo_pagto_resgate
        FROM "inf_mensal_fidc_tab_I"
    """)

    df_i = pd.read_sql(query_i, engine)

    # -------------------------------------------------
    # Integração das bases
    # -------------------------------------------------
    df = df_x5.merge(df_i, on="cnpj_fundo_classe", how="inner")

    # -------------------------------------------------
    # Cálculo do perfil de maturidade
    # -------------------------------------------------
    df["vl_curto_prazo"] = (
        df["tab_x_vl_liquidez_0"]
        + df["tab_x_vl_liquidez_30"]
        + df["tab_x_vl_liquidez_60"]
        + df["tab_x_vl_liquidez_90"]
    )

    df["pct_curto_prazo"] = (df["vl_curto_prazo"] / df["valor_carteira"]) * 100
    df["pct_longo_prazo"] = (
        df["tab_x_vl_liquidez_maior_360"] / df["valor_carteira"]
    ) * 100

    # -------------------------------------------------
    # Regra de descasamento de liquidez (Blueprint v2)
    # -------------------------------------------------
    df["flag_risco_liquidez"] = (
        (df["prazo_pagto_resgate"] <= 90)
        & (df["pct_curto_prazo"] < 20)
    ).astype(int)

    # -------------------------------------------------
    # Tabela final do Score 2
    # -------------------------------------------------
    resultado = df[
        [
            "cnpj_fundo_classe",
            "pct_curto_prazo",
            "pct_longo_prazo",
            "prazo_pagto_resgate",
            "flag_risco_liquidez"
        ]
    ]

    print("Gravando tabela score_2_liquidez_v2...")

    resultado.to_sql(
        "score_2_liquidez_v2",
        engine,
        if_exists="replace",
        index=False
    )

    print("Score 2 – Liquidez Estrutural calculado com sucesso!")

# =====================================================
# Execução
# =====================================================
if __name__ == "__main__":
    calcular_score_2_liquidez()