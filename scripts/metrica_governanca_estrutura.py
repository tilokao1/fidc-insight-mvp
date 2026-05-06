import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL")

def calcular_score_4():
    engine = create_engine(
        os.getenv("DATABASE_URL"), poolclass=NullPool,
    )

    with engine.begin() as conn:
        print("Iniciando cálculos do Score 4...")

        # --- MÉTRICA Proteção ao Investidor (Subordinação) ---
        print("Calculando Métrica 4.1...")
        query_41 = """
        SELECT 
            t4."CNPJ_FUNDO_CLASSE",
            t4."DENOM_SOCIAL",
            t4."DT_COMPTC",
            t4."TAB_IV_A_VL_PL"                                             AS vl_patrimonio_liquido,
            SUM(tx2."TAB_X_QT_COTA" * tx2."TAB_X_VL_COTA")                 AS vl_subordinacao_total,
            (SUM(tx2."TAB_X_QT_COTA" * tx2."TAB_X_VL_COTA")
                / NULLIF(t4."TAB_IV_A_VL_PL", 0)) * 100                    AS percentual_subordinacao
        FROM "inf_mensal_fidc_tab_IV" t4
        JOIN "inf_mensal_fidc_tab_X_2" tx2 
            ON t4."CNPJ_FUNDO_CLASSE" = tx2."CNPJ_FUNDO_CLASSE"
           AND t4."DT_COMPTC" = tx2."DT_COMPTC"
        WHERE tx2."TAB_X_CLASSE_SERIE" ILIKE '%%Subordinada%%'
           OR tx2."TAB_X_CLASSE_SERIE" ILIKE '%%Mezanino%%'
        GROUP BY t4."CNPJ_FUNDO_CLASSE", t4."DENOM_SOCIAL", t4."DT_COMPTC", t4."TAB_IV_A_VL_PL"
        """
        df_41 = pd.read_sql(query_41, conn)
        df_41.to_sql("score_protecao_ao_investidor", conn, if_exists="replace", index=False)
        print(f"   Métrica 4.1: {len(df_41)} registros salvos.")

        # --- MÉTRICA Confiança do Mercado (Variação de Cotistas) ---
        print("Calculando Métrica 4.2...")

        # Passo 1 — agregar (SUM) cotistas por CNPJ+mês dentro de uma CTE, garantindo 1 linha por CNPJ+mês antes de qualquer LAG.
        # Passo 2 — buscar DENOM_SOCIAL via subconsulta (primeiro valor por CNPJ).
        # Passo 3 — aplicar LAG() só depois, sobre os totais já consolidados.

        query_42 = """
        WITH cotistas_agregados AS (
            SELECT
                "CNPJ_FUNDO_CLASSE",
                "DT_COMPTC",
                SUM("TAB_X_NR_COTST") AS cotistas_total
            FROM "inf_mensal_fidc_tab_X_1"
            GROUP BY "CNPJ_FUNDO_CLASSE", "DT_COMPTC"
        ),
        nome_fundo AS (
            SELECT DISTINCT ON ("CNPJ_FUNDO_CLASSE")
                "CNPJ_FUNDO_CLASSE",
                "DENOM_SOCIAL"
            FROM "inf_mensal_fidc_tab_X_1"
            ORDER BY "CNPJ_FUNDO_CLASSE"
        )
        SELECT
            ca."CNPJ_FUNDO_CLASSE",
            nf."DENOM_SOCIAL",
            ca."DT_COMPTC",
            ca.cotistas_total                                         AS cotistas_atual,
            LAG(ca.cotistas_total) OVER (
                PARTITION BY ca."CNPJ_FUNDO_CLASSE"
                ORDER BY ca."DT_COMPTC"
            )                                                         AS cotistas_anterior,
            ca.cotistas_total - LAG(ca.cotistas_total) OVER (
                PARTITION BY ca."CNPJ_FUNDO_CLASSE"
                ORDER BY ca."DT_COMPTC"
            )                                                         AS variacao_cotistas
        FROM cotistas_agregados ca
        JOIN nome_fundo nf
            ON ca."CNPJ_FUNDO_CLASSE" = nf."CNPJ_FUNDO_CLASSE"
        ORDER BY ca."CNPJ_FUNDO_CLASSE", ca."DT_COMPTC"
        """
        df_42 = pd.read_sql(query_42, conn)
        df_42.to_sql("score_retencao_de_cotistas", conn, if_exists="replace", index=False)
        print(f"   Métrica 4.3: {len(df_42)} registros salvos.")

    print("✅ Score 4 calculado e salvo com sucesso no Supabase!")

if __name__ == "__main__":
    calcular_score_4()