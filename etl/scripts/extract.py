import os
import logging
import time
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
import requests
import csv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da API do Azure DevOps
organization = os.getenv('AZURE_DEVOPS_ORG')
project = os.getenv('AZURE_DEVOPS_PROJECT')
pat = os.getenv('AZURE_DEVOPS_PAT')

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Diretório para salvar checkpoints
CHECKPOINT_FILE = "etl/checkpoints/last_extracted.json"
os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)

# Cabeçalhos da requisição
HEADERS = {'Content-Type': 'application/json'}

def save_checkpoint(last_id):
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({"last_id": last_id}, f)
    except Exception as e:
        logging.error(f"Erro ao salvar checkpoint: {e}")

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                data = json.load(f)
                return data.get("last_id", 0)
        except Exception as e:
            logging.warning(f"Erro ao carregar checkpoint: {e}")
    return 0

def handle_rate_limiting(response):
    if response.status_code == 429:  # Too Many Requests
        retry_after = int(response.headers.get("Retry-After", 5))
        logging.warning(f"Limite de requisições atingido. Esperando {retry_after} segundos.")
        time.sleep(retry_after)
        return True
    return False

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def extract_work_item_ids():
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id] FROM workitems"}

    response = requests.post(url, json=query, headers=HEADERS, auth=HTTPBasicAuth('', pat), timeout=10)
    if handle_rate_limiting(response):
        return extract_work_item_ids()
    if response.status_code == 200:
        data = response.json()
        return [item['id'] for item in data.get('workItems', [])]
    else:
        response.raise_for_status()

def extract_work_items(work_item_ids, start_index=0):
    work_items = []
    for i in range(start_index, len(work_item_ids)):
        work_item_id = work_item_ids[i]
        url = (f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{work_item_id}"
               f"?api-version=6.0&fields=System.Title,System.State,System.CreatedDate,"
               f"System.ChangedDate,System.AssignedTo")
        try:
            response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth('', pat), timeout=10)
            if handle_rate_limiting(response):
                continue
            if response.status_code == 200:
                work_item = response.json()
                logging.info(f"Detalhes do Work Item {work_item_id} extraídos com sucesso.")
                work_items.append(work_item)
                save_checkpoint(work_item_id)  # Atualizar o checkpoint
            else:
                logging.error(f"Erro ao extrair Work Item {work_item_id}. Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Erro ao processar Work Item {work_item_id}: {e}")
            time.sleep(5)  # Pausa antes de tentar o próximo item
    return work_items

def transform_and_save_to_csv(work_items, output_path):
    if not work_items:
        logging.warning("Nenhum Work Item para salvar.")
        return

    keys = ["id", "System.Title", "System.State", "System.CreatedDate", 
            "System.ChangedDate", "System.AssignedTo"]

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            for item in work_items:
                row = {}
                row["id"] = item.get("id", "")
                fields = item.get("fields", {})
                row["System.Title"] = fields.get("System.Title", "")
                row["System.State"] = fields.get("System.State", "")
                row["System.CreatedDate"] = fields.get("System.CreatedDate", "")
                row["System.ChangedDate"] = fields.get("System.ChangedDate", "")
                row["System.AssignedTo"] = fields.get("System.AssignedTo", {}).get("displayName", "")
                
                # Verifique se os dados estão completos
                if any(row.values()):
                    dict_writer.writerow(row)
                else:
                    logging.warning(f"Work Item com campos ausentes ou inválidos: {row}")
        
        logging.info(f"Dados salvos com sucesso em {output_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar CSV: {e}")


# Função para execução da extração
def run_extract(output_path):
    try:
        logging.info("Iniciando extração dos Work Items...")
        work_item_ids = extract_work_item_ids()
        if not work_item_ids:
            logging.warning("Nenhum ID de Work Item encontrado. Processo finalizado.")
            return

        work_items = extract_work_items(work_item_ids)
        if not work_items:
            logging.warning("Nenhum dado extraído. Nenhum Work Item processado.")
            return

        logging.info(f"Salvando {len(work_items)} Work Items no arquivo CSV.")
        transform_and_save_to_csv(work_items, output_path)
        
        # Verificar se o arquivo foi realmente gerado
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logging.info(f"Arquivo de saída gerado com sucesso: {output_path}")
        else:
            logging.warning("Arquivo de saída não gerado ou vazio após a extração.")
    except RetryError as re:
        logging.error("Erro persistente ao tentar acessar a API: %s", re)
    except Exception as e:
        logging.error("Erro inesperado na extração: %s", e)

