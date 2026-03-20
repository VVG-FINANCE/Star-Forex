import os

# Definição da estrutura de pastas
folders = [
    'forex_quant_streamlit',
    'forex_quant_streamlit/engine',
    'forex_quant_streamlit/data',
    'forex_quant_streamlit/logs',
    'forex_quant_streamlit/tests'
]

# Definição dos arquivos iniciais
files = {
    'forex_quant_streamlit/engine/__init__.py': '',
    'forex_quant_streamlit/data/.gitkeep': '',
    'forex_quant_streamlit/logs/.gitkeep': '',
    'forex_quant_streamlit/requirements.txt': 'streamlit\nyfinance\npandas\nnumpy\nplotly\nscikit-learn\nscipy',
    'forex_quant_streamlit/config.py': '# Arquivo de Configurações\nclass Config:\n    SYMBOL = "EURUSD=X"\n    PIP_ADJUSTMENT = 0.0001',
    'forex_quant_streamlit/.gitignore': '__pycache__/\n*.pyc\ndata/*.csv\nlogs/*.log\n.env'
}

def create_structure():
    print("🚀 Iniciando criação da arquitetura do sistema...")
    
    # Criar pastas
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Pasta criada: {folder}")
    
    # Criar arquivos
    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Arquivo criado: {file_path}")

    print("\n✨ Estrutura pronta! Agora basta mover os códigos das Partes 1, 2 e 3 para seus respectivos arquivos.")

if __name__ == "__main__":
    create_structure()
