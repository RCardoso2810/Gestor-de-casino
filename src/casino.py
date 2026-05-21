# ══════════════════════════════════════════════════════════════
#  casino.py
#  CRUD de casinos — dicionarios de dicionarios
#  Estruturas: tuplos, listas, sets, dicionarios, date, defs
# ══════════════════════════════════════════════════════════════

import json
import os
from utils import (
    validar_nome,
    validar_localizacao,
    validar_taxa,
    validar_moeda,
    validar_capacidade,
    gerar_id_casino,
    MOEDAS_VALIDAS,
)
from logger import get_logger

log = get_logger("casino")

# ── Dicionario principal: { "J01": { campo: valor, ... } }
base_casinos = {}

# ── Dicionario auxiliar de contadores por casino — { "J01_cliente": 2, ... }
contadores_filhos = {}

# ── Tuplo dos campos editaveis
CAMPOS_EDITAVEIS_CASINO = (
    "nome", "localizacao", "taxa", "moeda", "capacidade_maxima"
)

# ── Dicionario de despacho de validacao — campo -> funcao
VALIDACOES_CASINO = {
    "nome"             : validar_nome,
    "localizacao"      : validar_localizacao,
    "taxa"             : validar_taxa,
    "moeda"            : validar_moeda,
    "capacidade_maxima": validar_capacidade,
}

FICHEIRO_CASINOS = "casinos.json"


# ══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ══════════════════════════════════════════════════════════════

def guardar_casinos():
    with open(FICHEIRO_CASINOS, "w", encoding="utf-8") as f:
        json.dump({"base_casinos": base_casinos, "contadores_filhos": contadores_filhos}, f, indent=4, ensure_ascii=False)
    log.debug("Casinos guardados em '%s'.", FICHEIRO_CASINOS)

def carregar_casinos():
    global base_casinos, contadores_filhos
    if os.path.exists(FICHEIRO_CASINOS):
        with open(FICHEIRO_CASINOS, "r", encoding="utf-8") as f:
            dados = json.load(f)
        base_casinos.clear()
        base_casinos.update(dados.get("base_casinos", {}))
        contadores_filhos.clear()
        contadores_filhos.update(dados.get("contadores_filhos", {}))
        log.debug("Casinos carregados: %d registo(s).", len(base_casinos))
    else:
        base_casinos.clear()
        contadores_filhos.clear()
        log.debug("Ficheiro '%s' nao encontrado. Base iniciada vazia.", FICHEIRO_CASINOS)
    return base_casinos


# ══════════════════════════════════════════════════════════════
#  CREATE — 201 Created
# ══════════════════════════════════════════════════════════════

def criar_casino(nome, localizacao, taxa, moeda, capacidade_maxima):
    log.info("Criar casino: nome='%s', localizacao='%s'.", nome, localizacao)
    carregar_casinos()
    try:
        rv = validar_nome(nome)
        if not rv["valido"]:
            log.error("Validacao falhou (nome): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        nome_ok = rv["valor"]

        rv = validar_localizacao(localizacao)
        if not rv["valido"]:
            log.error("Validacao falhou (localizacao): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        loc_ok = rv["valor"]

        rv = validar_taxa(taxa)
        if not rv["valido"]:
            log.error("Validacao falhou (taxa): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        taxa_ok = rv["valor"]

        rv = validar_moeda(moeda)
        if not rv["valido"]:
            log.error("Validacao falhou (moeda): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        moeda_ok = rv["valor"]

        rv = validar_capacidade(capacidade_maxima)
        if not rv["valido"]:
            log.error("Validacao falhou (capacidade_maxima): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        cap_ok = rv["valor"]

        id_casino = gerar_id_casino(nome_ok)

        casino = {
            "id"               : id_casino,
            "nome"             : nome_ok,
            "localizacao"      : loc_ok,
            "taxa"             : taxa_ok,
            "moeda"            : moeda_ok,
            "capacidade_maxima": cap_ok,
            "total_clientes"   : 0,
            "total_jogos"      : 0,
            "ids_clientes"     : [],
            "ids_jogos"        : [],
        }
        base_casinos[id_casino] = casino
        guardar_casinos()
        log.info("Casino criado com sucesso: id='%s'.", id_casino)
        return 201, casino

    except Exception as e:
        log.exception("Erro interno ao criar casino: %s", e)
        return 500, f"Erro interno: {e}"


# ══════════════════════════════════════════════════════════════
#  READ — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def ler_casino_por_id(id_casino):
    carregar_casinos()
    c = base_casinos.get(str(id_casino).strip().upper())
    if not c:
        log.error("Casino nao encontrado: id='%s'.", id_casino)
        return 404, "Casino nao encontrado."
    log.debug("Casino lido: id='%s'.", id_casino)
    return 200, c

def ler_casino_por_nome(nome):
    carregar_casinos()
    for c in base_casinos.values():
        if c["nome"].lower() == str(nome).strip().lower():
            log.debug("Casino lido por nome: '%s'.", nome)
            return 200, c
    log.error("Casino nao encontrado por nome: '%s'.", nome)
    return 404, f"Casino '{nome}' nao encontrado."

def listar_todos_casinos():
    carregar_casinos()
    lista = list(base_casinos.values())
    log.debug("Listagem de casinos: %d registo(s).", len(lista))
    return 200, lista

def total_casinos():
    carregar_casinos()
    return len(base_casinos)

def listar_casinos_disponiveis():
    carregar_casinos()
    return [(c["id"], c["nome"]) for c in base_casinos.values()]


# ══════════════════════════════════════════════════════════════
#  UPDATE — 200 OK | 404 Not Found | 400/422 erros
# ══════════════════════════════════════════════════════════════

def atualizar_casino(id_casino, campo, valor):
    log.info("Atualizar casino: id='%s', campo='%s'.", id_casino, campo)
    carregar_casinos()
    c = base_casinos.get(str(id_casino).strip().upper())
    if not c:
        log.error("Casino nao encontrado para atualizar: id='%s'.", id_casino)
        return 404, "Casino nao encontrado."

    campo = campo.lower().strip()
    if campo not in CAMPOS_EDITAVEIS_CASINO:
        log.error("Campo invalido para edicao: '%s'.", campo)
        return 400, f"Campo '{campo}' invalido. Editaveis: {' | '.join(CAMPOS_EDITAVEIS_CASINO)}"

    if campo in VALIDACOES_CASINO:
        rv = VALIDACOES_CASINO[campo](valor)
        if not rv["valido"]:
            log.error("Validacao falhou ao atualizar casino (%s): %s", campo, rv["mensagem"])
            return 422, rv["mensagem"]
        c[campo] = rv["valor"]
        guardar_casinos()
        log.info("Casino atualizado: id='%s', campo='%s'.", id_casino, campo)
        return 200, c

    return 400, f"Campo '{campo}' nao pode ser editado."


# ══════════════════════════════════════════════════════════════
#  DELETE — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def remover_casino(id_casino):
    log.info("Remover casino: id='%s'.", id_casino)
    carregar_casinos()
    id_upper = str(id_casino).strip().upper()
    if id_upper not in base_casinos:
        log.error("Casino nao encontrado para remover: id='%s'.", id_casino)
        return 404, f"Casino '{id_casino}' nao encontrado."
    c = base_casinos.pop(id_upper)
    guardar_casinos()
    log.info("Casino removido: id='%s'.", id_upper)
    return 200, c
