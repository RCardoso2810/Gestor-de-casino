# ══════════════════════════════════════════════════════════════
#  app.py  —  Sistema de Gestão de Casino
# ══════════════════════════════════════════════════════════════

import tkinter as tk
from tkinter import ttk, messagebox

from casino import (
    criar_casino, ler_casino_por_id, listar_todos_casinos,
    atualizar_casino, remover_casino,
    CAMPOS_EDITAVEIS_CASINO, listar_casinos_disponiveis,
)
from cliente import (
    criar_cliente, ler_cliente_por_id, listar_todos_clientes,
    atualizar_cliente, remover_cliente,
    CAMPOS_EDITAVEIS_CLIENTE,
)
from jogo import (
    criar_jogo, ler_jogo_por_id, listar_todos_jogos,
    atualizar_jogo, remover_jogo,
    CAMPOS_EDITAVEIS_JOGO,
)
from transacao import (
    criar_transacao, ler_transacao_por_id, listar_todas_transacoes,
    listar_transacoes_por_cliente, atualizar_transacao, remover_transacao,
    CAMPOS_EDITAVEIS_TRANSACAO, carregar_transacoes,
)

# ── Paleta ────────────────────────────────────────────────────
COR_BG        = "#0F0F1A"
COR_PANEL     = "#16213E"
COR_CARD      = "#1A1A2E"
COR_ACCENT    = "#E94560"
COR_TEXT      = "#EAEAEA"
COR_TEXT_DIM  = "#8A8AA8"
COR_ENTRY_BG  = "#0D1B33"
COR_ENTRY_FG  = "#D0E8FF"
COR_SEP       = "#252540"
COR_BTN_OK    = "#1DB954"
COR_BTN_WARN  = "#F59E0B"
COR_BTN_DEL   = "#EF4444"
COR_BTN_INFO  = "#3B82F6"
COR_BTN_CLEAR = "#6B7280"

CORES_MODULO = {
    "casino":    "#E94560",
    "cliente":   "#3B82F6",
    "jogo":      "#10B981",
    "transacao": "#F59E0B",
}


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def _escurecer(hex_cor, fator=0.75):
    hex_cor = hex_cor.lstrip("#")
    r, g, b = (int(hex_cor[i:i+2], 16) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(
        max(0, int(r * fator)), max(0, int(g * fator)), max(0, int(b * fator))
    )

def _estilo_entry(e, width=26):
    e.configure(
        width=width,
        bg=COR_ENTRY_BG, fg=COR_ENTRY_FG,
        insertbackground=COR_ENTRY_FG,
        relief="flat", bd=0,
        highlightthickness=1,
        highlightcolor=COR_ACCENT,
        highlightbackground=COR_SEP,
        font=("Consolas", 10),
    )

def _btn(parent, text, command, cor, width=14):
    b = tk.Button(
        parent, text=text, command=command,
        bg=cor, fg="white",
        activebackground=_escurecer(cor, 0.7),
        activeforeground="white",
        relief="flat", bd=0,
        padx=10, pady=6,
        font=("Segoe UI", 9, "bold"),
        width=width, cursor="hand2",
    )
    b.bind("<Enter>", lambda e: b.config(bg=_escurecer(cor, 0.8)))
    b.bind("<Leave>", lambda e: b.config(bg=cor))
    return b

def _treeview_estilo(accent=COR_ACCENT):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Casino.Treeview",
        background=COR_CARD, foreground=COR_TEXT,
        fieldbackground=COR_CARD, rowheight=27,
        font=("Consolas", 9),
    )
    style.configure("Casino.Treeview.Heading",
        background=accent, foreground="white",
        font=("Segoe UI", 9, "bold"), relief="flat",
    )
    style.map("Casino.Treeview",
        background=[("selected", "#2A2A5A")],
        foreground=[("selected", "white")],
    )

def _janela_modulo(titulo, icone, cor_mod, largura=1050, altura=680):
    win = tk.Toplevel()
    win.title(f"{icone}  {titulo}")
    win.geometry(f"{largura}x{altura}")
    win.minsize(820, 500)
    win.configure(bg=COR_CARD)

    fr_topo = tk.Frame(win, bg=cor_mod, height=46)
    fr_topo.pack(fill="x")
    fr_topo.pack_propagate(False)
    tk.Label(fr_topo, text=f"{icone}  {titulo.upper()}",
             bg=cor_mod, fg="white",
             font=("Segoe UI", 12, "bold")).pack(side="left", padx=18, pady=8)

    _treeview_estilo(accent=cor_mod)
    return win

