import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

print("Iniciando o Motor de Risco Cloud-Native...")

# Carrega a senha escondida do arquivo .env (quando rodar na máquina)
load_dotenv()

# Puxa a URL com segurança
url_postgres = os.getenv('DATABASE_URL')

# Cria o "motor" do banco
engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,)

def calcular_e_salvar_score_setorial(conexao_engine):
    print("1. Conectando ao Supabase para ler os dados brutos...")
    
    # Lendo do Supabase (Trazemos tudo e filtramos o mês mais recente via Pandas para evitar erros de sintaxe no Postgres)
    query = 'SELECT * FROM "inf_mensal_fidc_tab_II"'
    df_tab2 = pd.read_sql_query(query, conexao_engine)
    
    if df_tab2.empty:
        print("Erro: Nenhuma informação encontrada na tabela.")
        return

    # Filtrar apenas o mês mais recente disponível
    data_recente = df_tab2['DT_COMPTC'].max()
    df_tab2 = df_tab2[df_tab2['DT_COMPTC'] == data_recente]
    print(f"   -> Dados carregados! Processando competência: {data_recente}")
    
    # ---------------------------------------------------------
    # 2. IDENTIFICAR AS COLUNAS (Lógica mantida intacta)
    # ---------------------------------------------------------
    colunas_id = ['CNPJ_FUNDO_CLASSE', 'DT_COMPTC']
    colunas_remover = ['TAB_II_VL_CARTEIRA', 'TAB_II_C_VL_COMERC', 'TAB_II_D_VL_SERV', 'TAB_II_F_VL_FINANC', 'TAB_II_H_VL_FACTOR', 'TAB_II_I_VL_SETOR_PUBLICO']
    colunas_setores = [col for col in df_tab2.columns if col.startswith('TAB_II_') and col not in colunas_remover]

    # 3. UNPIVOT E CÁLCULOS
    print("2. Calculando o Score de Diversificação (HHI)...")
    df_unpivot = pd.melt(df_tab2, id_vars=colunas_id, value_vars=colunas_setores, var_name='Setor', value_name='Valor')
    df_unpivot = df_unpivot.fillna(0)
    df_unpivot = df_unpivot[df_unpivot['Valor'] > 0]
    
    df_unpivot['Total_Fundo'] = df_unpivot.groupby('CNPJ_FUNDO_CLASSE')['Valor'].transform('sum')
    df_unpivot['Share_Setor'] = (df_unpivot['Valor'] / df_unpivot['Total_Fundo']) * 100
    df_unpivot['Share_Quadrado'] = df_unpivot['Share_Setor'] ** 2
    
    df_score = df_unpivot.groupby(['CNPJ_FUNDO_CLASSE', 'DT_COMPTC'])['Share_Quadrado'].sum().reset_index()
    df_score.rename(columns={'Share_Quadrado': 'HHI_Setorial'}, inplace=True)
    
    df_score['Score_Diversificacao_Setorial'] = 10 - ((df_score['HHI_Setorial'] / 10000) * 10)
    df_score['Score_Diversificacao_Setorial'] = df_score['Score_Diversificacao_Setorial'].clip(lower=0, upper=10)
    
    # 4. SALVAR DE VOLTA NO SUPABASE
    print("3. Salvando a tabela de métricas no Supabase...")
    nome_tabela_destino = 'score_3_metrica_2'
    
    # O if_exists='replace' garante que ele sempre atualiza a tabela quando rodar
    df_score.to_sql(nome_tabela_destino, conexao_engine, if_exists='replace', index=False)
    
    # Criação de indice para melhor desempenho nas consultas
    print(f"4. Criando índices na tabela {nome_tabela_destino}...")
    with conexao_engine.begin() as conn:
        conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_score3_cnpj ON "{nome_tabela_destino}" ("CNPJ_FUNDO_CLASSE");'))

    print(f"Sucesso Total! Tabela '{nome_tabela_destino}' criada/atualizada no banco na nuvem.")

# Executar a função
try:
    calcular_e_salvar_score_setorial(engine)
except Exception as e:
    print(f"Erro durante a execução: {e}")