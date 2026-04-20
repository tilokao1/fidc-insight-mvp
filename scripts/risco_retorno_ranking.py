import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

print("Iniciando Motor de KPIs de Performance – Risco x Retorno...")

# =====================================================
# 1. Variáveis de ambiente
# =====================================================
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não encontrada no .env")

engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,)


# =====================================================
# 2. Função principal
# =====================================================
def calcular_kpis_performance(engine):
    
    print("Lendo dados de rentabilidade e scores...")

    query = """
        SELECT
            v.id_fundo,
            v.RENTAB_MES,
            s1.score_1_credito,
            s2.flag_risco_liquidez,
            s3.score_3_diversificacao
        FROM tabela_vii v
        LEFT JOIN score_1_credito s1 ON v.id_fundo = s1.id_fundo
        LEFT JOIN score_2_liquidez_v2 s2 ON v.id_fundo = s2.id_fundo
        LEFT JOIN score_3_diversificacao s3 ON v.id_fundo = s3.id_fundo
    """

    df = pd.read_sql(query, engine)

    # =====================================================
    # 3. KPIs de Performance
    # =====================================================

    # Índice de eficiência Risco x Retorno (usando Liquidez como risco exemplo)
    df["indice_risco_retorno_liquidez"] = (
        df["RENTAB_MES"] / (df["flag_risco_liquidez"] + 1)
    )

    # Ranking por eficiência
    df["ranking_eficiencia"] = df[
        "indice_risco_retorno_liquidez"
    ].rank(ascending=False, method="dense")

    # Ranking por retorno
    df["ranking_retorno"] = df[
        "RENTAB_MES"
    ].rank(ascending=False, method="dense")

    # =====================================================
    # 4. Resultado final
    # =====================================================
    resultado = df[[
        "id_fundo",
        "RENTAB_MES",
        "indice_risco_retorno_liquidez",
        "ranking_eficiencia",
        "ranking_retorno"
    ]]

    print("Gravando tabela de KPIs de Performance...")

    resultado.to_sql(
        "kpis_performance_risco_retorno",
        engine,
        if_exists="replace",
        index=False
    )

    print("KPIs de Performance processados com sucesso!")

# =====================================================
# 5. Execução controlada
# =====================================================
if __name__ == "__main__":
    try:
        calcular_kpis_performance(engine)
    except Exception as e:
        print("Erro no Motor de Performance:", str(e))
