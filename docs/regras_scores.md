# Métricas FIDC Insight

Com base nos informes da CVM, são criados dois módulos: no primeiro, temos o diagnóstico de risco e, no segundo, a análise de governança e estrutura.

---
### Score Métricas CVM
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

---

### Score Qualidade dos ativos
Traz um diagnóstico de qualidade dos fundos 

#### Métrica Desvio de Desempenho
**Conceito:** O fundo performou próximo ao que era esperado?
**Tabela(s):** inf_mensal_fidc_tab_X_6  
**Cálculo:** Desvio = ABS("TAB_X_PR_DESEMP_REAL" - "TAB_X_PR_DESEMP_ESPERADO"); A partir desse desvio, é criada uma nota de 0 a 100: score_aderencia_desempenho = 100 - ((Desvio - Limite_Bom) / (Limite_Ruim - Limite_Bom) * 100); Onde:Limite_Bom = 5; Limite_Ruim = 20; O resultado é limitado para nunca ficar abaixo de 0 ou acima de 100.
O resultado é limitado para nunca ficar abaixo de 0 ou acima de 100.  
**Observação:** Quanto maior a nota, mais próximo o fundo performou do esperado. Quanto menor a nota, maior foi o desvio entre o desempenho real e o desempenho esperado.

#### Métrica Concentração Setorial
**Conceito:** O fundo está muito exposto a um único setor da economia?  
**Tabela(s):** inf_mensal_fidc_tab_II
**Cálculo:** Share = Valor do Setor / Valor Total Exposto. Uso de Índice Herfindahl-Hirschman (HHI) para medir a concentração e inversão da lógica para ficar mais intuitivo. 
**Observação:** Após o cálculo o fundo é classificado conforme abaixo:  
* Nota $\ge$ 8: Alta Diversificação.  
* Nota entre 5 e 7.99: Média Diversificação.  
* Nota $<$ 5: Baixa Diversificação.  

---

### Score Governança e Estrutura
Mede o risco da gestão do fundo e da sua estrutura de capital.

#### Métrica Administradores com Processo Sancionador 
**Conceito:** Quais Administradores estão com processos Sancionadores na CVM(Comissão de Valores Mobiliários)?  
**Tabela(s):**  inf_mensal_fidc_tab_I e inf_mensal_fidc_tab_IV  
**Consulta Externa:**  https://sistemas.cvm.gov.br/asp/cvmwww/inqueritos/formbuscapas.asp  
**Cálculo:** Filtram-se os dados bancários pela data de competência (DT_COMPTC) mais recente, unindo as Tabelas I e IV. Isola-se um array contendo apenas os CNPJs únicos dos Administradores, garantindo que o processamento seja feito por entidade e não por fundo. Realiza-se uma requisição HTTP (POST) no formulário da CVM para cada CNPJ único. O algoritmo faz o parsing (leitura) da estrutura HTML retornada e contabiliza a quantidade de linhas presentes na tabela de resultados da CVM. O valor absoluto total é mapeado de volta para o banco de dados na coluna de volumetria QTD_PROC_CVM, atrelando o risco a todos os fundos sob o guarda-chuva daquele administrador.  
**Observação:** Tratamento de Firewall: A extração externa exige a injeção de um Header de User-Agent (simulando um navegador real) e delays estratégicos (pausas de ~1.5s a 2s entre consultas) para evitar que o WAF do governo bloqueie o IP da aplicação com erros de rede (ex: Errno 101: Network is unreachable).
O mapeamento em memória por CNPJs únicos evita requisições redundantes, reduzindo o tempo de processamento em banco de horas para poucos minutos.

#### Métrica Retenção de cotistas
**Conceito:** O fundo está ganhando ou perdendo investidores (cotistas)?  
**Tabela(s):**  inf_mensal_fidc_tab_X_1  
**Cálculo:** Variacao_Cotistas = SUM(TAB_X_NR_COTST)[Mês Atual] - SUM(TAB_X_NR_COTST)[Mês Anterior]  
**Observação:** Como a tabela registra uma linha por classe/série do fundo, o número de cotistas é somado por CNPJ + mês antes da comparação temporal. O LAG() é aplicado sobre esse total consolidado, garantindo que a variação reflita o fundo como um todo e não comparações entre séries distintas.  

