import os
import requests
import zipfile
import io
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from dateutil.relativedelta import relativedelta # Precisamos dessa lib para subtrair meses facilmente

# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")

# Lista exata das tabelas da CVM que você usa
TABELAS_CVM = [
    "I", "II", "III", "IV", "V", "VI", "VII", 
    "X_1", "X_2", "X_3", "X_5", "X_6", "X_7"
]

def descobrir_mes_mais_recente():
    """Testa os links da CVM de trás pra frente até achar o mês mais recente disponível."""
    data_teste = datetime.today().replace(day=1)
    
    for _ in range(6): # Tenta até 6 meses para trás
        ano = data_teste.year
        mes = f"{data_teste.month:02d}"
        url = f"http://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{ano}{mes}.zip"
        
        print(f"Testando disponibilidade em: {ano}/{mes}...")
        resposta = requests.head(url) # Head pega só o status, sem baixar o arquivo (super rápido)
        
        if resposta.status_code == 200:
            print(f"✅ Mês mais recente encontrado: {ano}/{mes}")
            return data_teste
            
        # Volta 1 mês
        data_teste -= relativedelta(months=1)
        
    raise Exception("Não foi possível encontrar dados recentes na CVM.")

def atualizar_banco():
    engine = create_engine(DATABASE_URL)
    
    # 1. Definir a janela de 12 meses
    data_recente = descobrir_mes_mais_recente()
    data_corte = data_recente - relativedelta(months=11)
    
    meses_alvo = []
    data_atual = data_recente
    for _ in range(12):
        meses_alvo.append((data_atual.year, f"{data_atual.month:02d}"))
        data_atual -= relativedelta(months=1)
        
    print(f"Janela de dados: {meses_alvo[-1][1]}/{meses_alvo[-1][0]} até {meses_alvo[0][1]}/{meses_alvo[0][0]}")
    
    # String da data de corte para o SQL (ex: '2025-05-01')
    data_corte_sql = data_corte.strftime('%Y-%m-01')

    # 2. Loop para baixar e atualizar cada mês
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
                            # Lê o CSV da CVM
                            df = pd.read_csv(f, sep=';', encoding='latin1', low_memory=False)
                            
                            if not df.empty:
                                # Prevenção de duplicatas: Apaga os dados DESSE mês específico antes de inserir
                                # A data na CVM vem no formato YYYY-MM-DD
                                conn.execute(text(f"DELETE FROM \"{nome_tabela_db}\" WHERE \"DT_COMPTC\" LIKE '{ano}-{mes}-%'"))
                                
                                # Insere os dados novos (append não estraga a estrutura da tabela)
                                df.to_sql(nome_tabela_db, conn, if_exists='append', index=False)
                                print(f"  -> Tabela {tab} atualizada ({len(df)} linhas).")
                                
        except Exception as e:
            print(f"Erro ao processar {ano}{mes}: {e}")

    # 3. Limpeza do Lixo (Otimização de Espaço)
    print(f"\nIniciando limpeza de dados mais antigos que {data_corte_sql}...")
    with engine.begin() as conn:
        for tab in TABELAS_CVM:
            nome_tabela_db = f"inf_mensal_fidc_tab_{tab}"
            # Deleta qualquer linha onde a data seja menor que a nossa data de corte
            query_limpeza = text(f"DELETE FROM \"{nome_tabela_db}\" WHERE \"DT_COMPTC\" < '{data_corte_sql}'")
            conn.execute(query_limpeza)
            
    print("\n✅ Sincronização com a CVM concluída com sucesso! Banco otimizado para 12 meses.")

if __name__ == "__main__":
    atualizar_banco()