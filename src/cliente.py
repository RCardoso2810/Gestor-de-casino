# ══════════════════════════════════════════════════════════════
#  cliente.py
#  CRUD de clientes — dicionarios de dicionarios
#  Estruturas: tuplos, listas, sets, dicionarios, date, defs
# ══════════════════════════════════════════════════════════════

import json
import os
from datetime import date
from utils import (
    validar_nome,
    validar_data_nascimento,
    validar_genero,
    validar_nacionalidade,
    validar_contacto,
    validar_saldo,
    validar_nivel,
    validar_estado,
    validar_casino_existe,
    validar_id_casino,
    gerar_id_filho,
)
from casino import contadores_filhos, carregar_casinos
from logger import get_logger

log = get_logger("cliente")

# Tuplos de valores validos (imutaveis)
GENEROS_VALIDOS = ("M", "F", "OUTRO")
NIVEIS_VALIDOS  = ("BRONZE", "PRATA", "OURO", "PLATINA", "VIP")
ESTADOS_VALIDOS = ("ATIVO", "INATIVO")

# Dicionario principal: { "J0101": { campo: valor, ... } }
base_clientes = {}

# Tuplo dos campos editaveis
CAMPOS_EDITAVEIS_CLIENTE = (
    "nome", "data_nascimento", "genero",
    "nacionalidade", "contacto", "saldo", "nivel", "estado"
)

# Dicionario de despacho de validacao — campo -> funcao
VALIDACOES_CLIENTE = {
    "nome"            : validar_nome,
    "data_nascimento" : validar_data_nascimento,
    "genero"          : validar_genero,
    "nacionalidade"   : validar_nacionalidade,
    "contacto"        : validar_contacto,
    "saldo"           : validar_saldo,
    "nivel"           : validar_nivel,
    "estado"          : validar_estado,
}

FICHEIRO_CLIENTES = "clientes.json"


# ══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ══════════════════════════════════════════════════════════════

