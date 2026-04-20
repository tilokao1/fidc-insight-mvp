import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

print("🚀 Iniciando Score de Cedentes...")

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,)

df = pd.read_sql_query('SELECT * FROM "inf_mensal_fidc_tab_I"', engine)

data_recente = df["DT_COMPTC"].max()
df = df[df["DT_COMPTC"] == data_recente]

cols_cedentes = [c for c in df.columns if "PR_CEDENTE" in c and "TAB_I2B1" in c]

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

df_long["quadrado"] = df_long["participacao"] ** 2

df_score = df_long.groupby(
    ["CNPJ_FUNDO_CLASSE", "DT_COMPTC"]
)["quadrado"].sum().reset_index()

df_score.rename(columns={"quadrado": "HHI_Cedentes"}, inplace=True)

df_score["score_cedentes"] = 10 - (df_score["HHI_Cedentes"] / 10000 * 10)
df_score["score_cedentes"] = df_score["score_cedentes"].clip(0, 10)
df_score["score_100"] = df_score["score_cedentes"] * 10

df_score.to_sql(
    "score_3_metrica_1",
    engine,
    if_exists="replace",
    index=False
)

print("✅ Score de cedentes salvo no Supabase!")