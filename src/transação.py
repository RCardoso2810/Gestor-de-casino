# ══════════════════════════════════════════════════════════════
#  transacao.py
#  CRUD de transacoes — dicionarios de dicionarios
#  Estruturas: tuplos, listas, sets, dicionarios, date, defs
# ══════════════════════════════════════════════════════════════

import json
import os
from datetime import datetime
from utils import (
    validar_id_cliente,
    validar_tipo_transacao,
    validar_tipo_movimento,
    validar_montante,
    validar_metodo_pagamento,
    validar_estado_transacao,
    TIPOS_TRANSACAO_VALIDOS,
    TIPOS_MOVIMENTO_VALIDOS,
    METODOS_PAGAMENTO_VALIDOS,
    ESTADOS_TRANSACAO_VALIDOS,
    validar_base_para_guardar,
    validar_ficheiro_para_carregar,
)
from logger import get_logger

log = get_logger("transacao")

# ── Dicionario principal: { "TRN00001": { campo: valor, ... } }
base_transacoes = {}

# ── Lista usada como pilha para controlo do contador de IDs
pilha_ids_transacao = [1]

# ── Tuplo dos campos editaveis
CAMPOS_EDITAVEIS_TRANSACAO = (
    "tipo", "tipo_movimento", "montante",
    "metodo_pagamento", "estado"
)

# ── Dicionario de despacho de validacao — campo -> funcao
VALIDACOES_TRANSACAO = {
    "tipo"             : validar_tipo_transacao,
    "tipo_movimento"   : validar_tipo_movimento,
    "montante"         : validar_montante,
    "metodo_pagamento" : validar_metodo_pagamento,
    "estado"           : validar_estado_transacao,
}

# ── Caminho do ficheiro JSON de persistencia
FICHEIRO_TRANSACOES = "transacoes.json"


# ══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ══════════════════════════════════════════════════════════════

def guardar_transacoes():
    with open(FICHEIRO_TRANSACOES, "w", encoding="utf-8") as f:
        json.dump(
            {
                "base_transacoes": base_transacoes,
                "pilha_ids_transacao": pilha_ids_transacao
            },
            f,
            indent=4,
            ensure_ascii=False
        )
    log.debug("Transacoes guardadas em '%s'.", FICHEIRO_TRANSACOES)


def carregar_transacoes():
    global base_transacoes, pilha_ids_transacao

    if os.path.exists(FICHEIRO_TRANSACOES):
        with open(FICHEIRO_TRANSACOES, "r", encoding="utf-8") as f:
            dados = json.load(f)

        base_transacoes.clear()
        base_transacoes.update(dados.get("base_transacoes", {}))

        pilha_ids_transacao.clear()
        pilha_ids_transacao.extend(
            dados.get("pilha_ids_transacao", [1])
        )
        log.debug("Transacoes carregadas: %d registo(s).", len(base_transacoes))

    else:
        base_transacoes.clear()
        pilha_ids_transacao.clear()
        pilha_ids_transacao.append(1)
        log.debug("Ficheiro '%s' nao encontrado. Base iniciada vazia.", FICHEIRO_TRANSACOES)


# ══════════════════════════════════════════════════════════════
#  CREATE — 201 Created
# ══════════════════════════════════════════════════════════════