def guardar_clientes():
    with open(FICHEIRO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(base_clientes, f, indent=4, ensure_ascii=False)
    log.debug("Clientes guardados em '%s'.", FICHEIRO_CLIENTES)

def carregar_clientes():
    global base_clientes
    if os.path.exists(FICHEIRO_CLIENTES):
        with open(FICHEIRO_CLIENTES, "r", encoding="utf-8") as f:
            base_clientes.clear()
            base_clientes.update(json.load(f))
        log.debug("Clientes carregados: %d registo(s).", len(base_clientes))
    else:
        base_clientes.clear()
        log.debug("Ficheiro '%s' nao encontrado. Base iniciada vazia.", FICHEIRO_CLIENTES)


# ══════════════════════════════════════════════════════════════
#  CREATE — 201 Created
# ══════════════════════════════════════════════════════════════

def criar_cliente(id_casino, nome, data_nasc, genero, nacionalidade,
                  contacto, saldo, nivel, estado="ATIVO"):
    log.info("Criar cliente: nome='%s', id_casino='%s'.", nome, id_casino)
    base_casinos = carregar_casinos()
    carregar_clientes()
    try:
        rv = validar_casino_existe(base_casinos)
        if not rv["valido"]:
            log.error("Sem casinos registados ao criar cliente.")
            return 404, rv["mensagem"]

        rv = validar_id_casino(id_casino, base_casinos)
        if not rv["valido"]:
            log.error("Casino invalido ao criar cliente: '%s'.", id_casino)
            return 404, rv["mensagem"]
        id_cas_ok = rv["valor"]

        rv = validar_nome(nome)
        if not rv["valido"]:
            log.error("Validacao falhou (nome): %s", rv["mensagem"])
            return 422, rv["mensagem"]

        rv = validar_data_nascimento(data_nasc)
        if not rv["valido"]:
            log.error("Validacao falhou (data_nascimento): %s", rv["mensagem"])
            return 422, rv["mensagem"]

        rv = validar_genero(genero)
        if not rv["valido"]:
            log.error("Validacao falhou (genero): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        genero_ok = rv["valor"]

        rv = validar_nacionalidade(nacionalidade)
        if not rv["valido"]:
            log.error("Validacao falhou (nacionalidade): %s", rv["mensagem"])
            return 422, rv["mensagem"]

        rv = validar_contacto(contacto)
        if not rv["valido"]:
            log.error("Validacao falhou (contacto): %s", rv["mensagem"])
            return 422, rv["mensagem"]

        rv = validar_saldo(saldo)
        if not rv["valido"]:
            log.error("Validacao falhou (saldo): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        saldo_ok = rv["valor"]

        rv = validar_nivel(nivel)
        if not rv["valido"]:
            log.error("Validacao falhou (nivel): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        nivel_ok = rv["valor"]

        rv = validar_estado(estado)
        if not rv["valido"]:
            log.error("Validacao falhou (estado): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        estado_ok = rv["valor"]

        id_cliente = gerar_id_filho(id_cas_ok, contadores_filhos, "cliente")

        hoje = date.today()
        cliente = {
            "id"             : id_cliente,
            "id_casino"      : id_cas_ok,
            "nome"           : str(nome).strip(),
            "data_nascimento": str(data_nasc).strip(),
            "genero"         : genero_ok,
            "nacionalidade"  : str(nacionalidade).strip(),
            "contacto"       : str(contacto).strip(),
            "data_registo"   : f"{hoje.day:02d}/{hoje.month:02d}/{hoje.year}",
            "saldo"          : saldo_ok,
            "nivel"          : nivel_ok,
            "estado"         : estado_ok,
        }
        base_clientes[id_cliente] = cliente
        guardar_clientes()
        log.info("Cliente criado com sucesso: id='%s'.", id_cliente)
        return 201, cliente

    except Exception as e:
        log.exception("Erro interno ao criar cliente: %s", e)
        return 500, f"Erro interno: {e}"


# ══════════════════════════════════════════════════════════════
#  READ — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def ler_cliente_por_id(id_cliente):
    carregar_clientes()
    c = base_clientes.get(str(id_cliente).upper())
    if not c:
        log.error("Cliente nao encontrado: id='%s'.", id_cliente)
        return 404, "Cliente nao encontrado."
    log.debug("Cliente lido: id='%s'.", id_cliente)
    return 200, c

def ler_cliente_por_nome(nome):
    carregar_clientes()
    for c in base_clientes.values():
        if c["nome"].lower() == str(nome).strip().lower():
            log.debug("Cliente lido por nome: '%s'.", nome)
            return 200, c
    log.error("Cliente nao encontrado por nome: '%s'.", nome)
    return 404, f"Cliente '{nome}' nao encontrado."

def listar_todos_clientes():
    carregar_clientes()
    lista = list(base_clientes.values())
    log.debug("Listagem de clientes: %d registo(s).", len(lista))
    return 200, lista

def total_clientes():
    carregar_clientes()
    return len(base_clientes)


# ══════════════════════════════════════════════════════════════
#  UPDATE — 200 OK | 404 Not Found | 400/422 erros
# ══════════════════════════════════════════════════════════════

def atualizar_cliente(id_cliente, campo, valor):
    log.info("Atualizar cliente: id='%s', campo='%s'.", id_cliente, campo)
    carregar_clientes()
    c = base_clientes.get(str(id_cliente).upper())
    if not c:
        log.error("Cliente nao encontrado para atualizar: id='%s'.", id_cliente)
        return 404, "Cliente nao encontrado."

    campo = campo.lower().strip()
    if campo not in CAMPOS_EDITAVEIS_CLIENTE:
        log.error("Campo invalido para edicao: '%s'.", campo)
        return 400, f"Campo '{campo}' invalido. Editaveis: {' | '.join(CAMPOS_EDITAVEIS_CLIENTE)}"

    if campo in VALIDACOES_CLIENTE:
        rv = VALIDACOES_CLIENTE[campo](valor)
        if not rv["valido"]:
            log.error("Validacao falhou ao atualizar cliente (%s): %s", campo, rv["mensagem"])
            return 422, rv["mensagem"]
        c[campo] = rv["valor"]
        guardar_clientes()
        log.info("Cliente atualizado: id='%s', campo='%s'.", id_cliente, campo)
        return 200, c

    return 400, f"Campo '{campo}' nao pode ser editado."


# ══════════════════════════════════════════════════════════════
#  DELETE — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def remover_cliente(id_cliente):
    log.info("Remover cliente: id='%s'.", id_cliente)
    carregar_clientes()
    id_upper = str(id_cliente).upper()
    if id_upper not in base_clientes:
        log.error("Cliente nao encontrado para remover: id='%s'.", id_cliente)
        return 404, f"Cliente '{id_cliente}' nao encontrado."
    c = base_clientes.pop(id_upper)
    guardar_clientes()
    log.info("Cliente removido: id='%s'.", id_upper)
    return 200, c
