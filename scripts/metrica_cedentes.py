import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

print("🚀 Iniciando Score de Cedentes (versão BI)...")

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,
)

# =========================
# 1. LEITURA
# =========================
df = pd.read_sql_query('SELECT * FROM "inf_mensal_fidc_tab_I"', engine)

data_recente = df["DT_COMPTC"].max()
df = df[df["DT_COMPTC"] == data_recente]

cols_cedentes = [c for c in df.columns if "PR_CEDENTE" in c and "TAB_I2B1" in c]

# =========================
# 2. UNPIVOT
# =========================
df_long = df.melt(
    id_vars=["CNPJ_FUNDO_CLASSE", "DT_COMPTC"],
    value_vars=cols_cedentes,
    var_name="cedente",
    value_name="participacao"
)

df_long = df_long.dropna()
df_long["participacao"] = pd.to_numeric(df_long["participacao"], errors="coerce")
df_long = df_long.dropna(subset=["participacao"])
df_long = df_long[df_long["participacao"] > 0]

# 🔥 CONVERSÃO PRA PROPORÇÃO (0–1)
df_long["share"] = df_long["participacao"] / 100

# =========================
# 3. HHI
# =========================
df_long["quadrado"] = df_long["share"] ** 2

df_score = df_long.groupby(
    ["CNPJ_FUNDO_CLASSE", "DT_COMPTC"]
)["quadrado"].sum().reset_index()

df_score.rename(columns={"quadrado": "HHI_Cedentes"}, inplace=True)

# =========================
# 4. SCORE (0–10)
# =========================
df_score["score_cedentes"] = (1 - df_score["HHI_Cedentes"]) * 10
df_score["score_cedentes"] = df_score["score_cedentes"].clip(0, 10)
df_score["score_100"] = df_score["score_cedentes"] * 10

# =========================
# 5. MÉTRICAS EXPLICATIVAS
# =========================

# qtd cedentes
qtd = df_long.groupby("CNPJ_FUNDO_CLASSE")["cedente"].count().reset_index()
qtd.rename(columns={"cedente": "qtd_cedentes"}, inplace=True)

# maior cedente
max_ced = df_long.groupby("CNPJ_FUNDO_CLASSE")["share"].max().reset_index()
max_ced.rename(columns={"share": "maior_cedente"}, inplace=True)

# top 3 concentração
top3 = (
    df_long.sort_values(["CNPJ_FUNDO_CLASSE", "share"], ascending=False)
    .groupby("CNPJ_FUNDO_CLASSE")
    .head(3)
)

top3_sum = top3.groupby("CNPJ_FUNDO_CLASSE")["share"].sum().reset_index()
top3_sum.rename(columns={"share": "top3_share"}, inplace=True)

# merge tudo
df_score = df_score.merge(qtd, on="CNPJ_FUNDO_CLASSE")
df_score = df_score.merge(max_ced, on="CNPJ_FUNDO_CLASSE")
df_score = df_score.merge(top3_sum, on="CNPJ_FUNDO_CLASSE")

# =========================
# 6. CLASSIFICAÇÃO
# =========================
def classificar(score):
    if score >= 8:
        return "Alta Diversificação"
    elif score >= 5:
        return "Média Diversificação"
    else:
        return "Baixa Diversificação"

df_score["classificacao"] = df_score["score_cedentes"].apply(classificar)

# =========================
# 7. SALVAR TABELA PRINCIPAL
# =========================
df_score.to_sql(
    "score_3_metrica_1",
    engine,
    if_exists="replace",
    index=False
)

# =========================
# 8. TABELA GRANULAR (PRO BI)
# =========================
df_long.to_sql(
    "score_3_metrica_1_detalhe",
    engine,
    if_exists="replace",
    index=False
)

print("✅ Dados prontos para BI!")