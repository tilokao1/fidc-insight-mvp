# Métricas FIDC Insight

Com base nos informes do CVM são criados dois módulos, onde no primeiro temos o disgnóstico de risco e no segundo temos a análise de desempenho e valor.

---

### Score 1: Qualidade dos Ativos (Risco de Crédito)
Mede o risco intrínseco de inadimplência da carteira.

#### Métrica 1.1: Taxa de Inadimplência Atual
**Conceito:** Quanto da carteira está com pagamento atrasado hoje?
**Tabelas:** 
**Cáculo:**

#### Métrica 1.2: Estratégia "Distressed"
**Conceito:** Qual % da carteira foi comprada já problemática?
**Tabelas:** 
**Cáculo:**

#### Métrica 1.3: Nível de Garantia (Coobrigação)
**Conceito:** Qual % da carteira tem uma garantia extra do originador (cedente)?
**Tabelas:** 
**Cáculo:**

#### Métrica 1.4: Risco Oculto (Compra de Ativos Subordinados)
**Conceito:** O fundo está comprando 'sobra' de outras operações (ativos que já são subordinados)?
**Tabelas:** 
**Cáculo:**

### Score 2: Risco de Liquidez
Mede o risco do fundo não ter dinheiro em caixa para pagar os resgates dos investidores.

#### Métrica 2.1: Perfil de Vencimento da Carteira (Maturidade)
**Conceito:** Como se distribui o prazo de recebimento dos ativos do fundo?
**Tabelas:** inf_mensal_fidc_tab_X_5 (todas as colunas VL_LIQUIDEZ_...) e inf_mensal_fidc_tab_I.
**Cáculo:** % Curto Prazo (Até 90d) = (TAB_X.VL_LIQUIDEZ_1_30 + TAB_X.VL_LIQUIDEZ_31_60 + TAB_X.VL_LIQUIDEZ_61_90) / tab_I.TAB_I2_VL_CARTEIRA * 100
% Longo Prazo (> 360d) = (TAB_X.VL_LIQUIDEZ_ACIMA_360) / TAB_X.TAB_I2_VL_CARTEIRA * 100

#### Métrica 2.2: Descasamento de Prazos
**Conceito:** O prazo que o fundo tem para pagar investidores é compatível com o prazo que ele tem para receber seus ativos?
**Tabelas:** inf_mensal_fidc_tab_I (para o passivo) e inf_mensal_fidc_tab_X_5 (para o ativo).
**Cáculo:** É uma regra de negócio, um "Alerta": Prazo_Resgate_Investidor = tab_I.PRAZO_PAGTO_RESGATE (em dias)
SE Prazo_Resgate_Investidor <= 90 DIAS E % Curto Prazo (Até 90d) < 20% ENTÃO "RISCO DE LIQUIDEZ ALTO"

### Score 3: Risco de Diversificação
Mede o risco do fundo estar "colocando todos os ovos na mesma cesta.

#### Métrica 3.1: Concentração de Originadores (Cedentes)
**Conceito:** O fundo depende de poucas empresas para originar seus créditos?
**Tabelas:**  inf_mensal_fidc_tab_I
**Cáculo:** Percentual_Top_1_Cedente = tab_I.TAB_I2A12_PR_CEDENTE_1 (A tabela já dá o percentual!).

#### Métrica 3.2: Concentração Setorial
**Conceito:**  O fundo está muito exposto a um único setor da economia?
**Tabelas:** inf_mensal_fidc_tab_I (várias colunas TAB_II_..._VL_...) e inf_mensal_fidc_tab_II (total).
**Cáculo:** Percentual_Maior_Setor = (MAX(tab_II.TAB_II_A_VL_INDUST, tab_II.TAB_II_C_VL_COMERC, ...) / tab_II.TAB_II_VL_CARTEIRA) * 100

### Score 4: Governança e Estrutura
Mede o risco da gestão do fundo e da sua estrutura de capital.

#### Métrica 4.1: Proteção ao Investidor (Subordinação)
**Conceito:** Qual o 'colchão' de segurança (cotas subordinadas e mezanino) que protege os investidores seniores das primeiras perdas em caso de inadimplência?
**Tabelas:**  inf_mensal_fidc_tab_X_2 (para calcular o PL das classes protetoras) e inf_mensal_fidc_tab_IV (para o PL Total do Fundo).
**Cáculo:** Percentual_Subordinação = (PL_Classes_Protetoras / PL_Total_Fundo) * 100
Onde: PL_Classes_Protetoras = A soma da multiplicação (tab_X_2.TAB_X_QT_COTA * tab_X_2.TAB_X_VL_COTA) apenas para as linhas onde a coluna TAB_X_CLASSE_SERIE contiver as palavras "Subordinada" ou "Mezanino". PL_Total_Fundo = tab_IV.TAB_IV_A_VL_PL (Patrimônio Líquido Total).

#### Métrica 4.2: Alinhamento do Gestor
**Conceito:** O gestor está concentrando o risco do fundo comprando créditos de uma única empresa (possível conflito de interesse/favorecimento)?
**Tabelas:**  inf_mensal_fidc_tab_VII (Encargos e Concentrações) e inf_mensal_fidc_tab_IV (PL).
**Cáculo:** (Tabela VII.TAB_VII_B1_2_VL_CEDENTE / tab_IV.TAB_IV_A_VL_PL) * 100
Se o resultado for maior que 20% (Regra padrão da CVM para fundos pulverizados), então "ALERTA - Alta Concentração", senão "OK".

#### Métrica 4.3: Alinhamento do Gestor
**Conceito:** O fundo está ganhando ou perdendo investidores (cotistas)?
**Tabelas:**  inf_mensal_fidc_tab_X_1
**Cáculo:** Variacao_Cotistas = (tab_X_1.TAB_X_NR_COTST[Mês Atual] - tab_X_1.TAB_X_NR_COTST[Mês Anterior]) (Análise de série temporal)