import pandas as pd
import sqlite3

# caminhos
csv_path = r"C:\Users\Wagner Martins\Downloads\inf_mensal_fidc_tab_I_202602.csv"
db_path = r"C:\Users\Wagner Martins\OneDrive\Área de Trabalho\Fiap - DS\DB.Challenge\fidc.db"

# ler csv
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

# limpeza
df = df.dropna(subset=["DENOM_SOCIAL", "TAB_I_VL_ATIVO"])
df = df.fillna(0)
df["DT_COMPTC"] = pd.to_datetime(df["DT_COMPTC"], errors="coerce")

# conectar banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# criar tabela real
cursor.execute("""
CREATE TABLE IF NOT EXISTS fidc_dados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    denom_social TEXT,
    cnpj TEXT,
    data TEXT,
    vl_ativo REAL,
    vl_carteira REAL,
    vl_risco REAL,
    vl_inadimplencia REAL
)
""")

conn.commit()

# inserir dados
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO fidc_dados (
            denom_social,
            cnpj,
            data,
            vl_ativo,
            vl_carteira,
            vl_risco,
            vl_inadimplencia
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["DENOM_SOCIAL"],
        row["CNPJ_FUNDO_CLASSE"],
        str(row["DT_COMPTC"]),
        float(row["TAB_I_VL_ATIVO"]),
        float(row["TAB_I2_VL_CARTEIRA"]),
        float(row["TAB_I2A_VL_DIRCRED_RISCO"]),
        float(row["TAB_I2A2_VL_CRED_VENC_INAD"])
    ))

conn.commit()
conn.close()

print("🔥 Dados reais da CVM inseridos com sucesso!")