---

### Score Cedentes e Proteção ao Investidor 
Diagnóstico de concentração de cedentes e proteção ao investidor

#### Métrica Concentração de Cedentes
**Conceito:** O fundo depende de poucas empresas para originar seus créditos?  
**Tabela(s):** inf_mensal_fidc_tab_I  
**Cálculo:** Share = Participação do Cedente / Total de Participações do fundo. Uso de Índice Herfindahl-Hirschman (HHI) para medir a concentração e inversão da lógica para ficar mais intuitivo. 
**Observação:**  Após o cálculo, o fundo é classificado:  
* Nota $\ge$ 8: Alta Diversificação.  
* Nota entre 5 e 7.99: Média Diversificação.
* Nota $<$ 5: Baixa Diversificação.  

#### Métrica Proteção ao Investidor (Subordinação)  
**Conceito:** Qual o 'colchão' de segurança (cotas subordinadas e mezanino) que protege os investidores seniores das primeiras perdas em caso de inadimplência?  
**Tabela(s):**  inf_mensal_fidc_tab_X_2 (para calcular o PL das classes protetoras) e inf_mensal_fidc_tab_IV (para o PL Total do Fundo).  
**Cálculo:** Percentual_Subordinação = (PL_Classes_Protetoras / PL_Total_Fundo) * 100  
**Observação:** PL_Classes_Protetoras = A soma da multiplicação (tab_X_2.TAB_X_QT_COTA * tab_X_2.TAB_X_VL_COTA) apenas para as linhas onde a coluna TAB_X_CLASSE_SERIE contiver as palavras "Subordinada" ou "Mezanino". PL_Total_Fundo = tab_IV.TAB_IV_A_VL_PL (Patrimônio Líquido Total).

---

### Score — Análise de Dados Núclea

Ferramenta de análise de risco para decisão de compra de direitos creditórios por cedente, com base em dados de boletos e indicadores de pagadores fornecidos pela base Núclea.  


#### Fontes de Dados

O dashboard consome dois arquivos CSV carregados pelo usuário:

| Arquivo | Campos esperados |
|---|---|
| **Boletos.csv** | `id_boleto`, `id_pagador`, `id_beneficiario`, `dt_emissao`, `dt_vencimento`, `dt_pagamento`, `vlr_nominal`, `vlr_baixa`, `tipo_baixa`, `tipo_especie` |
| **CNPJs.csv** | `id_cnpj`, `cd_cnae_prin`, `uf`, `sacado_indice_liquidez_1m`, `cedente_indice_liquidez_1m`, `score_materialidade_evolucao`, `media_atraso_dias`, `indicador_liquidez_quantitativo_3m`, `share_vl_inad_pag_bol_6_a_15d`, `score_quantidade_v2`, `score_materialidade_v2` |

**Cruzamento:** o campo `id_pagador` do arquivo de Boletos é cruzado com `id_cnpj` do arquivo de CNPJs (normalizado para minúsculas e sem espaços) para enriquecer cada pagador com seus indicadores de risco.  


#### Lógica de Processamento (`processData`)

Ao clicar em **Analisar**, o sistema:

1. Monta um dicionário `cnpjMap` indexando cada linha de CNPJs pelo `id_cnpj` normalizado.
2. Agrupa os boletos por `id_beneficiario` (cedente), formando um objeto por cedente com todos os seus boletos.
3. Para cada cedente, extrai os `id_pagador` únicos e cruza com `cnpjMap` para obter os dados de CNPJ de cada pagador.
4. Calcula o score do cedente via `calcScorePagadores` e o veredicto via `verdict`.
5. Calcula o valor total em carteira (`vlrTotal`) somando `vlr_nominal` ou `vlr_baixa` de todos os boletos.
6. Calcula o percentual de boletos pagos (`pctPago`) — boletos com `dt_pagamento` preenchida.
7. Ordena todos os cedentes do maior para o menor score.  


