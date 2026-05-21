# ══════════════════════════════════════════════════════════════
#  jogo.py
#  CRUD de jogos — dicionarios de dicionarios
#  Estruturas: tuplos, listas, sets, dicionarios, date, defs
# ══════════════════════════════════════════════════════════════

import json
import os
from datetime import date
from utils import (
    validar_nome_jogo,
    validar_custo_minimo,
    validar_saldo_jogo,
    validar_retorno,
    validar_nivel,
    validar_estado,
    validar_sim_nao,
    validar_casino_existe,
    validar_id_casino,
    gerar_id_filho,
)
from casino import  contadores_filhos, carregar_casinos
from logger import get_logger

log = get_logger("jogo")

# Tuplos de valores validos (imutaveis)
ESTADOS_JOGO = ("ATIVO", "INATIVO")
NIVEIS_JOGO  = ("BRONZE", "PRATA", "OURO", "PLATINA", "VIP")

# Dicionario principal: { "J0101": { campo: valor, ... } }
base_jogos = {}

# Set dos campos que sao tipos (sub-dicionario "tipos")
CAMPOS_TIPOS = {"dealer", "tabuleiro", "pecas", "cartas", "dados", "maquina"}

# Tuplo dos campos editaveis
CAMPOS_EDITAVEIS_JOGO = (
    "nome", "custo_minimo", "saldo_jogo", "retorno",
    "nivel_acesso", "estado",
    "dealer", "tabuleiro", "pecas", "cartas", "dados", "maquina"
)

# Dicionarios de despacho de validacao — campo -> funcao
VALIDACOES_JOGO = {
    "nome"         : validar_nome_jogo,
    "custo_minimo" : validar_custo_minimo,
    "saldo_jogo"   : validar_saldo_jogo,
    "retorno"      : validar_retorno,
    "nivel_acesso" : lambda v: validar_nivel(v, "Nivel de acesso"),
    "estado"       : validar_estado,
}

VALIDACOES_TIPOS_JOGO = {
    "dealer"    : lambda v: validar_sim_nao(v, "dealer"),
    "tabuleiro" : lambda v: validar_sim_nao(v, "tabuleiro"),
    "pecas"     : lambda v: validar_sim_nao(v, "pecas"),
    "cartas"    : lambda v: validar_sim_nao(v, "cartas"),
    "dados"     : lambda v: validar_sim_nao(v, "dados"),
    "maquina"   : lambda v: validar_sim_nao(v, "maquina"),
}

FICHEIRO_JOGOS = "jogos.json"


# ══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ══════════════════════════════════════════════════════════════

def guardar_jogos():
    with open(FICHEIRO_JOGOS, "w", encoding="utf-8") as f:
        json.dump(base_jogos, f, indent=4, ensure_ascii=False)
    log.debug("Jogos guardados em '%s'.", FICHEIRO_JOGOS)

def carregar_jogos():
    global base_jogos
    if os.path.exists(FICHEIRO_JOGOS):
        with open(FICHEIRO_JOGOS, "r", encoding="utf-8") as f:
            base_jogos.clear()
            base_jogos.update(json.load(f))
        log.debug("Jogos carregados: %d registo(s).", len(base_jogos))
    else:
        base_jogos.clear()
        log.debug("Ficheiro '%s' nao encontrado. Base iniciada vazia.", FICHEIRO_JOGOS)


# ══════════════════════════════════════════════════════════════
#  CREATE — 201 Created
# ══════════════════════════════════════════════════════════════