def _frame_form(parent, cor_mod):
    """
    Devolve (fr_outer, fr_grid):
      - fr_outer  : frame com pack — contém a stripe colorida e fr_grid
      - fr_grid   : sub-frame filho com APENAS grid — usa-se para os widgets
    Assim nunca se mistura pack e grid no mesmo container.
    """
    fr_outer = tk.Frame(parent, bg=COR_PANEL, padx=14, pady=10)
    fr_outer.pack(fill="x", padx=10, pady=(8, 4))

    # Linha colorida gerida por pack dentro de fr_outer — OK
    tk.Frame(fr_outer, bg=cor_mod, height=3).pack(fill="x", pady=(0, 6))

    # Sub-frame filho — todos os widgets usarão .grid() aqui
    fr_grid = tk.Frame(fr_outer, bg=COR_PANEL)
    fr_grid.pack(fill="x")          # pack só este frame dentro de fr_outer

    return fr_outer, fr_grid

def _frame_tabela(parent):
    fr = tk.Frame(parent, bg=COR_CARD)
    fr.pack(fill="both", expand=True, padx=10, pady=4)
    return fr

def _frame_botoes(parent):
    fr = tk.Frame(parent, bg=COR_CARD, pady=8, padx=10)
    fr.pack(fill="x")
    return fr

def _label_field(parent, text):
    return tk.Label(parent, text=text, bg=COR_PANEL,
                    fg=COR_TEXT_DIM, font=("Segoe UI", 9))

def _treeview_com_scroll(parent, colunas, larguras, altura=12):
    tabela = ttk.Treeview(parent, columns=colunas, show="headings",
                          height=altura, style="Casino.Treeview")
    for col, larg in zip(colunas, larguras):
        tabela.heading(col, text=col)
        tabela.column(col, width=larg, anchor="center")
    sb = ttk.Scrollbar(parent, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=sb.set)
    tabela.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return tabela

def _obter_casino_ids():
    _, lista = listar_todos_casinos()
    return [c["id"] for c in lista] if lista else []


# ══════════════════════════════════════════════════════════════
#  JANELA — CASINOS
# ══════════════════════════════════════════════════════════════

