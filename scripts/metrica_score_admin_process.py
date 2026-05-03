import os
import time
import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# A URL exata para onde o formulário envia o POST (identificada na image_efa6bb.png)
URL_CVM_ACTION = "https://sistemas.cvm.gov.br/asp/cvmwww/inqueritos/ResultBuscaPas_Novo.asp"

def buscar_qtd_processos_cvm(cnpj):
    """
    Faz um POST no portal da CVM e extrai a quantidade de processos
    da tabela HTML retornada, usando o Pandas.
    """
    payload = {
        "txtDocIndiciado": cnpj
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(URL_CVM_ACTION, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Tenta ler as tabelas HTML da página de resposta
        tabelas = pd.read_html(response.text)
        
        if tabelas:
            # Em páginas legadas ASP, a tabela de resultados costuma ser a última
            df_resultados = tabelas[-1]
            
            # Se a tabela tiver dados, retornamos a quantidade de linhas
            # Subtraímos 1 se a página retornar uma linha de cabeçalho mesclada, 
            # mas o read_html geralmente resolve isso usando a primeira linha como header.
            return len(df_resultados)
            
    except ValueError:
        # pd.read_html levanta ValueError se não achar nenhuma tag <table> (ex: CNPJ sem processos)
        return 0
    except Exception as e:
        print(f"      [!] Erro ao consultar CVM para o CNPJ {cnpj}: {e}")
        return 0
        
    return 0


def calcular_metrica_score_admin_process():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL, poolclass=NullPool)

    with engine.begin() as conn:
        print("Iniciando extração de dados do Supabase...")

        # 1. Query para pegar a data mais recente e fazer o JOIN das Tabelas I e IV
        query = """
        WITH UltimaData AS (
            SELECT MAX("DT_COMPTC") AS max_dt
            FROM "inf_mensal_fidc_tab_I"
        )
        SELECT 
            t1."CNPJ_FUNDO_CLASSE", 
            t1."DENOM_SOCIAL", 
            t1."DT_COMPTC", 
            t1."CNPJ_ADMIN", 
            t1."ADMIN",
            t4."TAB_IV_A_VL_PL"
        FROM "inf_mensal_fidc_tab_I" t1
        JOIN "inf_mensal_fidc_tab_IV" t4
            ON t1."CNPJ_FUNDO_CLASSE" = t4."CNPJ_FUNDO_CLASSE"
           AND t1."DT_COMPTC" = t4."DT_COMPTC"
        JOIN UltimaData ud
            ON t1."DT_COMPTC" = ud.max_dt
        """
        
        df_fundos = pd.read_sql(query, conn)
        print(f"Encontrados {len(df_fundos)} fundos na data de competência mais recente.")

        # 2. Isolar os CNPJs únicos de Administradores para não repetir consultas na CVM
        cnpjs_admins_unicos = df_fundos['CNPJ_ADMIN'].dropna().unique()
        print(f"Total de Administradores únicos para consultar na CVM: {len(cnpjs_admins_unicos)}")
        
        dict_processos = {}
        
        # 3. Web Scraping na CVM (com "politeness" para evitar bloqueios)
        print("\nIniciando consultas no portal da CVM (isso pode levar alguns minutos)...")
        for i, cnpj in enumerate(cnpjs_admins_unicos, start=1):
            print(f"   [{i}/{len(cnpjs_admins_unicos)}] Consultando CNPJ: {cnpj}")
            qtd = buscar_qtd_processos_cvm(cnpj)
            dict_processos[cnpj] = qtd
            
            # Pausa de 1.5 segundos entre as requisições para não estressar o servidor da CVM
            time.sleep(1.5) 

        # 4. Mapear os resultados de volta para o DataFrame principal
        df_fundos['QTD_PROC_CVM'] = df_fundos['CNPJ_ADMIN'].map(dict_processos)
        
        # Preencher possíveis Nulos com 0 e converter para inteiro
        df_fundos['QTD_PROC_CVM'] = df_fundos['QTD_PROC_CVM'].fillna(0).astype(int)

        # 5. Salvar a nova tabela no banco de dados
        print("\nSalvando resultados na tabela 'score_admin_process'...")
        df_fundos.to_sql("score_admin_process", conn, if_exists="replace", index=False)
        
        print(f"✅ Sucesso! Tabela criada/atualizada com {len(df_fundos)} registros.")


if __name__ == "__main__":
    calcular_metrica_score_admin_process()