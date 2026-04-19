
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
# 2. Função principal
# =====================================================

def calcular_score_2_liquidez(engine):
    print("Lendo dados da Tabela X_5 (Liquidez do Ativo)...")

    query_x5 = """
        SELECT
            id_fundo,
            VL_LIQUIDEZ_1_30,
            VL_LIQUIDEZ_31_60,
            VL_LIQUIDEZ_61_90,
            VL_LIQUIDEZ_ACIMA_360
        FROM tabela_x_5
    """

    df_x5 = pd.read_sql(query_x5, engine)

    print("Lendo dados da Tabela I (Estrutura do Fundo)...")

    query_i = """
        SELECT
            id_fundo,
            TAB_I2_VL_CARTEIRA AS valor_carteira,
            PRAZO_PAGTO_RESGATE
        FROM tabela_i
    """

    df_i = pd.read_sql(query_i, engine)

    # =====================================================
    # 3. Integração das bases
    # =====================================================
    df = df_x5.merge(df_i, on="id_fundo", how="inner")

    # =====================================================
    # 4. Cálculo do perfil de maturidade
    # =====================================================
    df["vl_curto_prazo"] = (
        df["VL_LIQUIDEZ_1_30"]
        + df["VL_LIQUIDEZ_31_60"]
        + df["VL_LIQUIDEZ_61_90"]
    )

    df["pct_curto_prazo"] = (df["vl_curto_prazo"] / df["valor_carteira"]) * 100
    df["pct_longo_prazo"] = (df["VL_LIQUIDEZ_ACIMA_360"] / df["valor_carteira"]) * 100

    # =====================================================
    # 5. Regra de descasamento de liquidez (Insight-chave)
    # =====================================================
    df["flag_risco_liquidez"] = (
        (df["PRAZO_PAGTO_RESGATE"] <= 90)
        & (df["pct_curto_prazo"] < 20)
    ).astype(int)

    # =====================================================
    # 6. Resultado final
    # =====================================================
    resultado = df[[
        "id_fundo",
        "pct_curto_prazo",
        "pct_longo_prazo",
        "PRAZO_PAGTO_RESGATE",
        "flag_risco_liquidez"
    ]]

    print("Gravando tabela score_2_liquidez_v2...")

    resultado.to_sql(
        "score_2_liquidez_v2",
        engine,
        if_exists="replace",
        index=False
    )

    print("Score 2 – Liquidez Estrutural v2 processado com sucesso!")

# =====================================================
# 7. Execução controlada
# =====================================================
if __name__ == "__main__":
    try:
        calcular_score_2_liquidez(engine)
    except Exception as e:
        print("Erro na execução do Score 2 v2:", str(e))
