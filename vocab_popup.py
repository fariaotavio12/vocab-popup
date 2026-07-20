# -*- coding: utf-8 -*-
"""
Vocab Popup — exibe a cada 4 minutos um popup discreto no canto da tela
(perto da barra de tarefas) com 3 palavras/expressões em inglês e suas
traduções, lidas do arquivo vocabulario.txt (formato: ingles;portugues).

Uso:
    python vocab_popup.py          (com janela de console)
    pythonw vocab_popup.py         (sem console — recomendado)
"""

import random
import sys
import tkinter as tk
from pathlib import Path

# ----------------------------- Configurações -----------------------------
ARQUIVO_VOCAB   = Path(__file__).with_name("vocabulario.txt")
SEPARADOR       = ";"          # separador das colunas no TXT
QTD_PALAVRAS    = 1            # quantas palavras por popup
INTERVALO_MIN   = 1            # intervalo entre popups, em minutos
DURACAO_SEG     = 11           # tempo que o popup fica visível, em segundos
MARGEM_PX       = 12           # distância das bordas da tela

COR_FUNDO      = "#1e2430"
COR_INGLES     = "#7fd4ff"
COR_PORTUGUES  = "#e8e8e8"
COR_TITULO     = "#9aa4b2"
COR_BORDA      = "#3a4556"
# --------------------------------------------------------------------------


def carregar_vocabulario():
    """Lê o TXT e devolve lista de tuplas (ingles, portugues)."""
    if not ARQUIVO_VOCAB.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_VOCAB}")

    pares = []
    # utf-8-sig aceita UTF-8 com ou sem BOM; latin-1 cobre TXT salvo no Bloco de Notas antigo
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            linhas = ARQUIVO_VOCAB.read_text(encoding=encoding).splitlines()
            break
        except UnicodeDecodeError:
            continue

    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        # aceita ponto e vírgula ou TAB como separador
        sep = SEPARADOR if SEPARADOR in linha else "\t"
        partes = linha.split(sep, 1)
        if len(partes) == 2:
            ingles, portugues = partes[0].strip(), partes[1].strip()
            if ingles and portugues:
                pares.append((ingles, portugues))

    if not pares:
        raise ValueError(f"Nenhuma linha válida em {ARQUIVO_VOCAB} (formato esperado: ingles{SEPARADOR}portugues)")
    return pares


class VocabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()          # janela principal fica invisível
        self.popup = None
        self.mostrar_popup()          # primeiro popup imediato

    def agendar_proximo(self):
        self.root.after(INTERVALO_MIN * 60 * 1000, self.mostrar_popup)

    def fechar_popup(self, _event=None):
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None

    def mostrar_popup(self):
        self.fechar_popup()           # garante que não empilha popups

        try:
            pares = carregar_vocabulario()   # relê o TXT: pode editar sem reiniciar
        except Exception as exc:
            print(f"Erro ao ler vocabulário: {exc}", file=sys.stderr)
            self.agendar_proximo()
            return

        sorteados = random.sample(pares, min(QTD_PALAVRAS, len(pares)))

        popup = tk.Toplevel(self.root)
        self.popup = popup
        popup.overrideredirect(True)          # sem borda/título do Windows
        popup.attributes("-topmost", True)    # sempre visível
        popup.configure(bg=COR_BORDA)

        quadro = tk.Frame(popup, bg=COR_FUNDO, padx=16, pady=12)
        quadro.pack(padx=1, pady=1)           # 1px de "borda" com a cor de fundo do popup

        tk.Label(
            quadro, text="English time!  (clique para fechar)",
            font=("Segoe UI", 8), fg=COR_TITULO, bg=COR_FUNDO,
        ).pack(anchor="w", pady=(0, 6))

        for ingles, portugues in sorteados:
            tk.Label(
                quadro, text=ingles,
                font=("Segoe UI Semibold", 12), fg=COR_INGLES, bg=COR_FUNDO,
                anchor="w", justify="left",
            ).pack(anchor="w")
            tk.Label(
                quadro, text=portugues,
                font=("Segoe UI", 10), fg=COR_PORTUGUES, bg=COR_FUNDO,
                anchor="w", justify="left",
            ).pack(anchor="w", pady=(0, 7))

        # clique em qualquer lugar do popup fecha
        for widget in (popup, quadro, *quadro.winfo_children()):
            widget.bind("<Button-1>", self.fechar_popup)

        # posiciona no canto inferior direito, acima da barra de tarefas
        popup.update_idletasks()
        largura = popup.winfo_reqwidth()
        altura  = popup.winfo_reqheight()
        x = popup.winfo_screenwidth() - largura - MARGEM_PX
        y = self._topo_barra_tarefas() - altura - MARGEM_PX
        popup.geometry(f"+{x}+{y}")

        popup.after(DURACAO_SEG * 1000, self.fechar_popup)
        self.agendar_proximo()

    def _topo_barra_tarefas(self):
        """Retorna a coordenada Y do topo da barra de tarefas (área de trabalho útil)."""
        try:
            import ctypes
            from ctypes import wintypes
            rect = wintypes.RECT()
            # SPI_GETWORKAREA = 0x0030 → área da tela sem a barra de tarefas
            ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
            return rect.bottom
        except Exception:
            return self.root.winfo_screenheight() - 48   # estimativa padrão

    def executar(self):
        self.root.mainloop()


if __name__ == "__main__":
    VocabApp().executar()
