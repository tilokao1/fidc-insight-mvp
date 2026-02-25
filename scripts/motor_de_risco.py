import sqlite3
import pandas as pd
import os

# 1. Configurar os caminhos das pastas dinamicamente
# Pega o caminho absoluto da pasta onde este script está salvo (.../scripts)
diretorio_script = os.path.dirname(os.path.abspath(__file__))

# Sobe um nível e aponta para a pasta 'database' (.../database)
diretorio_database = os.path.join(diretorio_script, '..', 'database')

# Garante que a pasta 'database' exista (cria se você tiver deletado sem querer)
os.makedirs(diretorio_database, exist_ok=True)

# Define o caminho completo dos arquivos
caminho_origem = os.path.join(diretorio_database, 'fidc_insight.db')
caminho_destino = os.path.join(diretorio_database, 'fidc_metrics.db')

# 2. Criar as DUAS conexões usando os novos caminhos
# Conexão de LEITURA (Banco atual com 1,1GB de dados da CVM)
conn_origem = sqlite3.connect(caminho_origem)

# Conexão de ESCRITA (Seu novo banco de métricas)
conn_destino = sqlite3.connect(caminho_destino)

def calcular_e_salvar_score_setorial(conexao_leitura, conexao_escrita):
    print("Iniciando o cálculo do Score de Diversificação Setorial...")
    
    # 3. Ler do banco de ORIGEM (pegando o mês mais recente)
    query = """
        SELECT *
        FROM inf_mensal_fidc_tab_II
        WHERE DT_COMPTC = (SELECT MAX(DT_COMPTC) FROM inf_mensal_fidc_tab_II)
    """
    df_tab2 = pd.read_sql_query(query, conexao_leitura)
    
    # ---------------------------------------------------------
    # 4. IDENTIFICAR AS COLUNAS
    # ---------------------------------------------------------
    colunas_id = ['CNPJ_FUNDO_CLASSE', 'DT_COMPTC']
    
    # Colunas que são agrupamentos "Pai" e causariam duplicidade na soma
    colunas_remover = [
        'TAB_II_VL_CARTEIRA', 
        'TAB_II_C_VL_COMERC', 
        'TAB_II_D_VL_SERV', 
        'TAB_II_F_VL_FINANC', 
        'TAB_II_H_VL_FACTOR', 
        'TAB_II_I_VL_SETOR_PUBLICO'
    ]
    
    # Pegar apenas as colunas de setores detalhados (excluindo os pais)
    colunas_setores = [
        col for col in df_tab2.columns 
        if col.startswith('TAB_II_') and col not in colunas_remover
    ]
    # ---------------------------------------------------------

    # 5. UNPIVOT (Transformar colunas em linhas)
    df_unpivot = pd.melt(
        df_tab2, 
        id_vars=colunas_id, 
        value_vars=colunas_setores,
        var_name='Setor', 
        value_name='Valor'
    )
    
    # Remover valores zerados ou nulos
    df_unpivot = df_unpivot.fillna(0)
    df_unpivot = df_unpivot[df_unpivot['Valor'] > 0]
    
    # 6. Calcular o Score HHI
    df_unpivot['Total_Fundo'] = df_unpivot.groupby('CNPJ_FUNDO_CLASSE')['Valor'].transform('sum')
    df_unpivot['Share_Setor'] = (df_unpivot['Valor'] / df_unpivot['Total_Fundo']) * 100
    df_unpivot['Share_Quadrado'] = df_unpivot['Share_Setor'] ** 2
    
    # Somar os quadrados por fundo
    df_score = df_unpivot.groupby(['CNPJ_FUNDO_CLASSE', 'DT_COMPTC'])['Share_Quadrado'].sum().reset_index()
    df_score.rename(columns={'Share_Quadrado': 'HHI_Setorial'}, inplace=True)
    
    # Calcular a Nota (0 a 10)
    df_score['Score_Diversificacao_Setorial'] = 10 - ((df_score['HHI_Setorial'] / 10000) * 10)
    df_score['Score_Diversificacao_Setorial'] = df_score['Score_Diversificacao_Setorial'].clip(lower=0, upper=10)
    
    # 7. Salvar no banco de DESTINO
    nome_tabela_destino = 'Fato_Score_Setorial'
    df_score.to_sql(nome_tabela_destino, conexao_escrita, if_exists='replace', index=False)
    
    print(f"Sucesso! Tabela '{nome_tabela_destino}' salva no banco 'fidc_metrics.db' dentro da pasta database.")

# Executar a função
try:
    calcular_e_salvar_score_setorial(conn_origem, conn_destino)
except Exception as e:
    print(f"Erro durante a execução: {e}")
finally:
    # Sempre fechar as conexões
    conn_origem.close()
    conn_destino.close()