#### Score dos Pagadores (`calcScorePagadores`)

**Conceito:** calcula um score de 0 a 100 para um conjunto de pagadores, representando o nível médio de risco de crédito daquele grupo. Quanto maior o score, melhor o perfil de pagamento.  

##### Variáveis utilizadas (médias dos pagadores)

| Variável | Campo CSV | Escala original | Descrição |
|---|---|---|---|
| `liq` | `sacado_indice_liquidez_1m` | 0 a 1 | % de boletos pagos no último mês |
| `liqQ` | `indicador_liquidez_quantitativo_3m` | 0 a 1 | % de boletos pagos nos últimos 3 meses |
| `inad` | `share_vl_inad_pag_bol_6_a_15d` | 0 a 1 | % de boletos com atraso de 6 a 15 dias |
| `atraso` | `media_atraso_dias` | dias (sem limite fixo) | Média de dias de atraso nos pagamentos |
| `mat` | `score_materialidade_v2` | 0 a 1000 | Score de materialidade do pagador |
| `matEvol` | `score_materialidade_evolucao` | 0 a 1000 | Evolução do score de materialidade |
| `qtd` | `score_quantidade_v2` | 0 a 1000 | Score de quantidade de operações |

#### Normalização para escala 0–100

Antes de compor o score, cada variável é normalizada:

```
liqNorm    = min(1, liq)  × 100          → liquidez 1m em %
liqQNorm   = min(1, liqQ) × 100          → liquidez 3m em %
inadInv    = (1 − min(1, inad)) × 100    → inadimplência invertida (0 = ruim, 100 = ótimo)
matNorm    = min(1000, mat) / 10         → materialidade em escala 0–100
atrasoNorm = (1 − min(1, atraso/90)) × 100 → atraso invertido, tolerância de 90 dias
```

> **Nota sobre inversão:** inadimplência e atraso são indicadores negativos — quanto maior, pior. Por isso são invertidos antes de entrar no score, de forma que 100 sempre representa o melhor estado possível.

#### Composição do Score Final

```
Score = (liqNorm × 0,30) + (liqQNorm × 0,18) + (inadInv × 0,27) + (matNorm × 0,15) + (atrasoNorm × 0,10)
```

| Componente | Peso | Justificativa |
|---|---|---|
| Liquidez 1m | **30%** | Principal indicador de capacidade de pagamento recente |
| Inadimplência 6–15d | **27%** | Sinal direto de risco de crédito de curto prazo |
| Liquidez 3m | **18%** | Consistência do comportamento de pagamento |
| Materialidade v2 | **15%** | Relevância e volume do pagador na base |
| Atraso médio | **10%** | Peso menor pois bons pagadores podem ter atraso alto por volume |

### Veredicto de Compra (`verdict`)

**Conceito:** classifica o cedente em uma das três categorias de decisão com base no score e em alertas rígidos de risco.

#### Trava de Risco (Hard Alert)

Antes de aplicar os cortes de score, o sistema verifica se algum indicador crítico está fora do limite aceitável:

```
hardAlert = inad > 0,20  OU  liq < 0,60  OU  liqQ < 0,65
```

Se qualquer uma dessas condições for verdadeira, o cedente **não pode ser classificado como "Comprar"**, independentemente do score.

#### Tabela de Classificação

| Condição | Resultado |
|---|---|
| `hardAlert = true` e `score >= 50` | ⚠ **Análise adicional** |
| `hardAlert = true` e `score < 50` | ✗ **Não Comprar** |
| `hardAlert = false` e `score >= 75` | ✓ **Comprar** |
| `hardAlert = false` e `score >= 50` | ⚠ **Análise adicional** |
| `hardAlert = false` e `score < 50` | ✗ **Não Comprar** |

> **Lógica de proteção:** um cedente com score alto mas inadimplência acima de 20% ou liquidez abaixo dos limites mínimos nunca receberá "Comprar" automaticamente — sempre cairá em "Análise adicional" no mínimo.

