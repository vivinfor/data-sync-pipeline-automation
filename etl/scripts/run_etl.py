import os
import sys
import logging
from datetime import datetime

# Adicionar o diretório raiz ao PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, BASE_DIR)

# Configuração do ambiente Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django
django.setup()

from etl.utils.logger import setup_logger
from etl.scripts.extract import run_extract
from etl.scripts.transform import run_transform
from etl.scripts.load import run_load

DATA_DIR = os.path.join(BASE_DIR, "etl/data/")
RAW_DIR = os.path.join(DATA_DIR, "raw/")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed/")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive/")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def archive_raw_file(file_path):
    try:
        if os.path.exists(file_path):
            archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(file_path))
            os.rename(file_path, archive_path)
            logging.info(f"Arquivo {file_path} movido para o diretório de arquivo: {archive_path}.")
        else:
            logging.warning(f"Arquivo {file_path} não encontrado para arquivamento.")
    except Exception as e:
        logging.error(f"Erro ao arquivar o arquivo {file_path}: {e}")

def run_etl():
    try:
        logging.info("Iniciando pipeline ETL...")
        today = datetime.now().strftime("%Y-%m-%d")
        raw_csv = os.path.join(RAW_DIR, f"work_items_raw_{today}.csv")
        processed_csv = os.path.join(PROCESSED_DIR, f"work_items_transformed_{today}.csv")
        
        # Extração
        run_extract(output_path=raw_csv)
        if not os.path.exists(raw_csv) or os.path.getsize(raw_csv) == 0:
            logging.warning("Nenhum dado extraído. Interrompendo pipeline ETL.")
            return
        
        # Transformação
        run_transform(input_path=raw_csv, output_path=processed_csv)
        if not os.path.exists(processed_csv) or os.path.getsize(processed_csv) == 0:
            logging.warning("Nenhum dado transformado. Interrompendo pipeline ETL.")
            return

        # Carga
        run_load(file_path=processed_csv)
        
        # Arquivamento
        archive_raw_file(raw_csv)
        logging.info("Pipeline ETL concluído com sucesso.")
    except Exception as e:
        logging.error(f"Erro durante o pipeline ETL: {e}")

if __name__ == "__main__":
    setup_logger(os.path.join(DATA_DIR, "logs/etl.log"))
    run_etl()
