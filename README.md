# FIDC Insight

Projeto desenvolvido para criação de uma solução de análise de risco aplicada a Fundos de Investimento em Direitos Creditórios (FIDCs).

Este repositório contém apenas o código-fonte, documentação técnica e estrutura do projeto.

---

## 🎯 Objetivo do Projeto

Identificar padrões e desafios encontrados pelos Fundo de Investimento em Direitos Creditórios(FIDC), utilizando os dados da Núclea e dados da CVM.  
Aplicação, tratamento e cálculos de métricas de risco em Python, armazenamento dos dados em banco PostgreSQL, hospedado na AWS e visualizações estratégicas em Power BI Online.

---

## 📂 Estrutura do Repositório

### Scripts
Contém os scripts Python utilizados no projeto:

- ETL (coleta, limpeza e transformação dos dados)
- Cálculo de Scores e métricas
- Atualização do banco PostgreSQL no AWS
- Funções auxiliares

Esses arquivos representam o núcleo técnico do projeto.

---

### Docs
Documentação técnica do projeto:

- Regras de cálculo dos Scores (1–4)
- Definição dos KPIs
- Dicionário de dados
- Decisões arquiteturais

---

### 📊 PowerPoint
Contém as apresentações dos respectivos sprints(.pptx) entregues em cada etapa  acadêmica do projeto.

---

### 📖 Readme
Documento principal explicando:
- Estrutura do projeto
- Tecnologias utilizadas
- Organização das pastas
- Fluxo de trabalho

---

## 🚫 Arquivos que NÃO ficam no repositório

Para manter organização e evitar conflitos, os seguintes arquivos não são versionados:

- Banco PostgreSQL
- Dados brutos da CVM
- Dados brutos da Núclea
- Arquivos Power BI (`*.pbib`)
- Outputs gerados automaticamente
- Cache do Python

Esses arquivos são mantidos em pasta compartilhada do grupo.

---

## 🧱 Tecnologias Utilizadas

- Python (Pandas, SQLAlchemy, psycopg2-binary, python-dotenv, requests e python-dateutil)
- PostgreSQL (Banco de Dados Online)
- Power BI Online (Visualização)
- Git e GitHub (Versionamento)

---

## 🔄 Fluxo de Atualização do Projeto

1. Dados são coletados e tratados via Python
2. Banco PostgreSQL é atualizado no AWS através do Supabase
3. Scores e métricas são calculados
4. Power BI consome os dados para visualização
5. PPT é atualizado com os resultados e entregas.

---

## 🔜 Próximos Passos

* Realizar mais análises a fim de melhorar o entendimento dos dados da base de dados.
* Inserir os dados da parceira Núclea para comparação e talvez uma possibilidade de vínculo com as bases de informe CVM.
* Verificar a possibilidade de inserção da Matriz de Risco vs. Retorno.
* Utilizar algoritmos de Machine Learning para analise preditiva com previsão de inadimplência.

---

Link para acesso à aplicação: [FIDC Insight](https://app.powerbi.com/view?r=eyJrIjoiMTMxYjMyMzktNjBhNC00N2ZkLTg0M2YtZDVhMmY5YTdlMDYxIiwidCI6IjY4ZWJmNmZlLTdmNzUtNGNmNS1hNWJmLTAzYWQyNGE3NjRiNCJ9)

## 👥 Equipe

Projeto desenvolvido pela equipe Data Insight.

<table align="center" border="0" cellspacing="0" cellpadding="20">
  <tr>
    <td align="center" style="border:none;">
      <a href="https://github.com/DanielaPSilva">
        <img src="./assets/imagem-daniela.png" width="100px" style="border-radius:50%;" alt="Daniela Silva"/><br/>
        <b>Daniela Silva</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/fabioamaralds">
        <img src="./assets/imagem-fabio.png" width="100px" style="border-radius:50%;" alt="Fabio Amaral"/><br/>
        <b>Fabio Amaral</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/ReginaBolsanelli">
        <img src="./assets/imagem-regina.png" width="100px" style="border-radius:50%;" alt="Regina Bolsanelli"/><br/>
        <b>Regina Bolsanelli</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/tilokao1">
        <img src="./assets/imagem-thiago.png" width="100px" style="border-radius:50%;" alt="Thiago Perez"/><br/>
        <b>Thiago Perez</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/WagnerMartins-on">
        <img src="./assets/imagem-wagner.png" width="100px" style="border-radius:50%;" alt="Wagner Santana"/><br/>
        <b>Wagner Santana</b>
      </a>
    </td>
  </tr>
</table>