def criar_transacao(id_cliente, tipo, tipo_movimento,
                    montante, metodo_pagamento, estado="PENDENTE"):
    log.info("Criar transacao: id_cliente='%s', tipo='%s', montante='%s'.",
             id_cliente, tipo, montante)
    try:
        rv = validar_id_cliente(id_cliente)
        if not rv["valido"]:
            log.error("Validacao falhou (id_cliente): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        id_cli_ok = rv["valor"]

        rv = validar_tipo_transacao(tipo)
        if not rv["valido"]:
            log.error("Validacao falhou (tipo): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        tipo_ok = rv["valor"]

        rv = validar_tipo_movimento(tipo_movimento)
        if not rv["valido"]:
            log.error("Validacao falhou (tipo_movimento): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        tipo_mov_ok = rv["valor"]

        rv = validar_montante(montante)
        if not rv["valido"]:
            log.error("Validacao falhou (montante): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        montante_ok = rv["valor"]

        rv = validar_metodo_pagamento(metodo_pagamento)
        if not rv["valido"]:
            log.error("Validacao falhou (metodo_pagamento): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        metodo_ok = rv["valor"]

        rv = validar_estado_transacao(estado)
        if not rv["valido"]:
            log.error("Validacao falhou (estado): %s", rv["mensagem"])
            return 422, rv["mensagem"]
        estado_ok = rv["valor"]

        # ── Construcao do registo ─────────────────────────────
        id_transacao = f"TRN{pilha_ids_transacao[0]:05d}"
        pilha_ids_transacao[0] += 1

        agora = datetime.now()
        transacao = {
            "id"               : id_transacao,
            "id_cliente"       : id_cli_ok,
            "tipo"             : tipo_ok,
            "tipo_movimento"   : tipo_mov_ok,
            "montante"         : montante_ok,
            "metodo_pagamento" : metodo_ok,
            "data_hora"        : agora.strftime("%d/%m/%Y %H:%M:%S"),
            "estado"           : estado_ok,
        }
        base_transacoes[id_transacao] = transacao
        log.info("Transacao criada com sucesso: id='%s'.", id_transacao)
        return 201, transacao

    except Exception as e:
        log.exception("Erro interno ao criar transacao: %s", e)
        return 500, f"Erro interno: {e}"


# ══════════════════════════════════════════════════════════════
#  READ — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def ler_transacao_por_id(id_transacao):
    t = base_transacoes.get(str(id_transacao).upper())
    if not t:
        log.error("Transacao nao encontrada: id='%s'.", id_transacao)
        return 404, "Transacao nao encontrada."
    log.debug("Transacao lida: id='%s'.", id_transacao)
    return 200, t

def listar_transacoes_por_cliente(id_cliente):
    id_cli = str(id_cliente).strip().upper()
    lista = [t for t in base_transacoes.values() if t["id_cliente"] == id_cli]
    if not lista:
        log.error("Nenhuma transacao encontrada para cliente: '%s'.", id_cliente)
        return 404, f"Nenhuma transacao encontrada para o cliente '{id_cliente}'."
    log.debug("Transacoes por cliente '%s': %d registo(s).", id_cliente, len(lista))
    return 200, lista

def listar_todas_transacoes():
    lista = list(base_transacoes.values())
    log.debug("Listagem de transacoes: %d registo(s).", len(lista))
    return 200, lista

def total_transacoes():
    return len(base_transacoes)


# ══════════════════════════════════════════════════════════════
#  UPDATE — 200 OK | 404 Not Found | 400/422 erros
# ══════════════════════════════════════════════════════════════

def atualizar_transacao(id_transacao, campo, valor):
    log.info("Atualizar transacao: id='%s', campo='%s'.", id_transacao, campo)
    t = base_transacoes.get(str(id_transacao).upper())
    if not t:
        log.error("Transacao nao encontrada para atualizar: id='%s'.", id_transacao)
        return 404, "Transacao nao encontrada."

    campo = campo.lower().strip()
    if campo not in CAMPOS_EDITAVEIS_TRANSACAO:
        log.error("Campo invalido para edicao: '%s'.", campo)
        return 400, f"Campo '{campo}' invalido. Editaveis: {' | '.join(CAMPOS_EDITAVEIS_TRANSACAO)}"

    if campo in VALIDACOES_TRANSACAO:
        rv = VALIDACOES_TRANSACAO[campo](valor)
        if not rv["valido"]:
            log.error("Validacao falhou ao atualizar transacao (%s): %s", campo, rv["mensagem"])
            return 422, rv["mensagem"]
        t[campo] = rv["valor"]
        log.info("Transacao atualizada: id='%s', campo='%s'.", id_transacao, campo)
        return 200, t

    return 400, f"Campo '{campo}' nao pode ser editado."


# ══════════════════════════════════════════════════════════════
#  DELETE — 200 OK | 404 Not Found
# ══════════════════════════════════════════════════════════════

def remover_transacao(id_transacao):
    log.info("Remover transacao: id='%s'.", id_transacao)
    id_upper = str(id_transacao).upper()
    if id_upper not in base_transacoes:
        log.error("Transacao nao encontrada para remover: id='%s'.", id_transacao)
        return 404, f"Transacao '{id_transacao}' nao encontrada."
    t = base_transacoes.pop(id_upper)
    log.info("Transacao removida: id='%s'.", id_upper)
    return 200, t
