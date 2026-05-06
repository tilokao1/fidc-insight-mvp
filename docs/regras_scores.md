# Métricas FIDC Insight

Com base nos informes da CVM, são criados dois módulos: no primeiro, temos o diagnóstico de risco e, no segundo, a análise de governança e estrutura.

---
### Score Qualidade dos Ativos
Mede o risco intrínseco da gestão do fundo, abrangendo sua proteção, liquidez, exposição e desvios.  

#### Métrica Proteção de Caixa  
**Conceito:** Quanto do patrimônio está disponível imediatamente?  
**Tabela(s):** inf_mensal_fidc_tab_I  
**Cálculo:** "TAB_I1_VL_DISP" / "TAB_I_VL_ATIVO"  
**Observação:** Quanto maior, mais colchão de segurança.  

#### Métrica Liquidez de Curto Prazo  
**Conceito:** Quanto do fundo retorna em até 90 dias?  
**Tabela(s):** inf_mensal_fidc_tab_X_5  
**Cálculo:** ("TAB_X_VL_LIQUIDEZ_0" + "TAB_X_VL_LIQUIDEZ_30" + "TAB_X_VL_LIQUIDEZ_60" + "TAB_X_VL_LIQUIDEZ_90") / ("TAB_X_VL_LIQUIDEZ_0" + "TAB_X_VL_LIQUIDEZ_30" + "TAB_X_VL_LIQUIDEZ_60" + "TAB_X_VL_LIQUIDEZ_90" + "TAB_X_VL_LIQUIDEZ_180" + "TAB_X_VL_LIQUIDEZ_360" + "TAB_X_VL_LIQUIDEZ_MAIOR_360")  
**Observação:** Quanto maior, mais fácil transformar a carteira em caixa rápido.  

#### Métrica Exposição de Longo Prazo  
**Conceito:** Quanto da carteira leva mais de 1 ano para retornar?  
**Tabela(s):** inf_mensal_fidc_tab_V  
**Cálculo:** ("TAB_V_A7_VL_PRAZO_VENC_360" + "TAB_V_A7_VL_PRAZO_VENC_720" + "TAB_V_A7_VL_PRAZO_VENC_1080" + "TAB_V_A10_VL_PRAZO_VENC_MAIOR_1080") / "TAB_V_A_VL_DIRCRED_PRAZO"  
**Observação:** Quanto maior o valor, mais longa e "travada" é a carteira.  

#### Métrica Desvio de Desempenho
**Conceito:** O quanto o desempenho real divergiu do esperado?
**Tabela(s):** inf_mensal_fidc_tab_X_6  
**Cálculo:** Desvio = "TAB_X_PR_DESEMP_REAL" - "TAB_X_PR_DESEMP_ESPERADO"
Métrica é normalizada através da divisão pelo limite (P95). Esse resultado é então limitado ("clipado") para que nunca seja menor que 0 ou maior que 1.  
**Observação:** Se o valor for baixo, o fundo performou perto do esperado. Se o valor for alto, o fundo se desviou muito do esperado.  

#### Métrica Número de Setores Ativos  
**Conceito:** Em quantos setores o fundo está exposto?  
**Tabela(s):** inf_mensal_fidc_tab_II  
**Cálculo:** Todas as 27 colunas que representam os setores ou segmentos são convertidas para o formato numérico. Valores inválidos ou nulos (NaN) são padronizados como zero. O script percorre os dados de cada fundo (por linha) e verifica o valor alocado em cada uma das 27 colunas setoriais. Um setor só é considerado "ativo" se o seu valor for estritamente maior que zero. O resultado da métrica é a soma simples de quantas colunas, dentre as 27 avaliadas, retornaram verdadeiro para a condição de valor maior que zero.  
**Observação:** Valores mais altos indicam que o fundo é mais diversificado.  

#### Métrica Concentração de Cedentes
**Conceito:** O fundo depende de poucas empresas para originar seus créditos?  
**Tabela(s):**  inf_mensal_fidc_tab_I  
**Cálculo:**  Share = Participação do Cedente / Total de Participações do fundo. Uso de Índice Herfindahl-Hirschman (HHI) para medir a concentração e inversão da lógica para ficar mais intuitivo. 
**Observação:**  Após o cálculo, o fundo é classificado:  
* Nota $\ge$ 8: Alta Diversificação.  
* Nota entre 5 e 7.99: Média Diversificação.
* Nota $<$ 5: Baixa Diversificação.  

