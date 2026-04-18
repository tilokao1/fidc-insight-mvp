import os
import pandas as pd
from sqlalchemy import create_engine, text

# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")

def calcular_score_4():
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        print("Iniciando cálculos do Score 4...")

        # --- MÉTRICA 4.1: Proteção ao Investidor (Subordinação) ---
        print("Calculando Métrica 4.1...")
        query_41 = """
        SELECT 
            t4."CNPJ_FUNDO_CLASSE",
            t4."DT_COMPTC",
            (SUM(tx2."TAB_X_QT_COTA" * tx2."TAB_X_VL_COTA") / NULLIF(t4."TAB_IV_A_VL_PL", 0)) * 100 AS percentual_subordinacao
        FROM "inf_mensal_fidc_tab_IV" t4
        JOIN "inf_mensal_fidc_tab_X_2" tx2 
            ON t4."CNPJ_FUNDO_CLASSE" = tx2."CNPJ_FUNDO_CLASSE" AND t4."DT_COMPTC" = tx2."DT_COMPTC"
        WHERE tx2."TAB_X_CLASSE_SERIE" ILIKE '%%Subordinada%%' OR tx2."TAB_X_CLASSE_SERIE" ILIKE '%%Mezanino%%'
        GROUP BY t4."CNPJ_FUNDO_CLASSE", t4."DT_COMPTC", t4."TAB_IV_A_VL_PL"
        """
        df_41 = pd.read_sql(query_41, conn)
        df_41.to_sql("score_4_metrica_1", conn, if_exists="replace", index=False)

        # --- MÉTRICA 4.2: Alinhamento do Gestor (Concentração de Cedente) ---
        print("Calculando Métrica 4.2...")
        query_42 = """
        SELECT 
            t7."CNPJ_FUNDO_CLASSE",
            t7."DT_COMPTC",
            (t7."TAB_VII_B1_2_VL_CEDENTE" / NULLIF(t4."TAB_IV_A_VL_PL", 0)) * 100 AS perc_concentracao_cedente,
            CASE 
                WHEN (t7."TAB_VII_B1_2_VL_CEDENTE" / NULLIF(t4."TAB_IV_A_VL_PL", 0)) * 100 > 20 THEN 'ALERTA - Alta Concentração'
                ELSE 'OK'
            END AS status_alinhamento
        FROM "inf_mensal_fidc_tab_VII" t7
        JOIN "inf_mensal_fidc_tab_IV" t4 
            ON t7."CNPJ_FUNDO_CLASSE" = t4."CNPJ_FUNDO_CLASSE" AND t7."DT_COMPTC" = t4."DT_COMPTC"
        """
        df_42 = pd.read_sql(query_42, conn)
        df_42.to_sql("score_4_metrica_2", conn, if_exists="replace", index=False)

        # --- MÉTRICA 4.3: Confiança do Mercado (Variação de Cotistas) ---
        print("Calculando Métrica 4.3...")
        # Usamos a função LAG para comparar o mês atual com o anterior do mesmo fundo
        query_43 = """
        SELECT 
            "CNPJ_FUNDO_CLASSE",
            "DT_COMPTC",
            "TAB_X_NR_COTST" as cotistas_atual,
            LAG("TAB_X_NR_COTST") OVER (PARTITION BY "CNPJ_FUNDO_CLASSE" ORDER BY "DT_COMPTC") as cotistas_anterior,
            "TAB_X_NR_COTST" - LAG("TAB_X_NR_COTST") OVER (PARTITION BY "CNPJ_FUNDO_CLASSE" ORDER BY "DT_COMPTC") as variacao_cotistas
        FROM "inf_mensal_fidc_tab_X_1"
        """
        df_43 = pd.read_sql(query_43, conn)
        df_43.to_sql("score_4_metrica_3", conn, if_exists="replace", index=False)

    print("✅ Score 4 calculado e salvo com sucesso no Supabase!")

if __name__ == "__main__":
    calcular_score_4()