## Visualizações do Dashboard

#### Parecer Principal

**Conceito:** exibe o veredicto final do cedente selecionado com destaque visual (verde/laranja/vermelho), o score numérico e o total em carteira.

**Etapas da visualização:**
- **Ícone e título colorido** — reflete o veredicto (`✓ Comprar`, `⚠ Análise adicional`, `✗ Não Comprar`) com cor correspondente
- **Score /100** — número calculado por `calcScorePagadores`, exibido em destaque no canto direito
- **Total em carteira** — soma de `vlr_nominal` (ou `vlr_baixa`) de todos os boletos do cedente, com contagem de boletos e % pagos
- **Texto descritivo** — mensagem automática explicando o motivo do veredicto

**Observações:** o total em carteira usa os boletos originais sem filtro de UF, mesmo quando o filtro de UF está ativo. O score e o veredicto, por outro lado, recalculam com o filtro aplicado.

#### KPIs (5 Cards)

**Conceito:** resumo visual dos 5 principais indicadores médios dos pagadores do cedente selecionado.

**Etapas da visualização:**
- **% Boletos pagos no último mês** — exibe `liq × 100` em %. Verde se ≥ 70%, vermelho se < 70%
- **% Boletos pagos nos últimos 3 meses** — exibe `liqQ × 100` em %. Verde ≥ 80%, laranja ≥ 60%, vermelho < 60%
- **Média de atraso** — exibe `atraso` em dias. Verde ≤ 7d, laranja ≤ 15d, vermelho > 15d
- **% Boletos com atraso 6–15 dias** — exibe `inad × 100` em %. Verde < 10%, laranja < 20%, vermelho ≥ 20%
- **Score de materialidade** — exibe `mat` (escala 0–1000) com subtítulo mostrando evolução (`matEvol`) e quantidade (`qtd`)

**Observações:** os KPIs refletem a média de todos os pagadores do cedente com dados na base de CNPJs. Pagadores sem cruzamento são ignorados no cálculo.  

#### Gráfico de Liquidez por Pagador (`chart-liq`)

**Conceito:** barras horizontais mostrando o índice de liquidez 1m (`sacado_indice_liquidez_1m`) de cada pagador individualmente, com coloração por faixa de risco.

**Etapas da visualização:**
- Exibe os **8 primeiros pagadores** com dados na base de CNPJs (após filtro de UF, se aplicado)
- Barras coloridas: **verde** se liq ≥ 0,80 · **laranja** se liq ≥ 0,50 · **vermelho** se liq < 0,50
- Tooltip exibe o valor exato da liquidez ao passar o mouse
- Altura do gráfico é dinâmica: `max(140, min(n_pagadores, 8) × 32 + 50)` pixels

**Observações:** o gráfico mostra os valores brutos (0 a 1), não convertidos para %. A coloração usa os mesmos limiares do dicionário de dados.

#### Gráfico Comparativo Cedente vs Média Geral (`chart-comp`)

**Conceito:** barras agrupadas comparando os índices médios do cedente selecionado contra a média de todos os cedentes da base, com todos os valores normalizados de 0 a 100 para permitir comparação direta.

**Etapas da visualização:**
- **6 dimensões comparadas:** Liq. 1m · Liq. 3m · Mat. v2 · Mat. evol. · Inadimp. (inv.) · Atraso (inv.)
- **Barra azul** = cedente selecionado · **Barra cinza** = média geral de todos os cedentes
- Inadimplência e atraso são exibidos **invertidos** (maior barra = melhor desempenho)
- Para o atraso, a normalização do gráfico usa referência dinâmica (`max(atraso_cedente, atraso_media, 1)`) para evitar que uma das barras desapareça quando o atraso é muito alto
- Tooltip do atraso exibe os dias reais além do valor normalizado

**Observações:** a normalização do gráfico é apenas visual — o score continua usando a regra fixa de 90 dias de tolerância. A média geral é calculada em tempo real sobre todos os pagadores de todos os cedentes carregados.  

