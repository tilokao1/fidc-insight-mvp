import os
import requests
import zipfile
import io
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from datetime import datetime
from dateutil.relativedelta import relativedelta

# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")

# LISTA REDUZIDA: Apenas o essencial para economizar espaço no Supabase
TABELAS_CVM = [
    "I", "II", "IV", "V", "VII", "X_1", "X_2", "X_3", "X_5", "X_6", "X_7"
]

def descobrir_mes_mais_recente():
    """Testa os links da CVM de trás pra frente até achar o mês mais recente disponível."""
    data_teste = datetime.today().replace(day=1)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for _ in range(12):
        ano = data_teste.year
        mes = f"{data_teste.month:02d}"
        url = f"http://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{ano}{mes}.zip"
        
        print(f"Testando disponibilidade em: {ano}/{mes}...")
        resposta = requests.get(url, headers=headers, stream=True) 
        
        if resposta.status_code == 200:
            print(f"✅ Mês mais recente encontrado: {ano}/{mes}")
            resposta.close()
            return data_teste
        data_teste -= relativedelta(months=1)
        
    raise Exception("Não foi possível encontrar dados recentes na CVM.")

def atualizar_banco():
    engine = create_engine(os.getenv("DATABASE_URL"), poolclass=NullPool,)
    data_recente = descobrir_mes_mais_recente()
    data_corte = data_recente - relativedelta(months=11)
    
    meses_alvo = []
    data_atual = data_recente
    for _ in range(12):
        meses_alvo.append((data_atual.year, f"{data_atual.month:02d}"))
        data_atual -= relativedelta(months=1)
        
    data_corte_sql = data_corte.strftime('%Y-%m-01')

    for ano, mes in meses_alvo:
        url_zip = f"http://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{ano}{mes}.zip"
        print(f"\nBaixando arquivo: {ano}{mes}...")
        
        try:
            r = requests.get(url_zip)
            r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            
            with engine.begin() as conn:
                for tab in TABELAS_CVM:
                    nome_arquivo_csv = f"inf_mensal_fidc_tab_{tab}_{ano}{mes}.csv"
                    nome_tabela_db = f"inf_mensal_fidc_tab_{tab}"
                    
                    if nome_arquivo_csv in z.namelist():
                        with z.open(nome_arquivo_csv) as f:
                            df = pd.read_csv(f, sep=';', encoding='latin1', low_memory=False)
                            if not df.empty:
                                conn.execute(text(f"DELETE FROM \"{nome_tabela_db}\" WHERE \"DT_COMPTC\" LIKE '{ano}-{mes}-%'"))
                                df.to_sql(nome_tabela_db, conn, if_exists='append', index=False)
                                print(f"  -> Tabela {tab} atualizada.")
                                
        except Exception as e:
            print(f"Erro ao processar {ano}{mes}: {e}")

    # Limpeza de lixo (Otimização)
    print(f"\nLimpando dados mais antigos que {data_corte_sql}...")
    with engine.begin() as conn:
        for tab in TABELAS_CVM:
            nome_tabela_db = f"inf_mensal_fidc_tab_{tab}"
            conn.execute(text(f"DELETE FROM \"{nome_tabela_db}\" WHERE \"DT_COMPTC\" < '{data_corte_sql}'"))

    print("\nOtimizando tabela X_3 com índices...")
    with engine.begin() as conn:
        # Cria o índice na X_3 se ele ainda não existir
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_tab_x3_cnpj ON "inf_mensal_fidc_tab_X_3" ("CNPJ_FUNDO_CLASSE");'))

    print("\n✅ Sincronização concluída. Banco otimizado.")

if __name__ == "__main__":
    atualizar_banco()