import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

print("🚀 Iniciando Score de Diversificação...")

# -----------------------------
# 1. CARREGA .env
# -----------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL não encontrada no .env")

# -----------------------------
# 2. CONEXÃO COM SUPABASE / POSTGRES
# -----------------------------
engine = create_engine(DATABASE_URL)

# -----------------------------
# 3. LEITURA DOS DADOS
# -----------------------------
df = pd.read_sql_query("SELECT * FROM fidc_dados", engine)

if df.empty:
    raise Exception("Tabela fidc_dados está vazia no banco")

print("📥 Dados carregados com sucesso!")

# -----------------------------
# 4. LIMPEZA
# -----------------------------
df = df.dropna(subset=[
    'vl_carteira',
    'vl_risco',
    'vl_inadimplencia'
])

# -----------------------------
# 5. TOTAL DA EXPOSIÇÃO
# -----------------------------
df['total'] = (
    df['vl_carteira'] +
    df['vl_risco'] +
    df['vl_inadimplencia']
)

df = df[df['total'] > 0]

# -----------------------------
# 6. PARTICIPAÇÕES
# -----------------------------
df['p_carteira'] = df['vl_carteira'] / df['total']
df['p_risco'] = df['vl_risco'] / df['total']
df['p_inad'] = df['vl_inadimplencia'] / df['total']

# -----------------------------
# 7. HHI (CONCENTRAÇÃO)
# -----------------------------
df['HHI'] = (
    df['p_carteira'] ** 2 +
    df['p_risco'] ** 2 +
    df['p_inad'] ** 2
)

# -----------------------------
# 8. SCORE (0 a 10 e 0 a 100)
# -----------------------------
df['score_diversificacao'] = 10 - (df['HHI'] * 10)
df['score_diversificacao'] = df['score_diversificacao'].clip(0, 10)

df['score_100'] = df['score_diversificacao'] * 10

# -----------------------------
# 9. RESULTADO FINAL
# -----------------------------
resultado = df[[
    'denom_social',
    'cnpj',
    'data',
    'score_diversificacao',
    'score_100'
]]

print("📊 Preview dos resultados:")
print(resultado.head())

# -----------------------------
# 10. SALVAR NO SUPABASE
# -----------------------------
resultado.to_sql(
    'fato_score_diversificacao',
    engine,
    if_exists='replace',
    index=False
)

print("✅ Sucesso! Dados salvos no Supabase.")