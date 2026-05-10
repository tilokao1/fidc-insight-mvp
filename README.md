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
- Observações
- Custo e Prazo

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
- HTML, CSS e JavaScript (Visualização)
- Git e GitHub (Versionamento)

---

## 🔄 Fluxo de Atualização do Projeto

**1. Execução Automatizada:** Na madrugada de todo dia 10, a esteira contendo os 10 scripts Python é acionada de forma automática através do GitHub Actions.  

**2. Coleta e Análise de Dados (CVM):** Durante a execução, os scripts acessam o portal da CVM, fazem as extração dos informes mensais, efetuam a limpeza e salvam no banco de dados. É feito também um processo de webscraping para cada CNPJ dos administradores de FIDCs buscando quantificar o número de processos em que o administrador consta como acusado.  

**3. Cálculo de Métricas e Banco de Dados:** Os scores e métricas são calculados e os dados consolidados atualizam o banco de dados PostgreSQL (hospedado na AWS pelo Supabase).  

**4. Consumo e Visualização no Power BI:** O Power BI se conecta ao banco para consumir as tabelas de métricas e scores, refletindo os resultados atualizados diretamente no dashboard online.  

**5. Interface Interativa via GitHub:** O dashboard no Power BI possui uma tela com o visual de HTML content, que renderiza uma página vinculada ao GitHub Pages. Através dessa integração, o usuário final pode interagir ativamente enviando arquivos e consultando métricas específicas da companhia na própria página.

---

## 📝 Observação

Para a tela de análises internas da empresa, desenvolvemos um arquivo HTML único — com CSS e JavaScript integrados — e o vinculamos ao Power BI por meio do visual HTML Content. Essa abordagem garante que as informações sejam processadas e descartadas imediatamente após a visualização, sem qualquer armazenamento em bancos de dados externos. Dessa forma garantimos a segurança de dados de produtos internos.

---

## 🪙 Custo e Prazo de Desenvolvimento do projeto

Custo Plataforma(Cliente): Power BI Pro(Valor com impostos): R$ 109,56(mensal);  
Custo Recursos Humanos: 60 dias x 4 horas por dia x 5 colaboradores = 1200 horas x R$ 50,00;  
Valor Total: R$ 60.000,00.  
Prazo: 60 Dias.  

---

## 🔜 Próximos Passos

* Realizar mais análises a fim de melhorar o entendimento dos dados das bases de dados CVM e Núclea.
* Utilizar algoritmos de Machine Learning para analise preditiva com previsão de inadimplência.

---

Link para acesso à aplicação: <a href="https://app.powerbi.com/view?r=eyJrIjoiMTMxYjMyMzktNjBhNC00N2ZkLTg0M2YtZDVhMmY5YTdlMDYxIiwidCI6IjY4ZWJmNmZlLTdmNzUtNGNmNS1hNWJmLTAzYWQyNGE3NjRiNCJ9" target="_blank" rel="noopener noreferrer">FIDC Insight</a>

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