def criar_jogo(id_casino, nome, custo_minimo, saldo_jogo, retorno,
               nivel_acesso, estado,
               tem_dealer, tem_tabuleiro, tem_pecas,
               tem_cartas, tem_dados, tem_maquina):
    log.info("Criar jogo: nome='%s', id_casino='%s'.", nome, id_casino)
    base_casinos = carregar_casinos()
    carregar_jogos()
    try:
        rv = validar_casino_existe(base_casinos)
        if not rv["valido"]:
            log.error("Sem casinos registados ao criar jogo.")
            return 404, rv["mensagem"]

        rv = validar_id_casino(id_casino, base_casinos)
        if not rv["valido"]:
            log.error("Casino invalido ao criar jogo: '%s'.", id_casino)
            return 404, rv["mensagem"]
        id_cas_ok = rv["valor"]

        rv = validar_nome_jogo(nome)
        if not rv["valido"]:
            log.error("Validacao falhou (nome_jogo): %s", rv["mensagem"])
            return 422, rv["mensagem"]

        rv = validar_custo_minimo(custo_minimo)
        if not rv["valido"]:
            log.error("Validacao falhou (custo_minimo): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        custo_ok = rv["valor"]

        rv = validar_saldo_jogo(saldo_jogo)
        if not rv["valido"]:
            log.error("Validacao falhou (saldo_jogo): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        saldo_ok = rv["valor"]

        rv = validar_retorno(retorno)
        if not rv["valido"]:
            log.error("Validacao falhou (retorno): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        retorno_ok = rv["valor"]

        rv = validar_nivel(nivel_acesso, "Nivel de acesso")
        if not rv["valido"]:
            log.error("Validacao falhou (nivel_acesso): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        nivel_ok = rv["valor"]

        rv = validar_estado(estado)
        if not rv["valido"]:
            log.error("Validacao falhou (estado): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        estado_ok = rv["valor"]

        entradas_tipos = (
            ("dealer",    tem_dealer),
            ("tabuleiro", tem_tabuleiro),
            ("pecas",     tem_pecas),
            ("cartas",    tem_cartas),
            ("dados",     tem_dados),
            ("maquina",   tem_maquina),
        )
        tipos = {}
        for campo_t, valor_t in entradas_tipos:
            rv = VALIDACOES_TIPOS_JOGO[campo_t](valor_t)
            if not rv["valido"]:
                log.error("Validacao falhou (tipo '%s'): %s", campo_t, rv["mensagem"])
                return 422, rv["mensagem"]
            tipos[campo_t] = rv["valor"]

        id_jogo = gerar_id_filho(id_cas_ok, contadores_filhos, "jogo")

        hoje = date.today()
        jogo = {
            "id"           : id_jogo,
            "id_casino"    : id_cas_ok,
            "nome"         : str(nome).strip(),
            "custo_minimo" : custo_ok,
            "saldo_jogo"   : saldo_ok,
            "retorno"      : retorno_ok,
            "nivel_acesso" : nivel_ok,
            "estado"       : estado_ok,
            "data_criacao" : f"{hoje.day:02d}/{hoje.month:02d}/{hoje.year}",
            "tipos"        : tipos,
        }
        base_jogos[id_jogo] = jogo
        guardar_jogos()
        log.info("Jogo criado com sucesso: id='%s'.", id_jogo)
        return 201, jogo

    except Exception as e:
        log.exception("Erro interno ao criar jogo: %s", e)
        return 500, f"Erro interno: {e}"


# ══════════════════════════════════════════════════════════════
#  READ — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def ler_jogo_por_id(id_jogo):
    carregar_jogos()
    j = base_jogos.get(str(id_jogo).upper())
    if not j:
        log.error("Jogo nao encontrado: id='%s'.", id_jogo)
        return 404, "Jogo nao encontrado."
    log.debug("Jogo lido: id='%s'.", id_jogo)
    return 200, j

def ler_jogo_por_nome(nome):
    carregar_jogos()
    for j in base_jogos.values():
        if j["nome"].lower() == str(nome).strip().lower():
            log.debug("Jogo lido por nome: '%s'.", nome)
            return 200, j
    log.error("Jogo nao encontrado por nome: '%s'.", nome)
    return 404, f"Jogo '{nome}' nao encontrado."

def listar_todos_jogos():
    carregar_jogos()
    lista = list(base_jogos.values())
    log.debug("Listagem de jogos: %d registo(s).", len(lista))
    return 200, lista

def listar_jogos_ativos():
    carregar_jogos()
    lista = [j for j in base_jogos.values() if j["estado"] == "ATIVO"]
    log.debug("Jogos ativos: %d registo(s).", len(lista))
    return 200, lista

def total_jogos():
    carregar_jogos()
    return len(base_jogos)


# ══════════════════════════════════════════════════════════════
#  UPDATE — 200 OK | 404 Not Found | 400/422 erros
# ══════════════════════════════════════════════════════════════

def atualizar_jogo(id_jogo, campo, valor):
    log.info("Atualizar jogo: id='%s', campo='%s'.", id_jogo, campo)
    carregar_jogos()
    j = base_jogos.get(str(id_jogo).upper())
    if not j:
        log.error("Jogo nao encontrado para atualizar: id='%s'.", id_jogo)
        return 404, f"Jogo '{id_jogo}' nao encontrado."

    campo = campo.lower().strip()
    if campo not in CAMPOS_EDITAVEIS_JOGO:
        log.error("Campo invalido para edicao: '%s'.", campo)
        return 400, f"Campo '{campo}' invalido. Editaveis: {' | '.join(CAMPOS_EDITAVEIS_JOGO)}"

    if campo in VALIDACOES_JOGO:
        rv = VALIDACOES_JOGO[campo](valor)
        if not rv["valido"]:
            log.error("Validacao falhou ao atualizar jogo (%s): %s", campo, rv["mensagem"])
            return 422, rv["mensagem"]
        j[campo] = rv["valor"]
        guardar_jogos()
        log.info("Jogo atualizado: id='%s', campo='%s'.", id_jogo, campo)
        return 200, j

    if campo in CAMPOS_TIPOS:
        rv = VALIDACOES_TIPOS_JOGO[campo](valor)
        if not rv["valido"]:
            log.error("Validacao falhou ao atualizar tipo de jogo (%s): %s", campo, rv["mensagem"])
            return 422, rv["mensagem"]
        j["tipos"][campo] = rv["valor"]
        guardar_jogos()
        log.info("Tipo de jogo atualizado: id='%s', campo='%s'.", id_jogo, campo)
        return 200, j

    return 400, f"Campo '{campo}' nao pode ser editado."


# ══════════════════════════════════════════════════════════════
#  DELETE — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def remover_jogo(id_jogo):
    log.info("Remover jogo: id='%s'.", id_jogo)
    carregar_jogos()
    id_upper = str(id_jogo).upper()
    if id_upper not in base_jogos:
        log.error("Jogo nao encontrado para remover: id='%s'.", id_jogo)
        return 404, f"Jogo '{id_jogo}' nao encontrado."
    j = base_jogos.pop(id_upper)
    guardar_jogos()
    log.info("Jogo removido: id='%s'.", id_upper)
    return 200, j
