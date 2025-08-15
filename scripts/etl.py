import pandas as pd
import sqlalchemy
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# 1. CONFIGURAÇÃO INICIAL ======================================================

def get_project_root():
    """Retorna o caminho absoluto para a raiz do projeto de forma confiável"""
    try:
        return Path(__file__).resolve().parent.parent
    except NameError:
        current_path = Path.cwd()
        while current_path != current_path.parent:
            if (current_path / '.env').exists() or (current_path / 'README.md').exists():
                return current_path
            current_path = current_path.parent
        return Path.cwd()

def log_transformation(description):
    """Registra transformações aplicadas"""
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {description}")

# Configurações de caminhos
PROJECT_ROOT = get_project_root()
RAW_DATA = PROJECT_ROOT / 'data' / 'raw' / 'incidentes-seguranca-brasil.csv'
PROCESSED_DATA = PROJECT_ROOT / 'data' / 'processed' / 'cleaned_incidents.csv'
DB_PATH = PROJECT_ROOT / 'database' / 'brazil_incidents.db'
VIZ_DIR = PROJECT_ROOT / 'visualizations' / 'plots'

# 2. FUNÇÕES AUXILIARES =======================================================

def detect_attack_columns(df):
    """Detecta automaticamente colunas de tipos de ataque"""
    potential_attacks = ['Worm', 'DOS', 'Invasao', 'Web', 'Scan', 'Fraude', 'Outros']
    return [col for col in potential_attacks if col in df.columns]

def data_quality_check(df, attack_cols):
    """Verifica qualidade dos dados após transformação"""
    checks = {
        "Valores nulos no Total": df['Total'].isnull().sum(),
        "Anos fora do intervalo 2010-2019": ~df['Ano'].between(2010, 2019).sum(),
        "Valores negativos em ataques": (df[attack_cols] < 0).sum().sum()
    }
    
    for desc, count in checks.items():
        status = "OK" if count == 0 else "ALERTA"
        log_transformation(f"{status}: {desc}: {count} ocorrências")

# 3. FUNÇÃO DE TRANSFORMAÇÃO ==================================================

def transform_data(df):
    """Executa todas as transformações nos dados"""
    log_transformation("Iniciando transformação de dados...")
    
    # Detectar colunas de ataque automaticamente
    attack_cols = detect_attack_columns(df)
    if not attack_cols:
        raise ValueError("Não foram encontradas colunas de tipos de ataque no dataset")
    
    log_transformation(f"Colunas de ataque detectadas: {', '.join(attack_cols)}")
    
    # Mapeamento de meses
    meses_map = {
        'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
        'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
        'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
    }
    
    # Transformações básicas
    df['Mes_num'] = df['Mes'].map(meses_map)
    df['Data'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mes_num'].astype(str))
    
    # Converter colunas numéricas
    numeric_cols = ['Total'] + attack_cols
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', ''), errors='coerce')
    
    # Preencher NAs
    df[attack_cols] = df[attack_cols].fillna(0)
    
    # Transformações avançadas
    df['Crescimento_Anual'] = df.groupby('Mes_num')['Total'].pct_change() * 100
    
    bins = [0, df['Total'].quantile(0.5), df['Total'].quantile(0.9), df['Total'].max()]
    df['Severidade'] = pd.cut(df['Total'], bins=bins, labels=['Baixo', 'Médio', 'Alto'])
    
    # Detecção de outliers
    Q1 = df[attack_cols].quantile(0.25)
    Q3 = df[attack_cols].quantile(0.75)
    IQR = Q3 - Q1
    df['Outlier'] = ((df[attack_cols] < (Q1 - 1.5 * IQR)) | (df[attack_cols] > (Q3 + 1.5 * IQR))).any(axis=1)
    
    # Agregações temporais
    df['Trimestre'] = df['Mes_num'].apply(lambda m: (m-1)//3 + 1)
    df['Semestre'] = df['Mes_num'].apply(lambda m: 1 if m <=6 else 2)
    
    # Normalização
    df['Total_Norm'] = df.groupby('Mes_num')['Total'].transform(lambda x: (x - x.mean()) / x.std())
    
    # Clusterização
    if len(attack_cols) >= 3:  # Requer pelo menos 3 features para clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['Cluster'] = kmeans.fit_predict(df[attack_cols])
    
    data_quality_check(df, attack_cols)
    return df, attack_cols

# 4. GERAÇÃO DE VISUALIZAÇÕES =================================================

def generate_insights(df, attack_cols):
    """Gera visualizações e insights principais"""
    os.makedirs(VIZ_DIR, exist_ok=True)
    plt.close('all')
    
    # Evolução anual
    plt.figure(figsize=(12, 6))
    df.groupby('Ano')['Total'].sum().plot(kind='bar', color='darkred')
    plt.title('Evolução Anual de Incidentes (2010-2019)')
    plt.ylabel('Total de Incidentes')
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'annual_trend.png', bbox_inches='tight')
    plt.close()
    
    # Proporção de tipos de ataque
    attack_totals = df[attack_cols].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 8))
    attack_totals.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Distribuição de Tipos de Ataque (2010-2019)')
    plt.ylabel('')
    plt.savefig(VIZ_DIR / 'attack_distribution.png', bbox_inches='tight')
    plt.close()
    
    # Heatmap de correlação
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[attack_cols].corr(), annot=True, cmap='coolwarm', center=0)
    plt.title('Correlação entre Tipos de Ataque')
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'attack_correlation.png', bbox_inches='tight')
    plt.close()

# 5. FLUXO PRINCIPAL ==========================================================

def main():
    try:
        # Configuração inicial
        os.makedirs(PROCESSED_DATA.parent, exist_ok=True)
        os.makedirs(DB_PATH.parent, exist_ok=True)
        
        # Extração
        log_transformation(f"Carregando dados de: {RAW_DATA}")
        df = pd.read_csv(RAW_DATA, sep=';', encoding='utf-8', thousands='.', decimal=',')
        
        # Transformação
        df, attack_cols = transform_data(df)
        
        # Visualização
        generate_insights(df, attack_cols)
        
        # Carregamento
        df.to_csv(PROCESSED_DATA, index=False)
        engine = sqlalchemy.create_engine(f'sqlite:///{DB_PATH}')
        df.to_sql('incidentes', engine, if_exists='replace', index=False)
        
        log_transformation(f"Dados processados salvos em: {PROCESSED_DATA}")
        log_transformation(f"Banco de dados atualizado em: {DB_PATH}")
        log_transformation("Processo ETL concluído com sucesso!")
        
    except Exception as e:
        log_transformation(f"ERRO: {str(e)}")
        raise

if __name__ == "__main__":
    main()