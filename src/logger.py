# ══════════════════════════════════════════════════════════════
#  logger.py
#  Logging centralizado — ficheiro + consola (opcional)
# ══════════════════════════════════════════════════════════════

import logging
import os
from datetime import date

# ── Ficheiro de log com data no nome (ex: casino_2025-05-19.log)
_LOG_DIR  = "logs"
_LOG_FILE = os.path.join(_LOG_DIR, f"casino_{date.today().isoformat()}.log")

os.makedirs(_LOG_DIR, exist_ok=True)

# ── Formato: timestamp | nivel | modulo | mensagem
_FORMATO = "%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s"
_DATA_FMT = "%d/%m/%Y %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=_FORMATO,
    datefmt=_DATA_FMT,
    handlers=[
        logging.FileHandler(_LOG_FILE, encoding="utf-8"),
        # Remove a linha abaixo se nao quiser logs no terminal:
        # logging.StreamHandler(),
    ],
)

def get_logger(nome: str) -> logging.Logger:
    """Devolve um logger com o nome do modulo."""
    return logging.getLogger(nome)
