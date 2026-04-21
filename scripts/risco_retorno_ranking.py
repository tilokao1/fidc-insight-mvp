import pandas as pd
from sqlalchemy import create_engine, text
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

# Adicionado timeout de 2 minutos para evitar que o script fique "pendurado"
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"options": "-c statement_timeout=120000"}
)

# =====================================================
# 2. Função principal
# =====================================================
def calcular_kpis_performance(engine):
    
    print("Lendo dados de rentabilidade e scores (Filtrando mês mais recente)...")
    
    # AJUSTE 1: Filtrar apenas a última competência e usar Alias 'v' explicitamente
    # Isso evita cruzar dados de meses diferentes desnecessariamente
    query = """
            SELECT
                v."CNPJ_FUNDO_CLASSE",
                v."TAB_X_VL_RENTAB_MES",
                -- Scores de Risco (Eixo X)
                s2."flag_risco_liquidez",
                s3."Score_Diversificacao_Setorial",
                -- s1."score_credito", -- Se você já tiver a tabela s1 pronta
                
                -- Dados para o "Insight Incrível" (Filtro de Estratégia)
                x1."TAB_X_VL_ESTRATEGIA_DISTRESSED" as pct_distressed
                
            FROM "inf_mensal_fidc_tab_X_3" v
            LEFT JOIN "score_2_metricas_1_e_2" s2 ON v."CNPJ_FUNDO_CLASSE" = s2."CNPJ_FUNDO_CLASSE"
            LEFT JOIN "score_3_metrica_2" s3 ON v."CNPJ_FUNDO_CLASSE" = s3."CNPJ_FUNDO_CLASSE"
            LEFT JOIN "inf_mensal_fidc_tab_X_1" x1 ON v."CNPJ_FUNDO_CLASSE" = x1."CNPJ_FUNDO_CLASSE" 
                AND v."DT_COMPTC" = x1."DT_COMPTC"
                
            WHERE v."DT_COMPTC" = (SELECT MAX("DT_COMPTC") FROM "inf_mensal_fidc_tab_X_3")
        """

    df = pd.read_sql(query, engine)
    
    if df.empty:
        print("Aviso: Nenhum dado encontrado para processar.")
        return

    print(f"Processando {len(df)} fundos...")

    # =====================================================
    # 3. KPIs de Performance (Lógica mantida)
    # =====================================================
    df["indice_risco_retorno_liquidez"] = (
        df["TAB_X_VL_RENTAB_MES"] / (df["flag_risco_liquidez"].fillna(0) + 1)
    )

    df["ranking_eficiencia"] = df["indice_risco_retorno_liquidez"].rank(ascending=False, method="dense")
    df["ranking_retorno"] = df["TAB_X_VL_RENTAB_MES"].rank(ascending=False, method="dense")

    # =====================================================
    # 4. Resultado final
    # =====================================================
    resultado = df[[
        "CNPJ_FUNDO_CLASSE",
        "TAB_X_VL_RENTAB_MES",
        "indice_risco_retorno_liquidez",
        "ranking_eficiencia",
        "ranking_retorno"
    ]]

    print("Gravando tabela de KPIs (Modo Turbo ativo)...")

    # AJUSTE 2: method="multi" e chunksize
    # Isso agrupa os INSERTS e faz a gravação ser 50x mais rápida
    resultado.to_sql(
        "kpis_performance_risco_retorno",
        engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi" 
    )

    print("✅ KPIs de Performance processados com sucesso!")

# =====================================================
# 5. Execução controlada
# =====================================================
if __name__ == "__main__":
    try:
        calcular_kpis_performance(engine)
    except Exception as e:
        print("Erro no Motor de Performance:", str(e))
    finally:
        engine.dispose() # Garante o fechamento da conexão