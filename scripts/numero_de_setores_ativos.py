# Importa o módulo os, usado para acessar variáveis de ambiente
import os

# Importa a biblioteca pandas, usada para manipulação e análise de dados em tabelas
import pandas as pd

# Importa a função create_engine do SQLAlchemy, usada para criar a conexão com o banco
from sqlalchemy import create_engine

# Importa NullPool para evitar o uso de pool persistente de conexões
from sqlalchemy.pool import NullPool

# Importa numpy, usado para cálculos numéricos e tratamento de valores nulos
import numpy as np


# Exibe uma mensagem indicando o início da execução da métrica
print("🚀 Iniciando Métrica - Número de Setores Ativos...")


# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")


# Cria a conexão com o banco usando a URL armazenada na variável de ambiente
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


# Define a função responsável por calcular e salvar a métrica de número de setores ativos
def calcular_e_salvar_num_setores_ativos(conexao_engine):

    # Query SQL que seleciona todos os dados da tabela setorial dos FIDCs
    query = '''
    SELECT * FROM "inf_mensal_fidc_tab_II"
    '''

    # Executa a query no banco de dados e carrega o resultado em um DataFrame pandas
    df = pd.read_sql_query(query, conexao_engine)

    # Lista com as colunas que representam os setores ou segmentos de exposição do fundo
    cols_setoriais = [
        "TAB_II_A_VL_INDUST",              # Indústria
        "TAB_II_B_VL_IMOBIL",              # Imobiliário
        "TAB_II_C1_VL_COMERC",             # Comércio
        "TAB_II_C2_VL_VAREJO",             # Varejo
        "TAB_II_C3_VL_ARREND",             # Arrendamento
        "TAB_II_D1_VL_SERV",               # Serviços
        "TAB_II_D2_VL_SERV_PUBLICO",       # Serviços públicos
        "TAB_II_D3_VL_SERV_EDUC",          # Serviços educacionais
        "TAB_II_D4_VL_ENTRET",             # Entretenimento
        "TAB_II_E_VL_AGRONEG",             # Agronegócio
        "TAB_II_F1_VL_CRED_PESSOA",        # Crédito pessoal
        "TAB_II_F2_VL_CRED_PESSOA_CONSIG", # Crédito pessoal consignado
        "TAB_II_F3_VL_CRED_CORP",          # Crédito corporativo
        "TAB_II_F4_VL_MIDMARKET",          # Midmarket
        "TAB_II_F5_VL_VEICULO",            # Veículos
        "TAB_II_F6_VL_IMOBIL_EMPRESA",     # Imobiliário empresarial
        "TAB_II_F7_VL_IMOBIL_RESID",       # Imobiliário residencial
        "TAB_II_F8_VL_OUTRO",              # Outros créditos financeiros
        "TAB_II_G_VL_CREDITO",             # Cartão/crédito
        "TAB_II_H1_VL_PESSOA",             # Pessoa física
        "TAB_II_H2_VL_CORP",               # Pessoa jurídica/corporativo
        "TAB_II_I1_VL_PRECAT",             # Precatórios
        "TAB_II_I2_VL_TRIBUT",             # Créditos tributários
        "TAB_II_I3_VL_ROYALTIES",          # Royalties
        "TAB_II_I4_VL_OUTRO",              # Outros direitos creditórios
        "TAB_II_J_VL_JUDICIAL",            # Créditos judiciais
        "TAB_II_K_VL_MARCA"                # Marcas/patentes ou ativos relacionados
    ]

    # Converte todas as colunas setoriais para formato numérico
    # Caso algum valor não possa ser convertido, ele vira NaN
    # Em seguida, os valores NaN são substituídos por 0
    for col in cols_setoriais:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Calcula o número de setores ativos em cada linha/fundo
    # A lógica considera setor ativo quando o valor da coluna setorial é maior que zero
    df["numero_setores_ativos"] = (df[cols_setoriais] > 0).sum(axis=1)

    # Cria um DataFrame final apenas com as colunas que serão salvas no banco
    df_resultado = df[[
        "CNPJ_FUNDO_CLASSE",       # Identificador do fundo/classe
        "DENOM_SOCIAL",            # Nome do fundo
        "DT_COMPTC",               # Data de competência
        "numero_setores_ativos"    # Quantidade de setores com exposição maior que zero
    ]].copy()

    # Salva o resultado no banco de dados
    df_resultado.to_sql(
        "score_num_setores_ativos",  # Nome da tabela que será criada/substituída
        conexao_engine,              # Conexão com o banco de dados
        if_exists="replace",         # Substitui a tabela caso ela já exista
        index=False                  # Não salva o índice do DataFrame como coluna
    )

    # Exibe mensagem confirmando que a tabela foi salva com sucesso
    print("✅ score_num_setores_ativos salvo com sucesso!")


# Executa a função, passando a conexão criada com o banco de dados
calcular_e_salvar_num_setores_ativos(engine)
