import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

print("🚀 Iniciando Score Setorial (versão final)...")

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,
)

def calcular_e_salvar_score_setorial(conexao_engine):

    # =========================
    # 1. LEITURA
    # =========================
    df = pd.read_sql_query('SELECT * FROM "inf_mensal_fidc_tab_II"', conexao_engine)

    if df.empty:
        print("❌ Nenhum dado encontrado.")
        return

    data_recente = df["DT_COMPTC"].max()
    df = df[df["DT_COMPTC"] == data_recente]

    print(f"📅 Processando competência: {data_recente}")

    # =========================
    # 2. IDENTIFICAR COLUNAS
    # =========================
    colunas_id = ["CNPJ_FUNDO_CLASSE", "DT_COMPTC"]

    colunas_remover = [
        "TAB_II_VL_CARTEIRA",
        "TAB_II_C_VL_COMERC",
        "TAB_II_D_VL_SERV",
        "TAB_II_F_VL_FINANC",
        "TAB_II_H_VL_FACTOR",
        "TAB_II_I_VL_SETOR_PUBLICO"
    ]

    colunas_setores = [
        col for col in df.columns
        if col.startswith("TAB_II_") and col not in colunas_remover
    ]

    # =========================
    # 3. UNPIVOT
    # =========================
    df_long = pd.melt(
        df,
        id_vars=colunas_id,
        value_vars=colunas_setores,
        var_name="setor",
        value_name="valor"
    )

    df_long["valor"] = pd.to_numeric(df_long["valor"], errors="coerce")
    df_long = df_long.dropna(subset=["valor"])
    df_long = df_long[df_long["valor"] > 0]

    # =========================
    # 4. NORMALIZAÇÃO
    # =========================
    df_long["total_fundo"] = df_long.groupby("CNPJ_FUNDO_CLASSE")["valor"].transform("sum")

    df_long["share"] = df_long["valor"] / df_long["total_fundo"]

    # =========================
    # 5. HHI
    # =========================
    df_long["quadrado"] = df_long["share"] ** 2

    df_score = df_long.groupby(
        ["CNPJ_FUNDO_CLASSE", "DT_COMPTC"]
    )["quadrado"].sum().reset_index()

    df_score.rename(columns={"quadrado": "HHI_Setorial"}, inplace=True)

    # =========================
    # 6. SCORE
    # =========================
    df_score["score_setorial"] = (1 - df_score["HHI_Setorial"]) * 10
    df_score["score_setorial"] = df_score["score_setorial"].clip(0, 10)

    df_score["score_100"] = df_score["score_setorial"] * 10

    # =========================
    # 7. MÉTRICAS EXPLICATIVAS
    # =========================

    # maior setor
    maior = df_long.groupby("CNPJ_FUNDO_CLASSE")["share"].max().reset_index()
    maior.rename(columns={"share": "maior_setor"}, inplace=True)

    # top 3 setores
    top3 = (
        df_long.sort_values(["CNPJ_FUNDO_CLASSE", "share"], ascending=False)
        .groupby("CNPJ_FUNDO_CLASSE")
        .head(3)
    )

    top3_sum = top3.groupby("CNPJ_FUNDO_CLASSE")["share"].sum().reset_index()
    top3_sum.rename(columns={"share": "top3_setores"}, inplace=True)

    # merge
    df_score = df_score.merge(maior, on="CNPJ_FUNDO_CLASSE")
    df_score = df_score.merge(top3_sum, on="CNPJ_FUNDO_CLASSE")

    # =========================
    # 8. CAMPOS PRO BI
    # =========================
    df_score["concentracao_top1_pct"] = df_score["maior_setor"] * 100

    # =========================
    # 9. CLASSIFICAÇÃO
    # =========================
    def classificar(score):
        if score >= 8:
            return "Alta Diversificação"
        elif score >= 5:
            return "Média Diversificação"
        else:
            return "Baixa Diversificação"

    df_score["classificacao"] = df_score["score_setorial"].apply(classificar)

    # =========================
    # 10. SALVAR
    # =========================
    df_score.to_sql(
        "score_concentracao_setorial",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    # índice
    with conexao_engine.begin() as conn:
        conn.execute(text(
            'CREATE INDEX IF NOT EXISTS idx_setorial_cnpj ON "score_concentracao_setorial" ("CNPJ_FUNDO_CLASSE");'
        ))

    print("✅ Score setorial final salvo no Supabase!")

# =========================
# EXECUÇÃO
# =========================
try:
    calcular_e_salvar_score_setorial(engine)
except Exception as e:
    print(f"❌ Erro: {e}")