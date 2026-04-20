
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

print("Iniciando Motor de Risco – Score 2 (Liquidez Estrutural v2)...")

# =====================================================
# 1. Variáveis de ambiente
# =====================================================
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não encontrada no .env")

engine = create_engine(DATABASE_URL)

# =====================================================
# 2. Tabelas físicas (PostgreSQL → tudo minúsculo)
# =====================================================
TABELA_X5 = "inf_mensal_fidc_tab_X_5"
TABELA_I  = "inf_mensal_fidc_tab_I"

# =====================================================
# 3. Função principal
# =====================================================

def calcular_score_2_liquidez(engine):
    print(f"Lendo dados da {TABELA_X5} (Liquidez dos Ativos)...")


    query_x5 = f"""
        SELECT
            cnpj_fundo_classe,
            tab_x_vl_liquidez_0,
            tab_x_vl_liquidez_30,
            tab_x_vl_liquidez_60,
            tab_x_vl_liquidez_90,
            tab_x_vl_liquidez_maior_360
        FROM {TABELA_X5}
    """

    df_x5 = pd.read_sql(query_x5, engine)

    print(f"Lendo dados da {TABELA_I} (Estrutura do Fundo)...")

    query_i = f"""
        SELECT
            cnpj_fundo_classe,
            tab_i2_vl_carteira AS valor_carteira,
            prazo_pagto_resgate
        FROM {TABELA_I}
    """

    df_i = pd.read_sql(query_i, engine)

    # =====================================================
    # 4. Integração das bases
    # =====================================================
    df = df_x5.merge(df_i, on="cnpj_fundo_classe", how="inner")

    # =====================================================
    # 5. Cálculo do perfil de maturidade
    # =====================================================
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

    # =====================================================
    # 6. Regra de descasamento de liquidez (INSIGHT-CHAVE)
    # =====================================================
    df["flag_risco_liquidez"] = (
        (df["prazo_pagto_resgate"] <= 90)
        & (df["pct_curto_prazo"] < 20)
    ).astype(int)

    # =====================================================
    # 7. Resultado final
    # =====================================================
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

    print("Score 2 – Liquidez Estrutural v2 processado com sucesso!")

# =====================================================
# 8. Execução controlada
# =====================================================
if __name__ == "__main__":
    try:
        calcular_score_2_liquidez(engine)
    except Exception as e:
        print("Erro na execução do Score 2 v2:", str(e))