#### Métrica Concentração Setorial
**Conceito:**  O fundo está muito exposto a um único setor da economia?  
**Tabela(s):** inf_mensal_fidc_tab_II
**Cálculo:** Share = Valor do Setor / Valor Total Exposto. Uso de Índice Herfindahl-Hirschman (HHI) para medir a concentração e inversão da lógica para ficar mais intuitivo. 
**Observação:**  Após o cálculo o fundo é classificado conforme abaixo:  
* Nota $\ge$ 8: Alta Diversificação.  
* Nota entre 5 e 7.99: Média Diversificação.  
* Nota $<$ 5: Baixa Diversificação.  

### Score Governança e Estrutura
Mede o risco da gestão do fundo e da sua estrutura de capital.

#### Métrica Proteção ao Investidor (Subordinação)  
**Conceito:** Qual o 'colchão' de segurança (cotas subordinadas e mezanino) que protege os investidores seniores das primeiras perdas em caso de inadimplência?  
**Tabela(s):**  inf_mensal_fidc_tab_X_2 (para calcular o PL das classes protetoras) e inf_mensal_fidc_tab_IV (para o PL Total do Fundo).  
**Cálculo:** Percentual_Subordinação = (PL_Classes_Protetoras / PL_Total_Fundo) * 100  
**Observação:** PL_Classes_Protetoras = A soma da multiplicação (tab_X_2.TAB_X_QT_COTA * tab_X_2.TAB_X_VL_COTA) apenas para as linhas onde a coluna TAB_X_CLASSE_SERIE contiver as palavras "Subordinada" ou "Mezanino". PL_Total_Fundo = tab_IV.TAB_IV_A_VL_PL (Patrimônio Líquido Total).

#### Métrica Retenção de cotistas
**Conceito:** O fundo está ganhando ou perdendo investidores (cotistas)?  
**Tabela(s):**  inf_mensal_fidc_tab_X_1  
**Cálculo:** Variacao_Cotistas = SUM(TAB_X_NR_COTST)[Mês Atual] - SUM(TAB_X_NR_COTST)[Mês Anterior]  
**Observação:** Como a tabela registra uma linha por classe/série do fundo, o número de cotistas é somado por CNPJ + mês antes da comparação temporal. O LAG() é aplicado sobre esse total consolidado, garantindo que a variação reflita o fundo como um todo e não comparações entre séries distintas.  

#### Métrica Administradores com Processo Sancionador 
**Conceito:** Quais Administradores estão com processos Sancionadores na CVM(Comissão de Valores Mobiliários)?  
**Tabela(s):**  inf_mensal_fidc_tab_I e inf_mensal_fidc_tab_IV  
**Consulta Externa:**  https://sistemas.cvm.gov.br/asp/cvmwww/inqueritos/formbuscapas.asp  
**Cálculo:** Filtram-se os dados bancários pela data de competência (DT_COMPTC) mais recente, unindo as Tabelas I e IV. Isola-se um array contendo apenas os CNPJs únicos dos Administradores, garantindo que o processamento seja feito por entidade e não por fundo. Realiza-se uma requisição HTTP (POST) no formulário da CVM para cada CNPJ único. O algoritmo faz o parsing (leitura) da estrutura HTML retornada e contabiliza a quantidade de linhas presentes na tabela de resultados da CVM. O valor absoluto total é mapeado de volta para o banco de dados na coluna de volumetria QTD_PROC_CVM, atrelando o risco a todos os fundos sob o guarda-chuva daquele administrador.  
**Observação:** Tratamento de Firewall: A extração externa exige a injeção de um Header de User-Agent (simulando um navegador real) e delays estratégicos (pausas de ~1.5s a 2s entre consultas) para evitar que o WAF do governo bloqueie o IP da aplicação com erros de rede (ex: Errno 101: Network is unreachable).
O mapeamento em memória por CNPJs únicos evita requisições redundantes, reduzindo o tempo de processamento em banco de horas para poucos minutos.