def abrir_casinos():
    cor = CORES_MODULO["casino"]
    win = _janela_modulo("Gestão de Casinos", "🏛", cor, 1000, 660)
    id_sel = tk.StringVar()

    _, fr = _frame_form(win, cor)   # fr é o sub-frame de grid

    grid_campos = [
        ("Nome",           "nome",  0, 0),
        ("Localização",    "loc",   0, 2),
        ("Taxa (%)",       "taxa",  0, 4),
        ("Moeda",          "moeda", 1, 0),
        ("Capacidade Máx", "cap",   1, 2),
    ]
    entries = {}
    for lbl, key, row, col in grid_campos:
        _label_field(fr, lbl).grid(row=row, column=col, sticky="w", pady=4, padx=(0,4))
        e = tk.Entry(fr); _estilo_entry(e)
        e.grid(row=row, column=col+1, pady=4, padx=(0,18))
        entries[key] = e

    tk.Frame(fr, bg=COR_SEP, height=1).grid(
        row=2, column=0, columnspan=6, sticky="ew", pady=(6, 4))

    _label_field(fr, "ID selecionado").grid(row=3, column=0, sticky="w", pady=4, padx=(0,4))
    e_id = tk.Entry(fr, textvariable=id_sel, state="readonly")
    _estilo_entry(e_id, 16); e_id.grid(row=3, column=1, pady=4, padx=(0,18))

    _label_field(fr, "Campo a editar").grid(row=3, column=2, sticky="w", pady=4, padx=(0,4))
    e_campo = tk.Entry(fr); _estilo_entry(e_campo, 18)
    e_campo.grid(row=3, column=3, pady=4, padx=(0,10))

    _label_field(fr, "Novo valor").grid(row=3, column=4, sticky="w", pady=4, padx=(0,4))
    e_valor = tk.Entry(fr); _estilo_entry(e_valor, 22)
    e_valor.grid(row=3, column=5, pady=4)

    tk.Label(fr, text=f"Campos editáveis: {' | '.join(CAMPOS_EDITAVEIS_CASINO)}",
             bg=COR_PANEL, fg=COR_TEXT_DIM, font=("Segoe UI", 8, "italic")
             ).grid(row=4, column=0, columnspan=6, sticky="w", pady=(2,0))

    fr_tab = _frame_tabela(win)
    colunas  = ("ID", "Nome", "Localização", "Taxa", "Moeda", "Capacidade", "Clientes", "Jogos")
    larguras = (60, 190, 160, 60, 70, 95, 70, 60)
    tabela = _treeview_com_scroll(fr_tab, colunas, larguras, 13)

    def limpar():
        id_sel.set("")
        e_campo.delete(0, "end"); e_valor.delete(0, "end")
        for e in entries.values(): e.delete(0, "end")

    def carregar():
        for r in tabela.get_children(): tabela.delete(r)
        _, lista = listar_todos_casinos()
        for c in lista:
            tabela.insert("", "end", values=(
                c["id"], c["nome"], c["localizacao"],
                f"{c['taxa']}%", c["moeda"], c["capacidade_maxima"],
                c["total_clientes"], c["total_jogos"]
            ))

    def ao_selecionar(event):
        sel = tabela.focus()
        if not sel: return
        vals = tabela.item(sel, "values")
        id_sel.set(vals[0])
        _, c = ler_casino_por_id(vals[0])
        if isinstance(c, dict):
            for key, field in [("nome","nome"),("loc","localizacao"),
                               ("taxa","taxa"),("moeda","moeda"),("cap","capacidade_maxima")]:
                entries[key].delete(0,"end"); entries[key].insert(0, c[field])

    def criar():
        code, obj = criar_casino(
            entries["nome"].get(), entries["loc"].get(),
            entries["taxa"].get(), entries["moeda"].get(), entries["cap"].get()
        )
        if code == 201:
            messagebox.showinfo("✓ Criado", f"Casino criado! ID: {obj['id']}", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def atualizar():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        campo, valor = e_campo.get().strip(), e_valor.get().strip()
        if not campo or not valor:
            messagebox.showwarning("Aviso", "Preencha 'Campo a editar' e 'Novo valor'.", parent=win); return
        code, obj = atualizar_casino(id_sel.get(), campo, valor)
        if code == 200:
            messagebox.showinfo("✓ Atualizado", "Casino atualizado.", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def remover():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        if messagebox.askyesno("Confirmar", f"Remover casino '{id_sel.get()}'?", parent=win):
            code, obj = remover_casino(id_sel.get())
            if code == 200:
                messagebox.showinfo("✓ Removido", f"Casino removido.", parent=win)
                limpar(); carregar()
            else:
                messagebox.showerror("Erro", str(obj), parent=win)

    tabela.bind("<<TreeviewSelect>>", ao_selecionar)

    fr_btn = _frame_botoes(win)
    _btn(fr_btn, "➕  Criar",            criar,    COR_BTN_OK).pack(side="left", padx=4)
    _btn(fr_btn, "✏  Atualizar",        atualizar, COR_BTN_WARN).pack(side="left", padx=4)
    _btn(fr_btn, "🗑  Remover",         remover,  COR_BTN_DEL).pack(side="left", padx=4)
    _btn(fr_btn, "↺  Limpar",          limpar,   COR_BTN_CLEAR).pack(side="left", padx=4)
    _btn(fr_btn, "⟳  Atualizar tabela", carregar, COR_BTN_INFO, 18).pack(side="right", padx=4)

    carregar()


# ══════════════════════════════════════════════════════════════
#  JANELA — CLIENTES
# ══════════════════════════════════════════════════════════════

def abrir_clientes():
    cor = CORES_MODULO["cliente"]
    win = _janela_modulo("Gestão de Clientes", "👤", cor, 1080, 720)
    id_sel = tk.StringVar()

    _, fr = _frame_form(win, cor)

    _label_field(fr, "Casino").grid(row=0, column=0, sticky="w", pady=4, padx=(0,4))
    casino_var = tk.StringVar()
    cb_casino = ttk.Combobox(fr, textvariable=casino_var, width=18, state="readonly")
    cb_casino.grid(row=0, column=1, pady=4, padx=(0,18))

    def _refresh_casinos():
        ids = _obter_casino_ids()
        cb_casino["values"] = ids
        if ids and not casino_var.get(): casino_var.set(ids[0])

    grid_campos = [
        ("Nome",                "nome",     0, 2),
        ("Nasc. (DD/MM/AAAA)", "nasc",     0, 4),
        ("Género (M/F/OUTRO)", "genero",   1, 0),
        ("Nacionalidade",      "nac",      1, 2),
        ("Contacto",           "contacto", 1, 4),
        ("Saldo (€)",          "saldo",    2, 0),
        ("Nível",              "nivel",    2, 2),
        ("Estado",             "estado",   2, 4),
    ]
    entries = {}
    for lbl, key, row, col in grid_campos:
        _label_field(fr, lbl).grid(row=row, column=col, sticky="w", pady=4, padx=(0,4))
        e = tk.Entry(fr); _estilo_entry(e)
        e.grid(row=row, column=col+1, pady=4, padx=(0,18))
        entries[key] = e

    tk.Frame(fr, bg=COR_SEP, height=1).grid(row=3, column=0, columnspan=6, sticky="ew", pady=(6,4))

    _label_field(fr, "ID selecionado").grid(row=4, column=0, sticky="w", pady=4, padx=(0,4))
    e_id = tk.Entry(fr, textvariable=id_sel, state="readonly")
    _estilo_entry(e_id, 16); e_id.grid(row=4, column=1, pady=4, padx=(0,18))

    _label_field(fr, "Campo a editar").grid(row=4, column=2, sticky="w", pady=4, padx=(0,4))
    e_campo = tk.Entry(fr); _estilo_entry(e_campo, 18)
    e_campo.grid(row=4, column=3, pady=4, padx=(0,10))

    _label_field(fr, "Novo valor").grid(row=4, column=4, sticky="w", pady=4, padx=(0,4))
    e_valor = tk.Entry(fr); _estilo_entry(e_valor, 22)
    e_valor.grid(row=4, column=5, pady=4)

    tk.Label(fr, text=f"Campos editáveis: {' | '.join(CAMPOS_EDITAVEIS_CLIENTE)}",
             bg=COR_PANEL, fg=COR_TEXT_DIM, font=("Segoe UI", 8, "italic")
             ).grid(row=5, column=0, columnspan=6, sticky="w", pady=(2,0))

    fr_tab = _frame_tabela(win)
    colunas  = ("ID", "Casino", "Nome", "Género", "Nacionalidade", "Contacto", "Saldo €", "Nível", "Estado")
    larguras = (80, 55, 170, 60, 120, 140, 75, 70, 70)
    tabela = _treeview_com_scroll(fr_tab, colunas, larguras, 10)

    def limpar():
        id_sel.set(); e_campo.delete(0,"end"); e_valor.delete(0,"end")
        for e in entries.values(): e.delete(0,"end")
        _refresh_casinos()

    def carregar():
        for r in tabela.get_children(): tabela.delete(r)
        _, lista = listar_todos_clientes()
        for c in lista:
            tabela.insert("","end", values=(
                c["id"], c["id_casino"], c["nome"], c["genero"],
                c["nacionalidade"], c["contacto"],
                f"{c['saldo']:.2f}", c["nivel"], c["estado"]
            ))

    def ao_selecionar(event):
        sel = tabela.focus()
        if not sel: return
        vals = tabela.item(sel, "values")
        id_sel.set(vals[0])
        _, c = ler_cliente_por_id(vals[0])
        if isinstance(c, dict):
            casino_var.set(c["id_casino"])
            mapa = [("nome","nome"),("nasc","data_nascimento"),("genero","genero"),
                    ("nac","nacionalidade"),("contacto","contacto"),
                    ("saldo","saldo"),("nivel","nivel"),("estado","estado")]
            for key, field in mapa:
                entries[key].delete(0,"end"); entries[key].insert(0, c[field])

    def criar():
        code, obj = criar_cliente(
            casino_var.get(),
            entries["nome"].get(), entries["nasc"].get(),
            entries["genero"].get(), entries["nac"].get(),
            entries["contacto"].get(), entries["saldo"].get(),
            entries["nivel"].get(), entries["estado"].get() or "ATIVO"
        )
        if code == 201:
            messagebox.showinfo("✓ Criado", f"Cliente criado! ID: {obj['id']}", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def atualizar():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        campo, valor = e_campo.get().strip(), e_valor.get().strip()
        if not campo or not valor:
            messagebox.showwarning("Aviso", "Preencha 'Campo a editar' e 'Novo valor'.", parent=win); return
        code, obj = atualizar_cliente(id_sel.get(), campo, valor)
        if code == 200:
            messagebox.showinfo("✓ Atualizado", "Cliente atualizado.", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def remover():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        if messagebox.askyesno("Confirmar", f"Remover cliente '{id_sel.get()}'?", parent=win):
            code, obj = remover_cliente(id_sel.get())
            if code == 200:
                messagebox.showinfo("✓ Removido", "Cliente removido.", parent=win)
                limpar(); carregar()
            else:
                messagebox.showerror("Erro", str(obj), parent=win)

    tabela.bind("<<TreeviewSelect>>", ao_selecionar)

    fr_btn = _frame_botoes(win)
    _btn(fr_btn, "➕  Criar",            criar,    COR_BTN_OK).pack(side="left", padx=4)
    _btn(fr_btn, "✏  Atualizar",        atualizar, COR_BTN_WARN).pack(side="left", padx=4)
    _btn(fr_btn, "🗑  Remover",         remover,  COR_BTN_DEL).pack(side="left", padx=4)
    _btn(fr_btn, "↺  Limpar",          limpar,   COR_BTN_CLEAR).pack(side="left", padx=4)
    _btn(fr_btn, "⟳  Atualizar tabela", carregar, COR_BTN_INFO, 18).pack(side="right", padx=4)

    _refresh_casinos()
    carregar()


# ══════════════════════════════════════════════════════════════
#  JANELA — JOGOS
# ══════════════════════════════════════════════════════════════

def abrir_jogos():
    cor = CORES_MODULO["jogo"]
    win = _janela_modulo("Gestão de Jogos", "🎲", cor, 1060, 720)
    id_sel = tk.StringVar()

    _, fr = _frame_form(win, cor)

    _label_field(fr, "Casino").grid(row=0, column=0, sticky="w", pady=4, padx=(0,4))
    casino_var = tk.StringVar()
    cb_casino = ttk.Combobox(fr, textvariable=casino_var, width=18, state="readonly")
    cb_casino.grid(row=0, column=1, pady=4, padx=(0,18))

    def _refresh_casinos():
        ids = _obter_casino_ids()
        cb_casino["values"] = ids
        if ids and not casino_var.get(): casino_var.set(ids[0])

    grid_campos = [
        ("Nome do Jogo",      "nome",    0, 2),
        ("Custo Mínimo (€)",  "custo",   0, 4),
        ("Saldo Banca (€)",   "saldo",   1, 0),
        ("Retorno",           "retorno", 1, 2),
        ("Nível Acesso",      "nivel",   1, 4),
        ("Estado",            "estado",  2, 0),
    ]
    entries = {}
    for lbl, key, row, col in grid_campos:
        _label_field(fr, lbl).grid(row=row, column=col, sticky="w", pady=4, padx=(0,4))
        e = tk.Entry(fr); _estilo_entry(e)
        e.grid(row=row, column=col+1, pady=4, padx=(0,18))
        entries[key] = e

    # Checkbuttons tipos — sub-frame com pack dentro de fr_tab_tipos
    # mas o fr_tab_tipos em si é colocado com grid dentro de fr
    fr_tipos = tk.Frame(fr, bg=COR_PANEL)
    fr_tipos.grid(row=2, column=2, columnspan=4, sticky="w", pady=4)
    tk.Label(fr_tipos, text="Tipos:", bg=COR_PANEL, fg=COR_TEXT_DIM,
             font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0,8))
    tipos_vars = {}
    for tipo in ("dealer", "tabuleiro", "pecas", "cartas", "dados", "maquina"):
        var = tk.StringVar(value="NAO")
        ck = tk.Checkbutton(
            fr_tipos, text=tipo.capitalize(), variable=var,
            onvalue="SIM", offvalue="NAO",
            bg=COR_PANEL, fg=COR_TEXT, selectcolor=COR_ENTRY_BG,
            activebackground=COR_PANEL, activeforeground=cor,
            font=("Segoe UI", 9),
        )
        ck.pack(side="left", padx=5)
        tipos_vars[tipo] = var

    tk.Frame(fr, bg=COR_SEP, height=1).grid(row=3, column=0, columnspan=6, sticky="ew", pady=(6,4))

    _label_field(fr, "ID selecionado").grid(row=4, column=0, sticky="w", pady=4, padx=(0,4))
    e_id = tk.Entry(fr, textvariable=id_sel, state="readonly")
    _estilo_entry(e_id, 16); e_id.grid(row=4, column=1, pady=4, padx=(0,18))

    _label_field(fr, "Campo a editar").grid(row=4, column=2, sticky="w", pady=4, padx=(0,4))
    e_campo = tk.Entry(fr); _estilo_entry(e_campo, 18)
    e_campo.grid(row=4, column=3, pady=4, padx=(0,10))

    _label_field(fr, "Novo valor").grid(row=4, column=4, sticky="w", pady=4, padx=(0,4))
    e_valor = tk.Entry(fr); _estilo_entry(e_valor, 22)
    e_valor.grid(row=4, column=5, pady=4)

    tk.Label(fr, text=f"Campos editáveis: {' | '.join(CAMPOS_EDITAVEIS_JOGO)}",
             bg=COR_PANEL, fg=COR_TEXT_DIM, font=("Segoe UI", 8, "italic")
             ).grid(row=5, column=0, columnspan=6, sticky="w", pady=(2,0))

    fr_tab = _frame_tabela(win)
    colunas  = ("ID", "Casino", "Nome", "Custo €", "Saldo €", "Retorno", "Nível", "Estado")
    larguras = (80, 60, 200, 75, 85, 75, 70, 70)
    tabela = _treeview_com_scroll(fr_tab, colunas, larguras, 10)

    def limpar():
        id_sel.set(); e_campo.delete(0,"end"); e_valor.delete(0,"end")
        for e in entries.values(): e.delete(0,"end")
        for v in tipos_vars.values(): v.set("NAO")
        _refresh_casinos()

    def carregar():
        for r in tabela.get_children(): tabela.delete(r)
        _, lista = listar_todos_jogos()
        for j in lista:
            tabela.insert("","end", values=(
                j["id"], j["id_casino"], j["nome"],
                f"{j['custo_minimo']:.2f}", f"{j['saldo_jogo']:.2f}",
                j["retorno"], j["nivel_acesso"], j["estado"]
            ))

    def ao_selecionar(event):
        sel = tabela.focus()
        if not sel: return
        vals = tabela.item(sel, "values")
        id_sel.set(vals[0])
        _, j = ler_jogo_por_id(vals[0])
        if isinstance(j, dict):
            casino_var.set(j["id_casino"])
            mapa = [("nome","nome"),("custo","custo_minimo"),("saldo","saldo_jogo"),
                    ("retorno","retorno"),("nivel","nivel_acesso"),("estado","estado")]
            for key, field in mapa:
                entries[key].delete(0,"end"); entries[key].insert(0, j[field])
            for tipo, var in tipos_vars.items():
                var.set(j["tipos"].get(tipo, "NAO"))

    def criar():
        code, obj = criar_jogo(
            casino_var.get(),
            entries["nome"].get(), entries["custo"].get(),
            entries["saldo"].get(), entries["retorno"].get(),
            entries["nivel"].get(), entries["estado"].get() or "ATIVO",
            tipos_vars["dealer"].get(), tipos_vars["tabuleiro"].get(),
            tipos_vars["pecas"].get(), tipos_vars["cartas"].get(),
            tipos_vars["dados"].get(), tipos_vars["maquina"].get(),
        )
        if code == 201:
            messagebox.showinfo("✓ Criado", f"Jogo criado! ID: {obj['id']}", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def atualizar():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        campo, valor = e_campo.get().strip(), e_valor.get().strip()
        if not campo or not valor:
            messagebox.showwarning("Aviso", "Preencha 'Campo a editar' e 'Novo valor'.", parent=win); return
        code, obj = atualizar_jogo(id_sel.get(), campo, valor)
        if code == 200:
            messagebox.showinfo("✓ Atualizado", "Jogo atualizado.", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def remover():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        if messagebox.askyesno("Confirmar", f"Remover jogo '{id_sel.get()}'?", parent=win):
            code, obj = remover_jogo(id_sel.get())
            if code == 200:
                messagebox.showinfo("✓ Removido", "Jogo removido.", parent=win)
                limpar(); carregar()
            else:
                messagebox.showerror("Erro", str(obj), parent=win)

    tabela.bind("<<TreeviewSelect>>", ao_selecionar)

    fr_btn = _frame_botoes(win)
    _btn(fr_btn, "➕  Criar",            criar,    COR_BTN_OK).pack(side="left", padx=4)
    _btn(fr_btn, "✏  Atualizar",        atualizar, COR_BTN_WARN).pack(side="left", padx=4)
    _btn(fr_btn, "🗑  Remover",         remover,  COR_BTN_DEL).pack(side="left", padx=4)
    _btn(fr_btn, "↺  Limpar",          limpar,   COR_BTN_CLEAR).pack(side="left", padx=4)
    _btn(fr_btn, "⟳  Atualizar tabela", carregar, COR_BTN_INFO, 18).pack(side="right", padx=4)

    _refresh_casinos()
    carregar()


# ══════════════════════════════════════════════════════════════
#  JANELA — TRANSAÇÕES
# ══════════════════════════════════════════════════════════════

def abrir_transacoes():
    cor = CORES_MODULO["transacao"]
    win = _janela_modulo("Gestão de Transações", "💳", cor, 1080, 700)
    id_sel = tk.StringVar()
    carregar_transacoes()

    _, fr = _frame_form(win, cor)

    grid_campos = [
        ("ID Cliente",              "id_cli",   0, 0),
        ("Tipo (ENTRADA/SAIDA)",    "tipo",     0, 2),
        ("Tipo Movimento",          "tipo_mov", 0, 4),
        ("Montante (€)",            "montante", 1, 0),
        ("Método Pagamento",        "metodo",   1, 2),
        ("Estado",                  "estado",   1, 4),
    ]
    entries = {}
    for lbl, key, row, col in grid_campos:
        _label_field(fr, lbl).grid(row=row, column=col, sticky="w", pady=4, padx=(0,4))
        e = tk.Entry(fr); _estilo_entry(e)
        e.grid(row=row, column=col+1, pady=4, padx=(0,18))
        entries[key] = e

    tk.Frame(fr, bg=COR_SEP, height=1).grid(row=2, column=0, columnspan=6, sticky="ew", pady=(6,4))

    _label_field(fr, "Filtrar por ID Cliente").grid(row=3, column=0, sticky="w", pady=4, padx=(0,4))
    e_filtro = tk.Entry(fr); _estilo_entry(e_filtro, 18)
    e_filtro.grid(row=3, column=1, pady=4, padx=(0,18))

    _label_field(fr, "ID selecionado").grid(row=3, column=2, sticky="w", pady=4, padx=(0,4))
    e_id = tk.Entry(fr, textvariable=id_sel, state="readonly")
    _estilo_entry(e_id, 16); e_id.grid(row=3, column=3, pady=4, padx=(0,10))

    _label_field(fr, "Campo  /  Novo valor").grid(row=3, column=4, sticky="w", pady=4, padx=(0,4))
    # sub-frame para os dois entries lado a lado — pack dentro dele, grid no fr pai
    fr_ed = tk.Frame(fr, bg=COR_PANEL)
    fr_ed.grid(row=3, column=5, pady=4)
    e_campo = tk.Entry(fr_ed, width=12); _estilo_entry(e_campo, 12); e_campo.pack(side="left", padx=(0,4))
    e_valor = tk.Entry(fr_ed, width=14); _estilo_entry(e_valor, 14); e_valor.pack(side="left")

    tk.Label(fr, text=f"Campos editáveis: {' | '.join(CAMPOS_EDITAVEIS_TRANSACAO)}",
             bg=COR_PANEL, fg=COR_TEXT_DIM, font=("Segoe UI", 8, "italic")
             ).grid(row=4, column=0, columnspan=6, sticky="w", pady=(2,0))

    fr_tab = _frame_tabela(win)
    colunas  = ("ID Transação", "ID Cliente", "Tipo", "Movimento", "Montante €", "Método", "Data/Hora", "Estado")
    larguras = (100, 85, 75, 80, 85, 115, 148, 90)
    tabela = _treeview_com_scroll(fr_tab, colunas, larguras, 11)

    def limpar():
        id_sel.set(); e_campo.delete(0,"end"); e_valor.delete(0,"end")
        e_filtro.delete(0,"end")
        for e in entries.values(): e.delete(0,"end")

    def _preencher(lista):
        for r in tabela.get_children(): tabela.delete(r)
        for t in lista:
            tabela.insert("","end", values=(
                t["id"], t["id_cliente"], t["tipo"],
                t["tipo_movimento"], f"{t['montante']:.2f}",
                t["metodo_pagamento"], t["data_hora"], t["estado"]
            ))

    def carregar():
        _, lista = listar_todas_transacoes(); _preencher(lista)

    def filtrar():
        id_cli = e_filtro.get().strip()
        if not id_cli: carregar(); return
        code, obj = listar_transacoes_por_cliente(id_cli)
        if code == 200: _preencher(obj)
        else: messagebox.showinfo("Sem resultados", str(obj), parent=win)

    def ao_selecionar(event):
        sel = tabela.focus()
        if not sel: return
        vals = tabela.item(sel, "values")
        id_sel.set(vals[0])
        _, t = ler_transacao_por_id(vals[0])
        if isinstance(t, dict):
            mapa = [("id_cli","id_cliente"),("tipo","tipo"),("tipo_mov","tipo_movimento"),
                    ("montante","montante"),("metodo","metodo_pagamento"),("estado","estado")]
            for key, field in mapa:
                entries[key].delete(0,"end"); entries[key].insert(0, t[field])

    def criar():
        code, obj = criar_transacao(
            entries["id_cli"].get(), entries["tipo"].get(),
            entries["tipo_mov"].get(), entries["montante"].get(),
            entries["metodo"].get(), entries["estado"].get() or "PENDENTE"
        )
        if code == 201:
            messagebox.showinfo("✓ Criada", f"Transação criada! ID: {obj['id']}", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def atualizar():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        campo, valor = e_campo.get().strip(), e_valor.get().strip()
        if not campo or not valor:
            messagebox.showwarning("Aviso", "Preencha o campo e o novo valor.", parent=win); return
        code, obj = atualizar_transacao(id_sel.get(), campo, valor)
        if code == 200:
            messagebox.showinfo("✓ Atualizado", "Transação atualizada.", parent=win)
            limpar(); carregar()
        else:
            messagebox.showerror("Erro", str(obj), parent=win)

    def remover():
        if not id_sel.get():
            messagebox.showwarning("Aviso", "Clique numa linha da tabela primeiro.", parent=win); return
        if messagebox.askyesno("Confirmar", f"Remover transação '{id_sel.get()}'?", parent=win):
            code, obj = remover_transacao(id_sel.get())
            if code == 200:
                messagebox.showinfo("✓ Removido", "Transação removida.", parent=win)
                limpar(); carregar()
            else:
                messagebox.showerror("Erro", str(obj), parent=win)

    tabela.bind("<<TreeviewSelect>>", ao_selecionar)

    fr_btn = _frame_botoes(win)
    _btn(fr_btn, "➕  Criar",      criar,    COR_BTN_OK).pack(side="left", padx=4)
    _btn(fr_btn, "🔍  Filtrar",   filtrar,  COR_BTN_INFO).pack(side="left", padx=4)
    _btn(fr_btn, "✏  Atualizar", atualizar, COR_BTN_WARN).pack(side="left", padx=4)
    _btn(fr_btn, "🗑  Remover",  remover,  COR_BTN_DEL).pack(side="left", padx=4)
    _btn(fr_btn, "↺  Limpar",   limpar,   COR_BTN_CLEAR).pack(side="left", padx=4)
    _btn(fr_btn, "⟳  Todos",    carregar, COR_BTN_INFO, 10).pack(side="right", padx=4)

    carregar()


# ══════════════════════════════════════════════════════════════
#  JANELA HUB — MENU PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    raiz = tk.Tk()
    raiz.title("Casino Management System")
    raiz.geometry("480x400")
    raiz.resizable(False, False)
    raiz.configure(bg=COR_BG)

    fr_banner = tk.Frame(raiz, bg=COR_ACCENT, height=90)
    fr_banner.pack(fill="x")
    fr_banner.pack_propagate(False)
    tk.Label(fr_banner, text="🎰", bg=COR_ACCENT,
             font=("Segoe UI", 32)).pack(side="left", padx=22)
    fr_txt = tk.Frame(fr_banner, bg=COR_ACCENT)
    fr_txt.pack(side="left", pady=18)
    tk.Label(fr_txt, text="CASINO MANAGEMENT SYSTEM",
             bg=COR_ACCENT, fg="white",
             font=("Segoe UI", 13, "bold")).pack(anchor="w")
    tk.Label(fr_txt, text="Seleciona um módulo para abrir a janela de gestão",
             bg=COR_ACCENT, fg="#FFD0D8",
             font=("Segoe UI", 9)).pack(anchor="w")

    fr_nav = tk.Frame(raiz, bg=COR_BG)
    fr_nav.pack(expand=True, fill="both", padx=40, pady=20)

    modulos = [
        ("🏛   Casinos",    CORES_MODULO["casino"],    abrir_casinos),
        ("👤   Clientes",   CORES_MODULO["cliente"],   abrir_clientes),
        ("🎲   Jogos",      CORES_MODULO["jogo"],      abrir_jogos),
        ("💳   Transações", CORES_MODULO["transacao"], abrir_transacoes),
    ]

    for texto, cor, comando in modulos:
        b = tk.Button(
            fr_nav,
            text=texto,
            command=comando,
            bg=cor,
            fg="white",
            activebackground=_escurecer(cor, 0.75),
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
            anchor="w",
            padx=20,
            pady=12,
        )
        b.pack(fill="x", pady=5)
        b.bind("<Enter>", lambda e, btn=b, c=cor: btn.config(bg=_escurecer(c, 0.80)))
        b.bind("<Leave>", lambda e, btn=b, c=cor: btn.config(bg=c))

    tk.Label(raiz,
             text="casino.py · cliente.py · jogo.py · transacao.py · utils.py",
             bg=COR_BG, fg=COR_TEXT_DIM,
             font=("Segoe UI", 8)).pack(pady=(0, 10))

    raiz.mainloop()


if __name__ == "__main__":
    main()