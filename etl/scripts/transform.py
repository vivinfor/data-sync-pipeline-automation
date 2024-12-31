import pandas as pd
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Diretórios para salvar os arquivos
RAW_DIR = "data/raw/"
PROCESSED_DIR = "data/processed/"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Função para converter datas para o formato BR (DD/MM/AAAA)
def format_date_br(date_str):
    try:
        if "." in date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError as e:
        logging.error(f"Erro ao formatar a data {date_str}: {e}")
        return None

# Função para validar as colunas obrigatórias
def validate_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Colunas ausentes no arquivo: {missing_columns}. Transformação abortada.")
        return False
    return True

# Função para transformar e salvar o CSV
def transform_csv(input_path, output_path):
    try:
        # Ler o CSV bruto
        df = pd.read_csv(input_path)
        logging.info(f"Arquivo bruto carregado de {input_path}.")

        # Verificar se as colunas esperadas estão presentes
        required_columns = ["System.CreatedDate", "System.ChangedDate", "System.Title", "System.State"]
        if not validate_columns(df, required_columns):
            return

        # Transformar datas para o formato BR
        df["System.CreatedDate"] = df["System.CreatedDate"].apply(format_date_br)
        df["System.ChangedDate"] = df["System.ChangedDate"].apply(format_date_br)

        # Validar se há valores nulos
        if df.isnull().values.any():
            missing_data = df[df.isnull().any(axis=1)]
            logging.warning(f"Existem valores nulos no arquivo transformado: {missing_data}")

        # Salvar o arquivo transformado
        df.to_csv(output_path, index=False)
        logging.info(f"Arquivo transformado salvo em {output_path}.")
    except Exception as e:
        logging.error(f"Erro ao transformar o arquivo: {e}")

# Função principal para executar a transformação
def run_transform(input_path, output_path):
    try:
        logging.info(f"Iniciando transformação do arquivo {input_path}.")
        transform_csv(input_path, output_path)
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logging.warning(f"O arquivo transformado {output_path} está vazio ou não foi gerado. Transformação interrompida.")
            return
        
        logging.info(f"Transformação concluída. Arquivo salvo em {output_path}.")
    except Exception as e:
        logging.error(f"Erro durante a transformação: {e}")