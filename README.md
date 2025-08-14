\# Projeto: Análise de Incidentes de Segurança da Informação no Brasil 🌐🔐



!\[Data Pipeline](assets/imagem-arquitetura.jpg)



Análise de padrões e tendências de incidentes de segurança da informação no Brasil (2010-2019) usando dados do CERT.br via Kaggle API.



\## 🔧 Ferramentas Utilizadas

\- \*\*Extração\*\*: Kaggle API

\- \*\*Processamento\*\*: Python (Pandas, NumPy)

\- \*\*Armazenamento\*\*: SQLite

\- \*\*Visualização\*\*: Apache Superset + Seaborn



\## 📂 Estrutura do Repositório

```

.

├── data/

│ ├── raw/incidentes-seguranca-brasil.csv # Dados baixados via API

│ └── processed/cleaned\_incidents.csv # Dados tratados

├── database/

│ └── brazil\_incidents.db # Banco SQLite

├── notebooks/

│ └── security\_analysis.ipynb # Análise exploratória

├── scripts/

│ ├── kaggle\_download.py # Download via API

│ ├── etl.py # Pipeline de processamento

│ └── superset\_config/

│ ├── dashboard\_export.json # Config do dashboard

│ └── import\_dashboard.py # Script de import

├── visualizations/

│ ├── dashboards/

│ │ └── security\_dashboard.json # Template Superset

│ └── plots/ # Imagens geradas

├── requirements.txt

├── .env # Armazena API key

└── README.md

```



\## 🌲 Estrutura do Pipeline

```mermaid

graph TD

&nbsp;   A\[Kaggle] -->|Extrair| B\[data/raw/cert\_2010-2019.csv]

&nbsp;   B -->|Transformar| C\[data/processed/cleaned\_incidents.csv]

&nbsp;   C -->|Carregar| D\[database/brazil\_incidents.db]

&nbsp;   D -->|Visualizar| E\[Apache Superset]

&nbsp;   E --> F\[📈 Evolução Anual]

&nbsp;   E --> G\[📊 Tipos de Ataque]

&nbsp;   E --> H\[🌐 Sazonalidade]

```





\## ⚙️ Pré-requisitos

1\. Conta no \[Kaggle](https://www.kaggle.com/)

2\. Obter API Key (Settings → Create New API Token)

3\. Python 3.10+



\## 🚀 Execução do Projeto



\### 1. Configurar ambiente

```bash

\# Cria o ambiente virtual

python -m venv venv



\# Ativa o venv (Linux/Mac)

source venv/bin/activate



\# Ou no Windows:

.\\venv\\Scripts\\activate



pip install -r requirements.txt --ignore-installed --no-deps --no-build-isolation --force-reinstall



\# Confirme as libs baixadas

pip list



```

\## 2. 2. Configurar API do Kaggle



```bash

\# Crie um arquivo .env na raiz do projeto com:

KAGGLE\_USERNAME=seu\_usuario

KAGGLE\_KEY=sua\_api\_key

```



\## 2. Baixar dados do Kaggle



```bash

python scripts/kaggle\_download.py

```



\## 3. Processar dados



```bash

python scripts/etl.py

```



\## 4. Visualização (Apache Superset)



```bash

superset run -p 8080



\# Acesse: http://localhost:8088

```



\## 📊 Principais Visualizações



\*\*Visualização 1\*\*  

!\[Visualização 1](https://miro.medium.com/max/480/1\*H7e2BY1C1M8UZMu3J0x-lQ.png)



\*\*Visualização 2\*\*  

!\[Visualização 2](https://matplotlib.org/stable/\_images/sphx\_glr\_scatter\_001.png)



\*\*Visualização 3\*\*  

!\[Visualização 3](https://pandas.pydata.org/pandas-docs/stable/\_images/boxplot\_ex1.png)



\## 🔍 Principais Insights



\### 1. Tendência Anual de Incidentes

!\[Tendência Anual](https://visualizations/plots/annual\_trend.png)  



\- \*\*Crescimento de 530%\*\* entre 2010-2019  

\- \*\*Pico histórico em 2017\*\* (Julho: 257.618 incidentes)  



---



\### 2. Tipos de Ataque Dominantes

```python

\# Código para análise:

df.groupby('Ano')\[\['Scan', 'DOS', 'Worm']].sum().plot(kind='bar')

```



| Tipo de Ataque | Percentual | Evolução Histórica         |

|----------------|------------|----------------------------|

| \*\*Scan\*\*       | 58%        | Técnica mais comum         |

| \*\*DOS\*\*        | 23%        | Cresceu 400x desde 2013    |

| \*\*Fraude\*\*     | -          | Aumento de 1200% na década |



---



\### 3. Padrões Mensais

!\[Padrões Mensais](https://visualizations/plots/monthly\_patterns.png)  



\- \*\*Meses críticos\*\*: Junho-Novembro  

\- \*\*Período mais seguro\*\*: Janeiro (-30% vs média)  



---



\### 4. Mudanças na Natureza dos Ataques

\*\*2012-2015\*\*:  

\- Dominância de Scans  



\*\*2016-2019\*\*:  

\- Explosão de ataques DOS  

\- Surgimento de novas ameaças (Web, Fraude)  



