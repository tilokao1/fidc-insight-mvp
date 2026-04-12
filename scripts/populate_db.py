import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

print("🚀 Inserindo dados no Supabase...")

# -----------------------
# 1. CONEXÃO SUPABASE
# -----------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# -----------------------
# 2. LER CSV
# -----------------------
csv_path = r"C:\Users\Wagner Martins\Downloads\inf_mensal_fidc_tab_I_202602.csv"

df = pd.read_csv(csv_path, sep=";", encoding="latin1")

colunas = [
    "DENOM_SOCIAL",
    "CNPJ_FUNDO_CLASSE",
    "DT_COMPTC",
    "TAB_I_VL_ATIVO",
    "TAB_I2_VL_CARTEIRA",
    "TAB_I2A_VL_DIRCRED_RISCO",
    "TAB_I2A2_VL_CRED_VENC_INAD"
]

df = df[colunas]

# -----------------------
# 3. LIMPEZA
# -----------------------
df = df.dropna(subset=["DENOM_SOCIAL", "TAB_I_VL_ATIVO"])
df = df.fillna(0)
df["DT_COMPTC"] = pd.to_datetime(df["DT_COMPTC"], errors="coerce")

# -----------------------
# 4. RENOMEAR COLUNAS (IMPORTANTE PRO SEU SCORE)
# -----------------------
df = df.rename(columns={
    "DENOM_SOCIAL": "denom_social",
    "CNPJ_FUNDO_CLASSE": "cnpj",
    "DT_COMPTC": "data",
    "TAB_I2_VL_CARTEIRA": "vl_carteira",
    "TAB_I2A_VL_DIRCRED_RISCO": "vl_risco",
    "TAB_I2A2_VL_CRED_VENC_INAD": "vl_inadimplencia"
})

# -----------------------
# 5. SUBIR PARA SUPABASE
# -----------------------
df.to_sql(
    "fidc_dados",
    engine,
    if_exists="replace",
    index=False
)

print("🔥 Dados inseridos no Supabase com sucesso!")