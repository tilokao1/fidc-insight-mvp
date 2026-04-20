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
    # Retornar após criar tabelas da métrica 1
    query = """
        SELECT
            "CNPJ_FUNDO_CLASSE",
            "TAB_X_VL_RENTAB_MES",
            -- s1.score_1_credito,
            s2."flag_risco_liquidez",
            s3."Score_Diversificacao_Setorial"
        FROM "inf_mensal_fidc_tab_X_3" v
        -- LEFT JOIN "score_1_credito" s1 ON v."CNPJ_FUNDO_CLASSE" = s1."CNPJ_FUNDO_CLASSE"
        LEFT JOIN "score_2_metricas_1_e_2" s2 ON v."CNPJ_FUNDO_CLASSE" = s2."CNPJ_FUNDO_CLASSE"
        LEFT JOIN "score_3_metrica_2" s3 ON v."CNPJ_FUNDO_CLASSE" = s3."CNPJ_FUNDO_CLASSE"
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
