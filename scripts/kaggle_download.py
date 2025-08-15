# scripts/kaggle_download.py
import os
from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path
import shutil

def get_project_root():
    """Encontra a raiz do projeto de forma confiável no Jupyter"""
    # Tenta encontrar pelo caminho de trabalho atual
    current_path = Path.cwd()
    
    # Procura para cima na hierarquia até encontrar o .env
    for parent in [current_path] + list(current_path.parents):
        if (parent / '.env').exists():
            return parent
    
    return current_path  # Fallback

def main():
    # 1. CONFIGURAÇÃO AUTOMÁTICA
    # --------------------------
    project_root = get_project_root()
    print(f"📁 Raiz do projeto identificada: {project_root}")
    
    # Caminhos definitivos
    raw_dir = project_root / 'data' / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. VERIFICAÇÃO DE CREDENCIAIS
    # -----------------------------
    env_path = project_root / '.env'
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado na raiz do projeto")
        print("Crie um arquivo .env com:")
        print("KAGGLE_USERNAME=seu_usuario")
        print("KAGGLE_KEY=sua_chave_api")
        return
    
    # Carrega as credenciais
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    
    # 3. EXECUÇÃO DO DOWNLOAD
    # -----------------------
    temp_dir = project_root / 'temp_kaggle_download'
    temp_dir.mkdir(exist_ok=True)
    
    try:
        api = KaggleApi()
        api.authenticate()
        
        print("⬇️ Baixando dataset...")
        api.dataset_download_files(
            'rodrigoriboldi/incidentes-de-segurana-da-informao-no-brasil',
            path=temp_dir,
            unzip=True
        )
        
        # 4. MOVER ARQUIVO
        # ----------------
        downloaded_files = list(temp_dir.glob('*.csv'))
        if not downloaded_files:
            print("❌ Nenhum arquivo CSV encontrado no download")
            return
            
        final_path = raw_dir / 'incidentes-seguranca-brasil.csv'
        if final_path.exists():
            final_path.unlink()
            
        shutil.move(str(downloaded_files[0]), str(final_path))
        print(f"✅ Arquivo salvo em: {final_path}")
        
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()