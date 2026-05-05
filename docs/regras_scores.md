# Métricas FIDC Insight

Com base nos informes do CVM são criados dois módulos, onde no primeiro temos o disgnóstico de risco e no segundo temos a análise de desempenho e valor.

---

### Score 1: Qualidade dos Ativos (Risco de Crédito)
Mede o risco intrínseco de inadimplência da carteira.

#### Métrica 1.1: Taxa de Inadimplência Atual
**Conceito:** Quanto da carteira está com pagamento atrasado hoje?  
**Tabelas:** inf_mensal_fidc_tab_I (para inadimplentes e total da carteira).  
**Cáculo:** (tab_I.TAB_I2A3_VL_CRED_INAD / tab_I.TAB_I2_VL_CARTEIRA)  

#### Métrica 1.2: Estratégia "Distressed"
**Conceito:** Qual o nível de exposição da carteira a créditos problemáticos?
**Tabelas:** inf_mensal_fidc_tab_I
**Cáculo:** MAX ((tab_I.TAB_I2A5_VL_CRED_VENCIDO_PENDENTE, tab_I.TAB_I2A6_VL_CRED_EMP_RECUP) / tab_I.TAB_I2_VL_CARTEIRA)

#### Métrica 1.3: Nível de Garantia (Coobrigação)
**Conceito:** Qual % da carteira possui proteção adicional por meio de garantias?
**Tabelas:** inf_mensal_fidc_tab_X_7 e inf_mensal_fidc_tab_I.
**Cáculo:** (tab_X_7.TAB_X_VL_GARANTIA_DIRCRED / tab_I.TAB_I2_VL_CARTEIRA)

#### Métrica 1.4: Risco Oculto (Proxy de Agressividade da Carteira)
**Conceito:** O fundo apresenta comportamento compatível com maior nível de risco na carteira?
**Tabelas:** inf_mensal_fidc_tab_X_3
**Cáculo:** ABS(tab_X_3.TAB_X_VL_RENTAB_MES) normalizado pelo percentil 95

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

#### Métrica 4.3: Alinhamento do Gestor
**Conceito:** O fundo está ganhando ou perdendo investidores (cotistas)?
**Tabelas:**  inf_mensal_fidc_tab_X_1
**Cáculo:** Variacao_Cotistas = SUM(TAB_X_NR_COTST)[Mês Atual] - SUM(TAB_X_NR_COTST)[Mês Anterior]
**Observação:** Como a tabela registra uma linha por classe/série do fundo, o número de cotistas é somado por CNPJ + mês antes da comparação temporal. O LAG() é aplicado sobre esse total consolidado, garantindo que a variação reflita o fundo como um todo e não comparações entre séries distintas.

#### Verificação de Administradores com Processo Sancionador 
**Conceito:** Quais Administradores estão com processos Sancionadores na CVM(Comissão de Valores Mobiliários) ?
**Tabelas:**  inf_mensal_fidc_tab_I e inf_mensal_fidc_tab_IV
**Consulta Externa:**  https://sistemas.cvm.gov.br/asp/cvmwww/inqueritos/formbuscapas.asp
**Cálculo:** Filtram-se os dados bancários pela data de competência (DT_COMPTC) mais recente, unindo as Tabelas I e IV. Isola-se um array contendo apenas os CNPJs únicos dos Administradores, garantindo que o processamento seja feito por entidade e não por fundo. Realiza-se uma requisição HTTP (POST) no formulário da CVM para cada CNPJ único. O algoritmo faz o parsing (leitura) da estrutura HTML retornada e contabiliza a quantidade de linhas presentes na tabela de resultados da CVM. O valor absoluto total é mapeado de volta para o banco de dados na coluna de volumetria QTD_PROC_CVM, atrelando o risco a todos os fundos sob o guarda-chuva daquele administrador.
**Observação:** Tratamento de Firewall: A extração externa exige a injeção de um Header de User-Agent (simulando um navegador real) e delays estratégicos (pausas de ~1.5s a 2s entre consultas) para evitar que o WAF do governo bloqueie o IP da aplicação com erros de rede (ex: Errno 101: Network is unreachable).
O mapeamento em memória por CNPJs únicos evita requisições redundantes, reduzindo o tempo de processamento em banco de horas para poucos minutos.