import logging
import os

def setup_logger(log_file, log_level=logging.INFO):
    # Certifique-se de que o diretório do arquivo de log existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Evitar adicionar múltiplos handlers se já existirem
    if len(logging.getLogger().handlers) == 0:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
