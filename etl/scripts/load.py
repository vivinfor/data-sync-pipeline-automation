import logging
import pandas as pd
from datetime import datetime
from django.db import transaction
import os
import sys

# Caminho absoluto do diretório raiz do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, BASE_DIR)

# Configuração do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
logging.info("Configurando o Django...")


# Inicializar o Django
import django
django.setup()

logging.info("Django configurado com sucesso!")


# Importações que dependem do Django
from dashboard.models import WorkItem, WorkItemHistory
logging.info("Modelos importados com sucesso!")



# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Diretório dos arquivos processados
PROCESSED_DIR = "etl/data/processed/"

def load_data_to_db(file_path):
    """
    Carrega os dados processados do CSV para as models Django.
    """
    try:
        # Ler o arquivo processado
        df = pd.read_csv(file_path)
        logging.info(f"Arquivo processado carregado de {file_path}.")
        
        # Verificar se as colunas esperadas estão presentes
        expected_columns = ["id", "System.Title", "System.State", "System.CreatedDate", "System.ChangedDate", "System.AssignedTo"]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Colunas ausentes no arquivo: {missing_columns}. Carregamento abortado.")
            return
        
        # Carregar os dados no banco de dados
        with transaction.atomic():
            for _, row in df.iterrows():
                # Verificar se o WorkItem já existe
                work_item, created = WorkItem.objects.update_or_create(
                    external_id=row["id"],
                    defaults={
                        "title": row["System.Title"],
                        "type": infer_work_item_type(row["System.Title"]),
                        "state": row["System.State"],
                        "created_date": parse_date(row["System.CreatedDate"]),
                        "changed_date": parse_date(row["System.ChangedDate"]),
                        "assigned_to": row["System.AssignedTo"] if pd.notna(row["System.AssignedTo"]) else None,
                    },
                )
                
                if created:
                    logging.info(f"Novo WorkItem criado: {work_item}")
                else:
                    logging.info(f"WorkItem atualizado: {work_item}")
                
                # Adicionar histórico
                WorkItemHistory.objects.create(
                    work_item=work_item,
                    state=row["System.State"],
                    changed_date=parse_date(row["System.ChangedDate"]),
                )
                logging.info(f"Histórico atualizado para WorkItem {work_item.external_id}.")
    except Exception as e:
        logging.error(f"Erro ao carregar dados para o banco de dados: {e}")


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            logging.error(f"Erro ao converter data {date_str}: {e}")
            return None



def infer_work_item_type(title):
    """
    Infere o tipo do WorkItem com base no título.
    """
    if "Bug" in title:
        return "Bug"
    elif "Task" in title:
        return "Task"
    elif "User Story" in title:
        return "UserStory"
    return "Task"  # Tipo padrão


def run_load(file_path=None):
    """
    Executa o processo de carregamento.
    """
    try:
        if not file_path:
            # Caminho do arquivo processado mais recente
            today = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join(PROCESSED_DIR, f"work_items_transformed_{today}.csv")
        
        if not os.path.exists(file_path):
            logging.warning(f"Arquivo processado não encontrado: {file_path}")
            return
        
        # Carregar os dados no banco
        load_data_to_db(file_path)
        logging.info("Processo de carregamento concluído com sucesso.")
    except Exception as e:
        logging.error(f"Erro durante o processo de carregamento: {e}")


if __name__ == "__main__":
    logging.info("Iniciando o processo de carregamento...")
    run_load()  # Passa o caminho do arquivo, se necessário
    logging.info("Processo de carregamento finalizado.")
