from datetime import datetime
import logging

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

