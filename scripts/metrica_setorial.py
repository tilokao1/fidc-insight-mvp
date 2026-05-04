import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

print("🚀 Iniciando Score Setorial (versão BI)...")

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=NullPool,
)

def calcular_e_salvar_score_setorial(conexao_engine):

    df_tab2 = pd.read_sql_query('SELECT * FROM "inf_mensal_fidc_tab_II"', conexao_engine)

    if df_tab2.empty:
        print("Erro: tabela vazia.")
        return

    data_recente = df_tab2['DT_COMPTC'].max()
    df_tab2 = df_tab2[df_tab2['DT_COMPTC'] == data_recente]

    colunas_id = ['CNPJ_FUNDO_CLASSE', 'DT_COMPTC']
    colunas_remover = [
        'TAB_II_VL_CARTEIRA',
        'TAB_II_C_VL_COMERC',
        'TAB_II_D_VL_SERV',
        'TAB_II_F_VL_FINANC',
        'TAB_II_H_VL_FACTOR',
        'TAB_II_I_VL_SETOR_PUBLICO'
    ]

    colunas_setores = [
        col for col in df_tab2.columns
        if col.startswith('TAB_II_') and col not in colunas_remover
    ]

    # =========================
    # UNPIVOT
    # =========================
    df_unpivot = pd.melt(
        df_tab2,
        id_vars=colunas_id,
        value_vars=colunas_setores,
        var_name='setor',
        value_name='valor'
    )

    df_unpivot = df_unpivot.fillna(0)
    df_unpivot = df_unpivot[df_unpivot['valor'] > 0]

    # =========================
    # SHARE (0–1)
    # =========================
    df_unpivot['total_fundo'] = df_unpivot.groupby('CNPJ_FUNDO_CLASSE')['valor'].transform('sum')
    df_unpivot['share'] = df_unpivot['valor'] / df_unpivot['total_fundo']

    # =========================
    # HHI
    # =========================
    df_unpivot['quadrado'] = df_unpivot['share'] ** 2

    df_score = df_unpivot.groupby(
        ['CNPJ_FUNDO_CLASSE', 'DT_COMPTC']
    )['quadrado'].sum().reset_index()

    df_score.rename(columns={'quadrado': 'HHI_Setorial'}, inplace=True)

    # =========================
    # SCORE
    # =========================
    df_score['score_setorial'] = (1 - df_score['HHI_Setorial']) * 10
    df_score['score_setorial'] = df_score['score_setorial'].clip(0, 10)

    # =========================
    # MÉTRICAS EXPLICATIVAS
    # =========================

    # qtd setores
    qtd = df_unpivot.groupby('CNPJ_FUNDO_CLASSE')['setor'].count().reset_index()
    qtd.rename(columns={'setor': 'qtd_setores'}, inplace=True)

    # maior setor
    max_setor = df_unpivot.groupby('CNPJ_FUNDO_CLASSE')['share'].max().reset_index()
    max_setor.rename(columns={'share': 'maior_setor'}, inplace=True)

    # top 3
    top3 = (
        df_unpivot.sort_values(['CNPJ_FUNDO_CLASSE', 'share'], ascending=False)
        .groupby('CNPJ_FUNDO_CLASSE')
        .head(3)
    )

    top3_sum = top3.groupby('CNPJ_FUNDO_CLASSE')['share'].sum().reset_index()
    top3_sum.rename(columns={'share': 'top3_setores'}, inplace=True)

    # merge
    df_score = df_score.merge(qtd, on='CNPJ_FUNDO_CLASSE')
    df_score = df_score.merge(max_setor, on='CNPJ_FUNDO_CLASSE')
    df_score = df_score.merge(top3_sum, on='CNPJ_FUNDO_CLASSE')

    # =========================
    # CLASSIFICAÇÃO
    # =========================
    def classificar(score):
        if score >= 8:
            return "Alta Diversificação"
        elif score >= 5:
            return "Média Diversificação"
        else:
            return "Baixa Diversificação"

    df_score['classificacao'] = df_score['score_setorial'].apply(classificar)

    # =========================
    # SALVAR PRINCIPAL
    # =========================
    df_score.to_sql(
        "score_3_metrica_2",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    # =========================
    # TABELA DETALHE (BI)
    # =========================
    df_unpivot.to_sql(
        "score_3_metrica_2_detalhe",
        conexao_engine,
        if_exists="replace",
        index=False
    )

    print("✅ Score setorial pronto para BI!")

try:
    calcular_e_salvar_score_setorial(engine)
except Exception as e:
    print(f"Erro: {e}")