#### Cards de Pagadores Individuais

**Conceito:** grid de cards mostrando cada pagador único do cedente, cruzado individualmente com a base de CNPJs, com seu próprio veredicto e métricas.

**Etapas da visualização:**
- Exibe até **24 pagadores** por cedente (com aviso de quantos foram omitidos)
- Cada card mostra: ID do pagador · UF · CNAE · nº de boletos · semáforo de veredicto individual
- **6 métricas por card:** Liq. 1m (%) · Liq. 3m (%) · Atraso (dias) · Inadimplência (%) · Materialidade v2 · Materialidade evolução
- Pagadores sem dados na base de CNPJs recebem card cinza com "Sem dados"
- O veredicto individual de cada pagador usa a mesma função `verdict` com `hardAlert`, aplicada ao pagador isolado

**Observações:** o filtro de UF afeta quais pagadores aparecem nos cards. O veredicto individual pode diferir do veredicto do cedente, pois o cedente é avaliado pela média de todos os seus pagadores.  

#### Tabela de Boletos

**Conceito:** listagem detalhada dos boletos do cedente selecionado, com cálculo de dias de atraso por boleto.

**Etapas da visualização:**
- Exibe até **100 boletos** (limitação de performance)
- Colunas: ID Boleto · Pagador · Emissão · Vencimento · Pagamento · Valor Nominal · Tipo Baixa · Dias de Atraso
- **Dias de atraso calculados** como `dt_pagamento − dt_vencimento` em dias:
  - Verde: pago antes do vencimento (ex: "3d antes")
  - Vermelho: pago com atraso (ex: "+12d")
  - Laranja: "Em aberto" — sem `dt_pagamento` preenchida

**Observações:** o filtro de UF restringe os boletos exibidos aos pagadores da UF selecionada. IDs longos são truncados na exibição mas o valor completo aparece no tooltip ao passar o mouse.  

#### Ranking Geral de Cedentes

**Conceito:** lista ordenada de todos os cedentes do maior para o menor score, com semáforo de veredicto, barra de score visual e resumo de boletos e valor.

**Etapas da visualização:**
- **Painel de resumo** no topo: contagem de cedentes por categoria (Comprar / Análise / Não Comprar / Total)
- **Lista ordenada** por score decrescente, com posição numérica
- Cada linha mostra: posição · semáforo · nome do cedente · nº de boletos · nº de pagadores · valor total · barra de score · score numérico
- **Filtro de ranking** (dropdown "Filtrar ranking") permite exibir apenas uma categoria
- Clicar em qualquer linha seleciona o cedente e atualiza todo o painel de análise
- O cedente ativo é destacado com borda azul

**Observações:** o ranking é calculado uma única vez no `processData` e reordenado por score. O filtro de UF **não** afeta o ranking — ele usa sempre o score calculado com todos os pagadores do cedente.  

#### Filtros Disponíveis

| Filtro | Efeito |
|---|---|
| **Cedente** | Seleciona o cedente ativo para análise detalhada |
| **UF pagadores** | Filtra KPIs, gráficos, cards e tabela de boletos pelos pagadores da UF selecionada. Recalcula score e veredicto para o subconjunto |
| **Filtrar ranking** | Exibe no ranking apenas cedentes da categoria selecionada (Comprar / Análise adicional / Não Comprar) |


#### Observações Gerais

- O parser de CSV suporta separadores `,` e `;`, campos entre aspas e encoding UTF-8.
- Campos numéricos ausentes ou inválidos são tratados como `0` via `parseFloat(x) || 0`.
- Cedentes sem nenhum pagador cruzado na base de CNPJs recebem score `0` e veredicto **Não Comprar**.
- O campo `cedente_indice_liquidez_1m` está presente no dicionário de dados mas **não é utilizado** nos cálculos — apenas os índices do sacado (pagador) são considerados.
- Todos os gráficos são destruídos e recriados a cada troca de cedente para evitar sobreposição de instâncias do Chart.js.
