import os

RAW_DIR = "data/raw/"
PROCESSED_DIR = "data/processed/"
LOG_DIR = "data/logs/"
ORGANIZATION = os.getenv('AZURE_DEVOPS_ORG')
PROJECT = os.getenv('AZURE_DEVOPS_PROJECT')
PAT = os.getenv('AZURE_DEVOPS_PAT')
