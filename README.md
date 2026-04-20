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

### PowerPoint
Contém as apresentações dos respectivos sprints(.pptx) entregues em cada etapa  acadêmica do projeto.

---

### README.md
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
- GitHub (Versionamento)

---

## 🔄 Fluxo de Atualização do Projeto

1. Dados são coletados e tratados via Python
2. Banco PostgreSQL é atualizado no AWS através do Supabase
3. Scores e métricas são calculados
4. Power BI consome os dados para visualização
5. PPT é atualizado com os resultados e entregas.

---

## 👥 Equipe

Projeto desenvolvido pela equipe Data Insight.

<p align="center">
  <a href="https://github.com/DanielaPSilva" target="_blank">
    <img src="./assets/imagem-daniela.png" width="120" height="120" style="border-radius: 50%; display: inline-block;">
  </a>
  <a href="https://github.com/fabioamaralds" target="_blank">
    <img src="./assets/imagem-fabio.png" width="120" height="120" style="border-radius: 50%; display: inline-block;">
  </a>
  <a href="https://github.com/ReginaBolsanelli" target="_blank">
    <img src="./assets/imagem-regina.png" width="120" height="120" style="border-radius: 50%; display: inline-block;">
  </a>
  <a href="https://github.com/tilokao1" target="_blank">
    <img src="./assets/imagem-thiago.png" width="120" height="120" style="border-radius: 50%; display: inline-block;">
  </a>
  <a href="https://github.com/WagnerMartins-on" target="_blank">
    <img src="./assets/imagem-wagner.png" width="120" height="120" style="border-radius: 50%; display: inline-block;">
  </a>
</p>
<p align="center">
  <sub><b>Daniela Silva</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Fabio Amaral</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Regina Bolsanelli</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Thiago Perez</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Wagner Santana</b></sub>
</p>
