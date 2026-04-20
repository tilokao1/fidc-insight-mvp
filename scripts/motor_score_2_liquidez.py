
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
# 2. Nomes físicos das tabelas (CONFIRMADOS)
# =====================================================
TABELA_X5 = "inf_mensal_fidc_tab_X_5"
TABELA_I  = "tabela_i"  # ajuste apenas se o nome físico for diferente

# =====================================================
# 3. Função principal
# =====================================================
def calcular_score_2_liquidez(engine):
    print(f"Lendo dados da {TABELA_X5} (Liquidez dos Ativos)...")

    query_x5 = f"""
        SELECT
            CNPJ_FUNDO_CLASSE,
            TAB_X_VL_LIQUIDEZ_0,
            TAB_X_VL_LIQUIDEZ_30,
            TAB_X_VL_LIQUIDEZ_60,
            TAB_X_VL_LIQUIDEZ_90,
            TAB_X_VL_LIQUIDEZ_MAIOR_360
        FROM {TABELA_X5}
    """

    df_x5 = pd.read_sql(query_x5, engine)

    print(f"Lendo dados da {TABELA_I} (Estrutura do Fundo)...")

    query_i = f"""
        SELECT
            CNPJ_FUNDO_CLASSE,
            TAB_I2_VL_CARTEIRA AS valor_carteira,
            PRAZO_PAGTO_RESGATE
        FROM {TABELA_I}
    """

    df_i = pd.read_sql(query_i, engine)

    # =====================================================
    # 4. Integração das bases
    # =====================================================
    df = df_x5.merge(df_i, on="CNPJ_FUNDO_CLASSE", how="inner")

    # =====================================================
    # 5. Cálculo do perfil de maturidade
    # =====================================================
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

    # =====================================================
    # 6. Regra de descasamento de liquidez (INSIGHT-CHAVE)
    # =====================================================
    df["flag_risco_liquidez"] = (
        (df["PRAZO_PAGTO_RESGATE"] <= 90)
        & (df["pct_curto_prazo"] < 20)
    ).astype(int)

    # =====================================================
    # 7. Resultado final
    # =====================================================
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
