import os
from sqlalchemy import create_engine, text

# URL do banco vinda do Secret do GitHub
DATABASE_URL = os.getenv("DATABASE_URL")

# Mapeamento de Tabelas e Colunas para limpeza
REGRAS_LIMPEZA = {
    "inf_mensal_fidc_tab_I": ["TAB_I2A3_VL_CRED_INAD", "TAB_I1_VL_DISP", "PRAZO_PAGTO_RESGATE", "TAB_I2A12_PR_CEDENTE_1"],
    "inf_mensal_fidc_tab_II": [
        "TAB_II_A_VL_INDUST", "TAB_II_B_VL_IMOBIL", "TAB_II_C_VL_COMERC", "TAB_II_C1_VL_COMERC",
        "TAB_II_C2_VL_VAREJO", "TAB_II_C3_VL_ARREND", "TAB_II_D_VL_SERV", "TAB_II_D1_VL_SERV",
        "TAB_II_D2_VL_SERV_PUBLICO", "TAB_II_D3_VL_SERV_EDUC", "TAB_II_D4_VL_ENTRET",
        "TAB_II_E_VL_AGRONEG", "TAB_II_F_VL_FINANC", "TAB_II_F1_VL_CRED_PESSOA",
        "TAB_II_F2_VL_CRED_PESSOA_CONSIG", "TAB_II_F3_VL_CRED_CORP", "TAB_II_F4_VL_MIDMARKET",
        "TAB_II_F5_VL_VEICULO", "TAB_II_F6_VL_IMOBIL_EMPRESA", "TAB_II_F7_VL_IMOBIL_RESID",
        "TAB_II_F8_VL_OUTRO", "TAB_II_G_VL_CREDITO", "TAB_II_H_VL_FACTOR", "TAB_II_H1_VL_PESSOA",
        "TAB_II_H2_VL_CORP", "TAB_II_I_VL_SETOR_PUBLICO", "TAB_II_I1_VL_PRECAT",
        "TAB_II_I2_VL_TRIBUT", "TAB_II_I3_VL_ROYALTIES", "TAB_II_I4_VL_OUTRO",
        "TAB_II_J_VL_JUDICIAL", "TAB_II_K_VL_MARCA"
    ],
    "inf_mensal_fidc_tab_V": [
        "TAB_V_A1_VL_PRAZO_VENC_30", "TAB_V_A2_VL_PRAZO_VENC_60", "TAB_V_A3_VL_PRAZO_VENC_90",
        "TAB_V_A4_VL_PRAZO_VENC_120", "TAB_V_A4_VL_PRAZO_VENC_150", "TAB_V_A4_VL_PRAZO_VENC_180",
        "TAB_V_A4_VL_PRAZO_VENC_360", "TAB_V_A4_VL_PRAZO_VENC_720", "TAB_V_A4_VL_PRAZO_VENC_1080",
        "TAB_V_A10_VL_PRAZO_VENC_MAIOR_1080"
    ],
    "inf_mensal_fidc_tab_IV": ["TAB_IV_B_VL_PL_MEDIO"],
    "inf_mensal_fidc_tab_X_1": ["TAB_X_NR_COTST"],
    "inf_mensal_fidc_tab_X_2": ["TAB_X_QT_COTA"],
    "inf_mensal_fidc_tab_X_3": ["TAB_X_VL_RENTAB_MES"],
    "inf_mensal_fidc_tab_X_5": [
        "TAB_X_VL_LIQUIDEZ_0", "TAB_X_VL_LIQUIDEZ_30", "TAB_X_VL_LIQUIDEZ_60",
        "TAB_X_VL_LIQUIDEZ_90", "TAB_X_VL_LIQUIDEZ_180", "TAB_X_VL_LIQUIDEZ_360",
        "TAB_X_VL_LIQUIDEZ_MAIOR_360"
    ],
    "inf_mensal_fidc_tab_X_6": ["TAB_X_PR_DESEMP_ESPERADO", "TAB_X_PR_DESEMP_REAL"],
    "inf_mensal_fidc_tab_X_7": ["TAB_X_VL_GARANTIA_DIRCRED", "TAB_X_PR_GARANTIA_DIRCRED"]
}

def limpar_dados():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        for tabela, colunas in REGRAS_LIMPEZA.items():
            print(f"Limpando tabela: {tabela}")
            for col in colunas:
                # O comando COALESCE(coluna, 0) substitui NULL por 0 no próprio banco
                query = text(f"UPDATE {tabela} SET \"{col}\" = COALESCE(\"{col}\", 0) WHERE \"{col}\" IS NULL")
                conn.execute(query)
    print("Limpeza concluída com sucesso!")

if __name__ == "__main__":
    limpar_dados()