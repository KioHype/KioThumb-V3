import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageGrab
import os, sys, threading, json, re, tempfile, time, random
try:
    import winsound
    _HAS_SOUND = True
except:
    _HAS_SOUND = False

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════
YT_W, YT_H  = 1280, 720
PV_W, PV_H  = 854, 480
APP_DIR      = os.path.dirname(os.path.abspath(__file__))

# Paleta anos 90 / Hypnospace
BG        = "#0a0a1a"
SURFACE   = "#141428"
SURFACE2  = "#1c1c38"
SURFACE3  = "#0e0e22"
ACCENT    = "#44cc66"
ACCENT2   = "#339955"
ACCENT_M  = "#aa55cc"
ACCENT_Y  = "#ccaa33"
ACCENT_R  = "#cc3344"
ACCENT_C  = "#3388aa"
TEXT      = "#dddde8"
TEXT_NEON = "#44cc66"
MUTED     = "#8888aa"
BORDER    = "#6633aa"
BORDER2   = "#226688"
DANGER    = "#cc3344"
SUCCESS   = "#44cc66"
CHECK_BG  = "#0e0e22"
TITLE_COL = "#ccaa33"

SUPPORTED_IMAGE = (".png",".jpg",".jpeg",".bmp",".webp")
def _play_click():
    if _HAS_SOUND:
        try: winsound.Beep(800, 40)
        except: pass

def _play_open():
    if _HAS_SOUND:
        try:
            for freq in [400, 600, 900, 1200]:
                winsound.Beep(freq, 60)
        except: pass



def resource_path(rel):
    try:    base = sys._MEIPASS
    except: base = APP_DIR
    return os.path.join(base, rel)

def get_windows_fonts():
    fd = os.path.join(os.environ.get("WINDIR","C:\\Windows"),"Fonts")
    out = []
    if os.path.isdir(fd):
        for f in os.listdir(fd):
            if f.lower().endswith((".ttf",".otf")):
                out.append(f)
    return sorted(out)

def find_font(name):
    fd = os.path.join(os.environ.get("WINDIR","C:\\Windows"),"Fonts")
    p  = os.path.join(fd, name)
    return p if os.path.exists(p) else None

# ══════════════════════════════════════════════════════════════════════════════
# BOTÃO ESTILO ANOS 90
# ══════════════════════════════════════════════════════════════════════════════
class RetroBtn(tk.Button):
    def __init__(self, parent, text, cmd, fg=BG, bg=ACCENT,
                 hover_bg=ACCENT_Y, size=9, pady=4, padx=8, **kwargs):
        super().__init__(parent, text=text, command=cmd,
                         bg=bg, fg=fg,
                         activebackground=hover_bg, activeforeground=BG,
                         relief="raised", bd=3, cursor="hand2",
                         font=("Comic Sans MS", size, "bold"),
                         padx=padx, pady=pady, **kwargs)
        self._bg       = bg
        self._fg       = fg
        self._hover_bg = hover_bg
        self.bind("<Enter>", lambda e: self.config(bg=hover_bg, fg=BG, relief="sunken"))
        self.bind("<Leave>", lambda e: self.config(bg=bg, fg=fg, relief="raised"))
        self.bind("<ButtonPress-1>", lambda e: _play_click())

def mkbtn(parent, text, cmd, fg=BG, bg=ACCENT, size=9, pady=4, padx=8):
    return RetroBtn(parent, text, cmd, fg=fg, bg=bg, size=size, pady=pady, padx=padx)

def mksep(parent, color=BORDER):
    f = tk.Frame(parent, bg=color, height=2)
    return f

def retro_label(parent, text, size=9, color=TEXT_NEON, bg=SURFACE, font_name="Comic Sans MS"):
    return tk.Label(parent, text=text, bg=bg, fg=color,
                    font=(font_name, size, "bold"))

# ══════════════════════════════════════════════════════════════════════════════
# ESTADO
# ══════════════════════════════════════════════════════════════════════════════
class BgImage:
    def __init__(self, path):
        self.path  = path
        self.ox    = 0.0
        self.oy    = 0.0
        self.scale = 1.0

    def to_dict(self):
        return {"path":self.path,"ox":self.ox,"oy":self.oy,"scale":self.scale}

    @staticmethod
    def from_dict(d):
        b = BgImage(d["path"])
        b.ox=d.get("ox",0.0); b.oy=d.get("oy",0.0); b.scale=d.get("scale",1.0)
        return b

class Overlay:
    def __init__(self, path, name=""):
        self.path = path
        self.name = name or os.path.basename(path)
        self.fx   = 0.72
        self.fy   = 0.04
        self.size = 180
        self.pil  = Image.open(path).convert("RGBA")

    def to_dict(self):
        return {"path":self.path,"name":self.name,
                "fx":self.fx,"fy":self.fy,"size":self.size}

    @staticmethod
    def from_dict(d):
        try:
            ov = Overlay(d["path"], d.get("name",""))
            ov.fx=d.get("fx",0.72); ov.fy=d.get("fy",0.04); ov.size=d.get("size",180)
            return ov
        except: return None

# ══════════════════════════════════════════════════════════════════════════════
# PRÉVIA EM GRADE
# ══════════════════════════════════════════════════════════════════════════════
class GridPreview(tk.Toplevel):
    def __init__(self, parent, bg_images, qty, start, composer):
        super().__init__(parent)
        self.title("KioThumb 3 — PRÉVIA TOTAL !!!!!")
        self.configure(bg=BG)
        self.geometry("980x620")
        self.grab_set()
        self.bg_images = bg_images
        self.qty       = qty
        self.start     = start
        self.composer  = composer
        self._build()
        self._render()

    def _build(self):
        hdr = tk.Frame(self,bg=BG,height=50); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr,text="★ PRÉVIA DE TODAS AS THUMBNAILS ★",
                 bg=BG,fg=ACCENT_Y,font=("Comic Sans MS",14,"bold")).pack(side="left",padx=14,pady=10)
        mkbtn(hdr,"↺ ATUALIZAR!!",self._render,bg=ACCENT_M,pady=4).pack(side="right",padx=12,pady=10)
        mksep(self,ACCENT_Y).pack(fill="x")

        c = tk.Canvas(self,bg=BG,highlightthickness=0)
        sb= tk.Scrollbar(self,orient="vertical",command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y"); c.pack(fill="both",expand=True)
        self._inner = tk.Frame(c,bg=BG)
        win = c.create_window((0,0),window=self._inner,anchor="nw")
        self._inner.bind("<Configure>",lambda e: c.configure(scrollregion=c.bbox("all")))
        c.bind("<Configure>",lambda e: c.itemconfig(win,width=e.width))
        mksep(self,ACCENT_M).pack(fill="x")
        ft = tk.Frame(self,bg=SURFACE,height=44); ft.pack(fill="x"); ft.pack_propagate(False)
        mkbtn(ft,"FECHAR xD",self.destroy,bg=DANGER,pady=6).pack(side="right",padx=12,pady=6)

    def _render(self):
        for w in self._inner.winfo_children(): w.destroy()
        tk.Label(self._inner,text="CARREGANDO... POR FAVOR AGUARDE...",
                 bg=BG,fg=ACCENT,font=("Courier",10,"bold")).pack(pady=20)
        self.update()
        for w in self._inner.winfo_children(): w.destroy()
        n=len(self.bg_images); cols=4
        for i in range(self.qty):
            bg  = self.bg_images[i] if i<n else (self.bg_images[n-1] if n else None)
            num = self.start+i
            colors = [BORDER, BORDER2, ACCENT_Y, ACCENT_M, ACCENT_R]
            fr  = tk.Frame(self._inner,bg=SURFACE2,highlightthickness=2,
                           highlightbackground=colors[i%len(colors)])
            fr.grid(row=i//cols,column=i%cols,padx=5,pady=5,sticky="nsew")
            self._inner.grid_columnconfigure(i%cols,weight=1)
            try:
                img = self.composer(bg,num,320,180)
                ph  = ImageTk.PhotoImage(img)
                lb  = tk.Label(fr,image=ph,bg=SURFACE2); lb.image=ph; lb.pack(padx=3,pady=3)
            except: pass
            tk.Label(fr,text=f"#{num}",bg=SURFACE2,fg=ACCENT_Y,
                     font=("Comic Sans MS",9,"bold")).pack(pady=(0,4))

# ══════════════════════════════════════════════════════════════════════════════
# JANELA DE AJUDA SARCÁSTICA
# ══════════════════════════════════════════════════════════════════════════════
class HelpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("AJUDA PARA LEIGOS")
        self.configure(bg=BG)
        self.geometry("540x420")
        self.resizable(False, False)
        self.grab_set()

        slides = [
            ("🌟 BEM-VINDO, GÊNIO!! 🌟",
             "Parabéns! Você conseguiu abrir o programa!\n\nEsse botãozinho de '?' que você clicou serve para explicar\ncomo funciona o KioThumb 3... para quem não consegue\ndescobrir sozinho como clicar em botões.\n\nVamos lá, devagarzinho..."),
            ("📁 ADICIONANDO IMAGENS (uau!)",
             "Sabe aquele botão escrito '+ ADICIONAR IMAGEM'?\n\nENTÃO. CLICA NELE.\n\nVai abrir uma janelinha para você escolher uma imagem\ndo seu computador. Ou aperta Ctrl+V se tiver\numa print na área de transferência.\n\nIncrível, né? Tecnologia avançada."),
            ("🖱️ MEXENDO NO PREVIEW (parte difícil)",
             "Aquela tela grande no meio? É o PREVIEW.\n\nClica em algo lá dentro para selecionar\n(vai aparecer uma borda vermelha piscando).\n\nDepois ARRASTA com o mouse. É isso.\nScroll do mouse = zoom na imagem.\nScroll em cima de uma logo = muda o tamanho dela.\n\nCtrl+Z se você estragar tudo."),
            ("▶ GERANDO AS THUMBNAILS (o ponto do programa)",
             "Lá embaixo tem 'Início #' e 'Qtd'.\n\nInício = número do primeiro episódio.\nQtd = quantas thumbnails você quer gerar.\n\n1 imagem + Qtd 20 = 20 thumbs iguais.\n5 imagens + Qtd 5 = uma diferente pra cada.\n\nClica em '▶ GERAR' e escolhe onde salvar.\nParabéns, você usou o programa!!"),
        ]

        self._idx = 0

        # Header piscante
        hdr = tk.Frame(self, bg=BG); hdr.pack(fill="x")
        self._blink_lbl = tk.Label(hdr,
            text="★★★ CENTRAL DE AJUDA PARA USUÁRIOS CONFUSOS ★★★",
            bg=BG, fg=ACCENT_Y, font=("Comic Sans MS",11,"bold"))
        self._blink_lbl.pack(pady=8)
        self._blink()

        mksep(self, BORDER).pack(fill="x")

        tl = tk.Label(self, text="", bg=BG, fg=ACCENT_M,
                      font=("Comic Sans MS",13,"bold"),
                      wraplength=500, justify="left")
        tl.pack(padx=20, pady=(14,6), anchor="w")

        bl = tk.Label(self, text="", bg=BG, fg=TEXT,
                      font=("Courier",9), wraplength=500, justify="left")
        bl.pack(padx=20, pady=4, anchor="w", fill="both", expand=True)

        pl = tk.Label(self, text="", bg=BG, fg=MUTED,
                      font=("Courier",8))
        pl.pack(pady=(0,4))

        mksep(self, BORDER2).pack(fill="x")
        ft = tk.Frame(self, bg=SURFACE); ft.pack(fill="x", padx=16, pady=10)
        mkbtn(ft,"FECHAR (tchau!)",self.destroy,bg=DANGER,pady=6).pack(side="left")
        nb = mkbtn(ft,"PRÓXIMO >>",None,bg=ACCENT_M,pady=6); nb.pack(side="right")
        pb = mkbtn(ft,"<< ANTERIOR",None,bg=SURFACE2,fg=MUTED,pady=6)
        pb.pack(side="right",padx=6)

        def show(i):
            tl.config(text=slides[i][0])
            bl.config(text=slides[i][1])
            pl.config(text=f"Página {i+1} de {len(slides)} — sim, tem mais")
            nb.config(text="PRÓXIMO >>" if i<len(slides)-1 else "FECHAR (finalmente!)")
            nb.config(command=(lambda: show(i+1)) if i<len(slides)-1 else self.destroy)
            pb.config(state="normal" if i>0 else "disabled")
            pb.config(command=lambda: show(i-1))

        show(0)

    def _blink(self):
        cur = self._blink_lbl.cget("fg")
        self._blink_lbl.config(fg=ACCENT_Y if cur==BG else BG)
        self.after(600, self._blink)

# ══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class KioThumb3(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KioThumb 3 — GERADOR DE THUMBNAILS PROFISSIONAL!!!")
        self.geometry("1200x740")
        self.minsize(1000, 640)
        self.configure(bg=BG)
        self.resizable(True, True)
        # Fecha direto sem perguntar nada
        self.protocol("WM_DELETE_WINDOW", self._close_app)

        try:
            ip = resource_path("icone2.png")
            self._ico = tk.PhotoImage(file=ip)
            self.iconphoto(True, self._ico)
        except: pass

        # Estado
        self.bg_images    = []
        self.overlays     = []
        self.current_idx  = 0
        self.selected_ov  = None
        self.custom_fonts = {}
        self.selected     = None
        self._hover       = None
        self._drag_sx=0; self._drag_sy=0; self._drag_ref={}
        self._undo_stack  = []
        self._list_drag_start = None
        self._visit_count = self._load_visits()

        # Vars
        self.prefix_var     = tk.StringVar(value="#")
        self.start_var      = tk.IntVar(value=1)
        self.qty_var        = tk.IntVar(value=1)
        self.font_var       = tk.StringVar(value="arialbd.ttf")
        self.font_size_var  = tk.IntVar(value=72)
        self.text_color     = "#ffffff"
        self.outline_on     = tk.BooleanVar(value=True)
        self.outline_color  = "#000000"
        self.outline_sz_var = tk.IntVar(value=3)
        self.shadow_on      = tk.BooleanVar(value=False)
        self.shadow_color   = "#000000"
        self.shadow_opacity  = tk.IntVar(value=80)
        self.shadow_dist    = tk.IntVar(value=6)
        self.gradient_on    = tk.BooleanVar(value=False)
        self.text_color2    = "#FF00FF"  # segunda cor do degradê
        self._fav_fonts     = self._load_fav_fonts()
        self.export_fmt     = tk.StringVar(value="PNG")
        self.jpeg_quality   = tk.IntVar(value=92)
        self.text_fx = 0.05; self.text_fy = 0.78

        self._build()
        self._refresh_preview()
        self._load_recent_projects()
        self._start_marquee()

        self.bind("<Control-v>", self._paste)
        self.bind("<Control-V>", self._paste)
        self.bind("<Control-z>", self._undo)
        self.bind("<Control-Z>", self._undo)

        # Fade-in ao abrir
        self.attributes("-alpha", 0.0)
        self.after(100, self._fade_in)
        threading.Thread(target=_play_open, daemon=True).start()

    def _close_app(self):
        if _HAS_SOUND:
            try:
                import threading
                def bye_sound():
                    for freq in [1200, 900, 600, 400]:
                        winsound.Beep(freq, 50)
                threading.Thread(target=bye_sound, daemon=True).start()
                import time; time.sleep(0.25)
            except: pass
        self.destroy()

    def _fade_in(self, alpha=0.0):
        alpha += 0.08
        if alpha >= 1.0:
            self.attributes("-alpha", 1.0)
            return
        self.attributes("-alpha", alpha)
        self.after(30, lambda: self._fade_in(alpha))


    def _load_fav_fonts(self):
        p = os.path.join(APP_DIR, "fav_fonts.json")
        try:
            if os.path.exists(p):
                with open(p) as f: return json.load(f)
        except: pass
        return []

    def _save_fav_fonts(self):
        p = os.path.join(APP_DIR, "fav_fonts.json")
        try:
            with open(p,"w") as f: json.dump(self._fav_fonts, f)
        except: pass

    def _toggle_fav_font(self, name):
        if name in self._fav_fonts:
            self._fav_fonts.remove(name)
        else:
            self._fav_fonts.append(name)
        self._save_fav_fonts()
        self._update_font_combo()

    def _update_font_combo(self):
        all_fonts = get_windows_fonts()
        # Importadas
        imported = list(self.custom_fonts.keys())
        # Favoritas no topo
        favs = [f for f in self._fav_fonts if f in all_fonts or f in imported]
        rest = [f for f in all_fonts if f not in favs]
        ordered = []
        if favs:
            ordered += [f"★ {f}" for f in favs]
            ordered += ["─────────────"]
        ordered += rest + imported
        self.font_combo["values"] = ordered
        # Atualiza valor atual se necessário
        cur = self.font_var.get()
        if cur.startswith("★ "):
            pass  # já tem estrela
        elif f"★ {cur}" in ordered:
            self.font_var.set(f"★ {cur}")

    def _load_visits(self):
        p = os.path.join(APP_DIR, "visits.txt")
        try:
            if os.path.exists(p):
                with open(p) as f: return int(f.read().strip())
        except: pass
        return 0

    def _save_visits(self):
        p = os.path.join(APP_DIR, "visits.txt")
        try:
            with open(p,"w") as f: f.write(str(self._visit_count))
        except: pass

    # ══════════════════════════════════════════════════════════════════════════
    # BUILD UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build(self):
        # ── HEADER estilo anos 90 ──
        hdr = tk.Frame(self, bg=BG, height=80)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        try:
            ic = Image.open(resource_path("icone2.png")).convert("RGBA")
            ic.thumbnail((52,52))
            self._hico = ImageTk.PhotoImage(ic)
            tk.Label(hdr, image=self._hico, bg=BG).pack(side="left",padx=(10,4),pady=6)
        except: pass

        # Título estilo WordArt
        title_fr = tk.Frame(hdr, bg=BG)
        title_fr.pack(side="left", pady=6)
        tk.Label(title_fr, text="KioThumb 3", bg=BG, fg=ACCENT_Y,
                 font=("Times New Roman",30,"bold italic"),
                 relief="flat").pack(anchor="w")
        tk.Label(title_fr, text="~~~ GERADOR DE THUMBNAILS PROFISSIONAL ~~~",
                 bg=BG, fg=ACCENT_M, font=("Comic Sans MS",10,"bold")).pack(anchor="w")

        # Botão ? sarcástico
        help_btn = tk.Button(hdr, text=" ? ", bg=ACCENT_R, fg=ACCENT_Y,
                             relief="raised", bd=3, cursor="hand2",
                             font=("Comic Sans MS",11,"bold"),
                             command=self._show_help)
        help_btn.pack(side="right", padx=10, pady=14)
        help_btn.bind("<Enter>", lambda e: help_btn.config(bg=ACCENT_Y, fg=ACCENT_R))
        help_btn.bind("<Leave>", lambda e: help_btn.config(bg=ACCENT_R, fg=ACCENT_Y))

        # Menu projetos recentes
        self._recent_menu_btn = tk.Menubutton(hdr, text="📁 PROJETOS",
                                               bg=SURFACE2, fg=ACCENT_C,
                                               relief="raised", bd=2,
                                               cursor="hand2",
                                               font=("Comic Sans MS",8,"bold"),
                                               highlightthickness=1,
                                               highlightbackground=BORDER2)
        self._recent_menu = tk.Menu(self._recent_menu_btn, tearoff=0,
                                     bg=SURFACE2, fg=ACCENT_C,
                                     activebackground=ACCENT_M,
                                     activeforeground=BG,
                                     font=("Comic Sans MS",8))
        self._recent_menu_btn["menu"] = self._recent_menu
        self._recent_menu_btn.pack(side="right", padx=6, pady=14)

        # Separador colorido duplo
        mksep(self, ACCENT_M).pack(fill="x")
        mksep(self, ACCENT_C).pack(fill="x")

        # Marquee
        self._marquee_fr = tk.Frame(self, bg=SURFACE3, height=26)
        self._marquee_fr.pack(fill="x"); self._marquee_fr.pack_propagate(False)
        self._marquee_lbl = tk.Label(self._marquee_fr,
            text="★ BEM-VINDO AO KioThumb 3 ★ O MELHOR GERADOR DE THUMBNAILS DA INTERNET ★ MADE BY KioHype ★ ESTE SITE É MELHOR VISUALIZADO EM 1280x720 ★",
            bg=SURFACE3, fg=ACCENT_Y, font=("Courier",10,"bold"), anchor="w")
        self._marquee_lbl.place(x=0, y=2)
        self._marquee_x = 1200
        mksep(self, ACCENT_Y).pack(fill="x")

        body = tk.Frame(self, bg=BG); body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=SURFACE, width=210, relief="ridge", bd=2)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        self._build_left(left)

        right = tk.Frame(body, bg=SURFACE, width=265, relief="ridge", bd=2)
        right.pack(side="right", fill="y"); right.pack_propagate(False)
        self._build_right(right)

        mid = tk.Frame(body, bg=BG)
        mid.pack(side="left", fill="both", expand=True)
        self._build_center(mid)

        mksep(self, ACCENT_M).pack(fill="x")
        mksep(self, ACCENT_C).pack(fill="x")
        self._build_footer()

    def _start_marquee(self):
        def scroll():
            self._marquee_x -= 2
            w = self._marquee_lbl.winfo_reqwidth()
            if self._marquee_x < -w:
                self._marquee_x = 1200
            self._marquee_lbl.place(x=self._marquee_x, y=2)
            self.after(30, scroll)
        self.after(100, scroll)

    # ── Esquerda ──────────────────────────────────────────────────────────────
    def _build_left(self, p):
        tk.Label(p, text="~~~ IMAGENS ~~~", bg=SURFACE, fg=ACCENT_Y,
                 font=("Comic Sans MS",9,"bold")).pack(pady=(8,4),padx=6,anchor="w")
        mkbtn(p, "★ + ADICIONAR ★", self._add_from_image,
              bg=ACCENT, size=9).pack(fill="x",padx=6,pady=(0,2))
        tk.Label(p, text="(ou Ctrl+V pra colar print)",
                 bg=SURFACE, fg=MUTED, font=("Courier",7)).pack(padx=6,anchor="w")
        mksep(p, BORDER).pack(fill="x", pady=4)

        c = tk.Canvas(p, bg=SURFACE, highlightthickness=0)
        sb= tk.Scrollbar(p, orient="vertical", command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); c.pack(side="left", fill="both", expand=True)
        self._list_inner = tk.Frame(c, bg=SURFACE)
        win = c.create_window((0,0), window=self._list_inner, anchor="nw")
        self._list_inner.bind("<Configure>",
            lambda e: c.configure(scrollregion=c.bbox("all")))
        c.bind("<Configure>", lambda e: c.itemconfig(win, width=e.width))

    def _refresh_list(self):
        for w in self._list_inner.winfo_children(): w.destroy()
        for i, bg in enumerate(self.bg_images):
            self._make_bg_card(i, bg)

    def _make_bg_card(self, i, bg):
        is_cur = (i == self.current_idx)
        bg2    = SURFACE3 if is_cur else SURFACE2
        border = ACCENT_Y if is_cur else BORDER

        fr = tk.Frame(self._list_inner, bg=bg2, cursor="hand2",
                      highlightthickness=2, highlightbackground=border)
        fr.pack(fill="x", padx=4, pady=3)

        if bg.path and os.path.exists(bg.path):
            try:
                im = Image.open(bg.path).convert("RGB"); im.thumbnail((52,36))
                ph = ImageTk.PhotoImage(im)
                ll = tk.Label(fr, image=ph, bg=bg2); ll.image=ph
                ll.pack(side="left", padx=3, pady=3)
            except:
                tk.Label(fr, text="???", bg=bg2, fg=ACCENT_Y,
                         font=("Courier",8)).pack(side="left",padx=4)
        else:
            tk.Label(fr, text="???", bg=bg2, fg=ACCENT_Y,
                     font=("Courier",8)).pack(side="left",padx=4)

        name = os.path.basename(bg.path) if bg.path else "???"
        if len(name)>14: name=name[:12]+"…"
        info = tk.Frame(fr, bg=bg2); info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=f"#{i+1}", bg=bg2, fg=ACCENT_Y,
                 font=("Comic Sans MS",10,"bold")).pack(anchor="w",padx=4,pady=(3,0))
        tk.Label(info, text=name, bg=bg2, fg=MUTED,
                 font=("Courier",7)).pack(anchor="w",padx=4)

        tk.Button(fr, text="X", bg=bg2, fg=DANGER, relief="raised", bd=2,
                  cursor="hand2", font=("Comic Sans MS",8,"bold"),
                  command=lambda i=i: self._remove_bg(i)).pack(side="right",padx=3,pady=3)

        def enter(e, f=fr): f.config(highlightbackground=ACCENT_Y)
        def leave(e, f=fr): f.config(highlightbackground=ACCENT_Y if i==self.current_idx else BORDER)

        for w in fr.winfo_children():
            if not isinstance(w, tk.Button):
                w.bind("<ButtonPress-1>",   lambda e,idx=i: self._lpress(e,idx))
                w.bind("<B1-Motion>",       lambda e,idx=i: self._lmotion(e,idx))
                w.bind("<ButtonRelease-1>", lambda e,idx=i: self._lrelease(e,idx))
                w.bind("<Enter>", enter); w.bind("<Leave>", leave)
        fr.bind("<ButtonPress-1>",   lambda e,idx=i: self._lpress(e,idx))
        fr.bind("<B1-Motion>",       lambda e,idx=i: self._lmotion(e,idx))
        fr.bind("<ButtonRelease-1>", lambda e,idx=i: self._lrelease(e,idx))
        fr.bind("<Enter>", enter); fr.bind("<Leave>", leave)

    def _lpress(self,e,idx): self._list_drag_start=(idx,e.y_root)
    def _lmotion(self,e,idx): pass
    def _lrelease(self,e,idx):
        if self._list_drag_start is None: return
        orig,y0=self._list_drag_start; dy=e.y_root-y0; new=orig
        if   dy<-25 and orig>0:                        new=orig-1
        elif dy> 25 and orig<len(self.bg_images)-1:    new=orig+1
        if new!=orig:
            self.bg_images.insert(new,self.bg_images.pop(orig))
            if self.current_idx==orig:  self.current_idx=new
            elif self.current_idx==new: self.current_idx=orig
        else:
            self.current_idx=idx
        self._list_drag_start=None
        self._refresh_list(); self._refresh_preview()

    # ── Centro ────────────────────────────────────────────────────────────────
    def _build_center(self, p):
        tb = tk.Frame(p, bg=BG, height=32); tb.pack(fill="x"); tb.pack_propagate(False)
        mkbtn(tb,"↩ DESFAZER",self._undo,bg=SURFACE2,fg=ACCENT_C,size=8,pady=3,padx=6).pack(side="left",padx=8,pady=4)
        tk.Label(tb,text="[ 1280 × 720 px — YouTube ]",bg=BG,fg=MUTED,
                 font=("Courier",7)).pack(side="right",padx=12)

        fr = tk.Frame(p, bg=BG); fr.pack(expand=True)

        # Borda colorida ao redor do canvas
        border_fr = tk.Frame(fr, bg=BORDER, padx=3, pady=3)
        border_fr.pack(pady=10)
        inner_border = tk.Frame(border_fr, bg=BORDER2, padx=2, pady=2)
        inner_border.pack()

        self.cv = tk.Canvas(inner_border, width=PV_W, height=PV_H, bg="#000011",
                            cursor="crosshair", highlightthickness=0)
        self.cv.pack()

        self.cv.bind("<ButtonPress-1>",   self._cvpress)
        self.cv.bind("<B1-Motion>",       self._cvdrag)
        self.cv.bind("<ButtonRelease-1>", self._cvrelease)
        self.cv.bind("<MouseWheel>",      self._cvscroll)
        self.cv.bind("<Motion>",          self._cvhover)
        self.cv.bind("<Leave>",           self._cvleave)

    # ── Direita ───────────────────────────────────────────────────────────────
    def _build_right(self, p):
        c = tk.Canvas(p, bg=SURFACE, highlightthickness=0)
        sb= tk.Scrollbar(p, orient="vertical", command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); c.pack(fill="both", expand=True)
        inn = tk.Frame(c, bg=SURFACE)
        win = c.create_window((0,0), window=inn, anchor="nw")
        inn.bind("<Configure>",lambda e: c.configure(scrollregion=c.bbox("all")))
        c.bind("<Configure>",  lambda e: c.itemconfig(win,width=e.width))

        pad=dict(padx=8,pady=2)

        def sec(txt, color=ACCENT_Y):
            mksep(inn, color).pack(fill="x",pady=(10,4))
            tk.Label(inn,text=txt,bg=SURFACE,fg=color,
                     font=("Comic Sans MS",8,"bold")).pack(anchor="w",padx=8)

        tk.Label(inn,text="~~~ CONFIGURAÇÕES ~~~",bg=SURFACE,fg=ACCENT_M,
                 font=("Comic Sans MS",9,"bold")).pack(anchor="w",padx=8,pady=(10,4))

        sec("★ TEXTO DO EPISÓDIO ★")
        r=tk.Frame(inn,bg=SURFACE); r.pack(fill="x",**pad)
        tk.Label(r,text="Prefixo:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left")
        e=self._mkentry(r,self.prefix_var,8); e.pack(side="left",padx=4)
        e.bind("<KeyRelease>",lambda e:self._rp())

        tk.Label(inn,text="Fonte:",bg=SURFACE,fg=TEXT,
                 font=("Courier",8)).pack(anchor="w",padx=8,pady=(6,0))
        font_row = tk.Frame(inn,bg=SURFACE); font_row.pack(fill="x",padx=8,pady=2)
        self.font_combo=ttk.Combobox(font_row,textvariable=self.font_var,
                                      font=("Courier",8),state="readonly")
        self._update_font_combo()
        self.font_combo.pack(side="left",fill="x",expand=True)
        self.font_combo.bind("<<ComboboxSelected>>",lambda e:self._rp())
        fav_btn = tk.Button(font_row, text="★", bg=SURFACE2, fg=ACCENT_Y,
                            relief="raised", bd=2, cursor="hand2",
                            font=("Comic Sans MS",9,"bold"),
                            command=self._fav_current_font)
        fav_btn.pack(side="left",padx=(4,0))
        fav_btn.bind("<Enter>", lambda e: fav_btn.config(bg=ACCENT_Y,fg=BG))
        fav_btn.bind("<Leave>", lambda e: fav_btn.config(bg=SURFACE2,fg=ACCENT_Y))
        self._fav_btn = fav_btn
        mkbtn(inn,"+ IMPORTAR FONTE",self._import_font,bg=SURFACE2,fg=ACCENT_C,size=8).pack(fill="x",padx=8,pady=2)
        self._imp_lbl=tk.Label(inn,text="",bg=SURFACE,fg=ACCENT,font=("Courier",7))
        self._imp_lbl.pack(anchor="w",padx=8)

        tk.Label(inn,text="Tamanho:",bg=SURFACE,fg=TEXT,
                 font=("Courier",8)).pack(anchor="w",padx=8,pady=(6,0))
        self._mkslider(inn,self.font_size_var,8,300,ACCENT_Y)

        sec("★ CORES E EFEITOS ★", ACCENT_M)
        cr=tk.Frame(inn,bg=SURFACE); cr.pack(fill="x",padx=8,pady=3)
        tk.Label(cr,text="Cor do texto:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left")
        self._tcol=tk.Button(cr,bg=self.text_color,width=3,relief="raised",bd=2,
                              cursor="hand2",command=self._pick_text)
        self._tcol.pack(side="left",padx=6)

        # Degradê vertical
        tk.Checkbutton(inn,text="DEGRADÊ no texto",variable=self.gradient_on,
                       bg=SURFACE,fg=ACCENT_Y,selectcolor=CHECK_BG,
                       activebackground=SURFACE,font=("Comic Sans MS",8,"bold"),
                       command=self._rp).pack(anchor="w",padx=8)
        gr=tk.Frame(inn,bg=SURFACE); gr.pack(fill="x",padx=8,pady=2)
        tk.Label(gr,text="2ª cor:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left")
        self._tcol2=tk.Button(gr,bg=self.text_color2,width=3,relief="raised",bd=2,
                               cursor="hand2",command=self._pick_text2)
        self._tcol2.pack(side="left",padx=6)
        tk.Label(gr,text="(topo→base)",bg=SURFACE,fg=MUTED,font=("Courier",7)).pack(side="left")

        tk.Checkbutton(inn,text="CONTORNO!!",variable=self.outline_on,
                       bg=SURFACE,fg=ACCENT_Y,selectcolor=CHECK_BG,
                       activebackground=SURFACE,font=("Comic Sans MS",8,"bold"),
                       command=self._rp).pack(anchor="w",padx=8)
        ocr=tk.Frame(inn,bg=SURFACE); ocr.pack(fill="x",padx=8,pady=2)
        tk.Label(ocr,text="Cor:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left")
        self._ocol=tk.Button(ocr,bg=self.outline_color,width=3,relief="raised",bd=2,
                              cursor="hand2",command=self._pick_outline)
        self._ocol.pack(side="left",padx=4)
        tk.Label(ocr,text="Esp.:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left",padx=(8,0))
        self._mkslider(inn,self.outline_sz_var,1,20,ACCENT_C)

        tk.Checkbutton(inn,text="SOMBRA",variable=self.shadow_on,
                       bg=SURFACE,fg=ACCENT_C,selectcolor=CHECK_BG,
                       activebackground=SURFACE,font=("Comic Sans MS",8,"bold"),
                       command=self._rp).pack(anchor="w",padx=8)
        scr=tk.Frame(inn,bg=SURFACE); scr.pack(fill="x",padx=8,pady=2)
        tk.Label(scr,text="Cor:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left")
        self._scol=tk.Button(scr,bg=self.shadow_color,width=3,relief="raised",bd=2,
                              cursor="hand2",command=self._pick_shadow)
        self._scol.pack(side="left",padx=6)
        tk.Label(inn,text="Opacidade:",bg=SURFACE,fg=TEXT,
                 font=("Courier",8)).pack(anchor="w",padx=8,pady=(4,0))
        self._mkslider(inn,self.shadow_opacity,0,100,ACCENT_M)
        tk.Label(inn,text="Distância:",bg=SURFACE,fg=TEXT,
                 font=("Courier",8)).pack(anchor="w",padx=8,pady=(4,0))
        self._mkslider(inn,self.shadow_dist,1,40,ACCENT_M)

        sec("★ SOBREPOSIÇÕES ★", ACCENT_C)
        mkbtn(inn,"+ ADICIONAR PNG",self._add_overlay,bg=SURFACE2,fg=ACCENT_C,size=8).pack(fill="x",padx=8,pady=3)
        tk.Label(inn,text="(logos, selos, etc)\nscroll em cima = redimensiona",
                 bg=SURFACE,fg=MUTED,font=("Courier",7),justify="left").pack(anchor="w",padx=8)
        self._ov_list_fr=tk.Frame(inn,bg=SURFACE)
        self._ov_list_fr.pack(fill="x",padx=8,pady=4)

        sec("★ EXPORTAR ★", ACCENT_Y)
        er=tk.Frame(inn,bg=SURFACE); er.pack(fill="x",padx=8,pady=4)
        tk.Label(er,text="Formato:",bg=SURFACE,fg=TEXT,font=("Courier",8)).pack(side="left")
        for fmt in ("PNG","JPEG"):
            tk.Radiobutton(er,text=fmt,variable=self.export_fmt,value=fmt,
                           bg=SURFACE,fg=ACCENT_Y,selectcolor=CHECK_BG,
                           activebackground=SURFACE,font=("Comic Sans MS",8,"bold"),
                           command=self._rp).pack(side="left",padx=4)
        tk.Label(inn,text="Qualidade JPEG:",bg=SURFACE,fg=TEXT,
                 font=("Courier",8)).pack(anchor="w",padx=8,pady=(4,0))
        self._mkslider(inn,self.jpeg_quality,50,100,ACCENT_Y)

        sec("★ PROJETOS ★", ACCENT_M)
        mkbtn(inn,"💾 SALVAR PROJETO",self._save_project,bg=SURFACE2,fg=ACCENT_Y,size=8).pack(fill="x",padx=8,pady=2)
        mkbtn(inn,"📂 ABRIR PROJETO",self._open_project,bg=SURFACE2,fg=ACCENT_C,size=8).pack(fill="x",padx=8,pady=2)

    def _mkentry(self,parent,var,width):
        return tk.Entry(parent,textvariable=var,width=width,
                        bg=SURFACE3,fg=ACCENT_Y,insertbackground=ACCENT_Y,
                        relief="sunken",bd=2,
                        font=("Courier",9))

    def _mkslider(self,parent,var,lo,hi,color=ACCENT):
        fr=tk.Frame(parent,bg=SURFACE); fr.pack(fill="x",padx=8,pady=2)
        vl=tk.Label(fr,text=str(var.get()),bg=SURFACE,fg=color,
                    font=("Courier",9,"bold"),width=5); vl.pack(side="right")
        tk.Scale(fr,from_=lo,to=hi,orient="horizontal",variable=var,showvalue=False,
                 bg=SURFACE,troughcolor=SURFACE3,activebackground=color,
                 highlightthickness=0,
                 command=lambda v,l=vl,c=color:(l.config(text=v,fg=c),self._rp())
                 ).pack(side="left",fill="x",expand=True)

    def _refresh_ov_list(self):
        for w in self._ov_list_fr.winfo_children(): w.destroy()
        colors=[BORDER,BORDER2,ACCENT_Y,ACCENT_M]
        for i,ov in enumerate(self.overlays):
            fr=tk.Frame(self._ov_list_fr,bg=SURFACE3,highlightthickness=1,
                        highlightbackground=colors[i%len(colors)])
            fr.pack(fill="x",pady=2)
            tk.Label(fr,text=ov.name[:18],bg=SURFACE3,fg=TEXT,
                     font=("Courier",7)).pack(side="left",padx=4,pady=3)
            tk.Button(fr,text="X",bg=SURFACE3,fg=DANGER,relief="raised",bd=1,
                      cursor="hand2",font=("Comic Sans MS",7,"bold"),
                      command=lambda i=i: self._remove_overlay(i)).pack(side="right",padx=3)

    # ── Rodapé ────────────────────────────────────────────────────────────────
    def _build_footer(self):
        ft=tk.Frame(self,bg=SURFACE,height=54,relief="ridge",bd=2)
        ft.pack(fill="x"); ft.pack_propagate(False)

        lf=tk.Frame(ft,bg=SURFACE); lf.pack(side="left",padx=10,pady=8)
        tk.Label(lf,text="Projeto:",bg=SURFACE,fg=MUTED,font=("Courier",7)).pack(side="left")
        self._proj_var = tk.StringVar(value="Novo Projeto")
        e=tk.Entry(lf,textvariable=self._proj_var,width=12,
                   bg=SURFACE3,fg=ACCENT_Y,insertbackground=ACCENT_Y,
                   relief="sunken",bd=2,font=("Courier",8))
        e.pack(side="left",padx=4)
        tk.Label(lf,text=" Início#",bg=SURFACE,fg=MUTED,font=("Courier",7)).pack(side="left")
        tk.Spinbox(lf,from_=1,to=9999,textvariable=self.start_var,width=4,
                   bg=SURFACE3,fg=ACCENT_Y,relief="sunken",bd=2,
                   buttonbackground=SURFACE2,font=("Courier",8),
                   command=self._rp).pack(side="left",padx=2)
        tk.Label(lf,text=" Qtd:",bg=SURFACE,fg=MUTED,font=("Courier",7)).pack(side="left")
        tk.Spinbox(lf,from_=1,to=999,textvariable=self.qty_var,width=4,
                   bg=SURFACE3,fg=ACCENT_Y,relief="sunken",bd=2,
                   buttonbackground=SURFACE2,font=("Courier",8)).pack(side="left",padx=2)

        cf=tk.Frame(ft,bg=SURFACE); cf.pack(side="left",expand=True)
        mkbtn(cf,"👁 VER PRÉVIA",self._show_grid_preview,bg=ACCENT_M,size=9,pady=6,padx=10).pack(side="left",padx=4)
        self._gen_btn=mkbtn(cf,"★ ▶ GERAR THUMBNAILS ★",self._generate,
                             bg=ACCENT,fg=BG,size=10,pady=8,padx=16)
        self._gen_btn.pack(side="left",padx=4)

        rf2=tk.Frame(ft,bg=SURFACE); rf2.pack(side="left",padx=6)
        for fmt in ("PNG","JPEG"):
            tk.Radiobutton(rf2,text=fmt,variable=self.export_fmt,value=fmt,
                           bg=SURFACE,fg=ACCENT_Y,selectcolor=CHECK_BG,
                           activebackground=SURFACE,font=("Comic Sans MS",8,"bold"),
                           command=self._rp).pack(side="left",padx=2)

        # Contador de visitas
        rf=tk.Frame(ft,bg=SURFACE3,relief="sunken",bd=2)
        rf.pack(side="right",padx=10,pady=8)
        tk.Label(rf,text="VISITAS:",bg=SURFACE3,fg=MUTED,
                 font=("Courier",7,"bold")).pack(padx=6,pady=(4,0))
        self._visit_count += 1
        self._save_visits()
        self._visit_lbl=tk.Label(rf,text=f"{self._visit_count:08d}",
                                  bg="#000000",fg=ACCENT,
                                  font=("Courier",11,"bold"))
        self._visit_lbl.pack(padx=6,pady=(0,4))

        self._res_lbl=tk.Label(ft,text="",bg=SURFACE,fg="#222244",font=("Courier",7))
        self._res_lbl.pack(side="right",padx=4)
        self._update_res()

    # ══════════════════════════════════════════════════════════════════════════
    # PREVIEW E COMPOSIÇÃO
    # ══════════════════════════════════════════════════════════════════════════
    def _rp(self,*_): self._refresh_preview()

    def _refresh_preview(self,*_):
        try:
            bg  = self.bg_images[self.current_idx] if self.bg_images else None
            num = self.start_var.get()
            img = self._compose(bg, num, PV_W, PV_H)
            self._pvphoto = ImageTk.PhotoImage(img)
            self.cv.delete("all")
            self.cv.create_image(0,0,anchor="nw",image=self._pvphoto)
            self._draw_sel()
            self._draw_hover()
        except Exception as ex:
            self.cv.delete("all")
            self.cv.create_text(PV_W//2,PV_H//2,
                                text=f"ERRO NO PREVIEW\n{ex}",
                                fill=ACCENT_R,font=("Courier",10),justify="center")

    def _compose(self, bg, number, W, H):
        base = Image.new("RGB",(W,H),"#000011")
        if bg and bg.path and os.path.exists(bg.path):
            try:
                src=Image.open(bg.path).convert("RGB")
                sw,sh=src.size
                bs=max(W/sw,H/sh)*bg.scale
                nw=max(1,int(sw*bs)); nh=max(1,int(sh*bs))
                scaled=src.resize((nw,nh),Image.LANCZOS)
                cx=nw//2+int(bg.ox*W); cy=nh//2+int(bg.oy*H)
                l=cx-W//2; t=cy-H//2; r=l+W; b=t+H
                if l<0:  l,r=0,W
                if t<0:  t,b=0,H
                if r>nw: l,r=nw-W,nw
                if b>nh: t,b=nh-H,nh
                l=max(0,min(l,nw-1)); t=max(0,min(t,nh-1))
                r=max(1,min(r,nw));   b=max(1,min(b,nh))
                crop=scaled.crop((l,t,r,b))
                if crop.size!=(W,H): crop=crop.resize((W,H),Image.LANCZOS)
                base.paste(crop,(0,0))
            except: pass

        draw  = ImageDraw.Draw(base)
        label = f"{self.prefix_var.get()}{number}"
        fsize = max(8,int(self.font_size_var.get()*W/YT_W))
        font  = self._load_font(fsize)
        tx=int(self.text_fx*W); ty=int(self.text_fy*H)

        if self.shadow_on.get():
            off=max(1,int(self.shadow_dist.get()*W/YT_W))
            opacity=int(self.shadow_opacity.get()*2.55)
            try:
                sr=int(self.shadow_color[1:3],16)
                sg=int(self.shadow_color[3:5],16)
                sb_=int(self.shadow_color[5:7],16)
                sh_l=Image.new("RGBA",base.size,(0,0,0,0))
                sd=ImageDraw.Draw(sh_l)
                sd.text((tx+off,ty+off),label,font=font,fill=(sr,sg,sb_,opacity))
                base_rgba=base.convert("RGBA")
                base_rgba=Image.alpha_composite(base_rgba,sh_l)
                base=base_rgba.convert("RGB")
                draw=ImageDraw.Draw(base)
            except:
                draw.text((tx+off,ty+off),label,font=font,fill=self.shadow_color)

        if self.outline_on.get():
            osz=max(1,int(self.outline_sz_var.get()*W/YT_W))
            for dx in range(-osz,osz+1):
                for dy in range(-osz,osz+1):
                    if dx or dy:
                        draw.text((tx+dx,ty+dy),label,font=font,fill=self.outline_color)

        if self.gradient_on.get():
            # Degradê vertical no texto via máscara
            try:
                # Renderiza texto em camada separada
                txt_layer = Image.new("RGBA", base.size, (0,0,0,0))
                td = ImageDraw.Draw(txt_layer)
                td.text((tx,ty), label, font=font, fill="#ffffff")
                # Bounding box do texto
                bbox = txt_layer.getbbox()
                if bbox:
                    x0,y0,x1,y1 = bbox
                    th = max(1, y1-y0)
                    # Cria gradiente vertical
                    grad = Image.new("RGBA",(x1-x0, th),(0,0,0,0))
                    c1r=int(self.text_color[1:3],16)
                    c1g=int(self.text_color[3:5],16)
                    c1b=int(self.text_color[5:7],16)
                    c2r=int(self.text_color2[1:3],16)
                    c2g=int(self.text_color2[3:5],16)
                    c2b=int(self.text_color2[5:7],16)
                    for gy in range(th):
                        t2=gy/th
                        r=int(c1r+(c2r-c1r)*t2)
                        g=int(c1g+(c2g-c1g)*t2)
                        b=int(c1b+(c2b-c1b)*t2)
                        for gx in range(x1-x0):
                            grad.putpixel((gx,gy),(r,g,b,255))
                    # Aplica gradiente usando texto como máscara
                    mask = txt_layer.crop(bbox).split()[3]
                    base_rgba = base.convert("RGBA")
                    base_rgba.paste(grad,(x0,y0),mask)
                    base = base_rgba.convert("RGB")
                    draw = ImageDraw.Draw(base)
            except:
                draw.text((tx,ty),label,font=font,fill=self.text_color)
        else:
            draw.text((tx,ty),label,font=font,fill=self.text_color)

        for ov in self.overlays:
            try:
                lsz=max(10,int(ov.size*W/YT_W))
                lg=ov.pil.copy(); lg.thumbnail((lsz,lsz),Image.LANCZOS)
                lx=max(0,min(int(ov.fx*W),W-lg.width))
                ly=max(0,min(int(ov.fy*H),H-lg.height))
                if lg.mode=="RGBA": base.paste(lg,(lx,ly),lg)
                else:               base.paste(lg,(lx,ly))
            except: pass

        return base

    def _load_font(self,size):
        sel=self.font_var.get()
        path=self.custom_fonts.get(sel) or find_font(sel)
        try:
            if path and os.path.exists(path):
                return ImageFont.truetype(path,size)
        except: pass
        try:    return ImageFont.truetype("arialbd.ttf",size)
        except:
            try: return ImageFont.truetype("arial.ttf",size)
            except: return ImageFont.load_default()

    # ══════════════════════════════════════════════════════════════════════════
    # HIT TEST
    # ══════════════════════════════════════════════════════════════════════════
    def _hit(self,x,y):
        for i in range(len(self.overlays)-1,-1,-1):
            ov=self.overlays[i]
            lsz=max(10,int(ov.size*PV_W/YT_W))
            lx=int(ov.fx*PV_W); ly=int(ov.fy*PV_H)
            if lx-8<=x<=lx+lsz+8 and ly-8<=y<=ly+lsz+8:
                return f"ov_{i}"
        tx=int(self.text_fx*PV_W); ty=int(self.text_fy*PV_H)
        fsize=max(8,int(self.font_size_var.get()*PV_W/YT_W))
        if tx-8<=x<=tx+fsize*5 and ty-8<=y<=ty+fsize+12:
            return "text"
        return "image"

    def _draw_sel(self):
        if self.selected: self._draw_handle(self.selected,"#FF0000",2,(4,3))

    def _draw_hover(self):
        if self._hover and self._hover!=self.selected:
            self._draw_handle(self._hover,ACCENT_Y,1,(3,4))

    def _draw_handle(self,target,color,width,dash):
        if target=="text":
            tx=int(self.text_fx*PV_W); ty=int(self.text_fy*PV_H)
            fsize=max(8,int(self.font_size_var.get()*PV_W/YT_W))
            self.cv.create_rectangle(tx-8,ty-8,tx+fsize*5,ty+fsize+12,
                                     outline=color,width=width,dash=dash)
        elif target=="image":
            self.cv.create_rectangle(4,4,PV_W-4,PV_H-4,
                                     outline=color,width=width,dash=dash)
        elif target and target.startswith("ov_"):
            idx=int(target[3:])
            if idx<len(self.overlays):
                ov=self.overlays[idx]
                lsz=max(10,int(ov.size*PV_W/YT_W))
                lx=int(ov.fx*PV_W); ly=int(ov.fy*PV_H)
                self.cv.create_rectangle(lx-8,ly-8,lx+lsz+8,ly+lsz+8,
                                         outline=color,width=width,dash=dash)

    # ══════════════════════════════════════════════════════════════════════════
    # CANVAS EVENTOS
    # ══════════════════════════════════════════════════════════════════════════
    def _cvpress(self,e):
        self._push_undo()
        self.selected=self._hit(e.x,e.y)
        if self.selected and self.selected.startswith("ov_"):
            self.selected_ov=int(self.selected[3:]); self._refresh_ov_list()
        self._drag_sx=e.x; self._drag_sy=e.y
        bg=self.bg_images[self.current_idx] if self.bg_images else None
        ref={"tx":self.text_fx,"ty":self.text_fy,
             "ox":bg.ox if bg else 0,"oy":bg.oy if bg else 0}
        for i,ov in enumerate(self.overlays):
            ref[f"ov_{i}_fx"]=ov.fx; ref[f"ov_{i}_fy"]=ov.fy
        self._drag_ref=ref
        self._refresh_preview()

    def _cvdrag(self,e):
        if not self.selected: return
        dx=(e.x-self._drag_sx)/PV_W; dy=(e.y-self._drag_sy)/PV_H
        if self.selected=="text":
            self.text_fx=max(0,min(0.95,self._drag_ref["tx"]+dx))
            self.text_fy=max(0,min(0.95,self._drag_ref["ty"]+dy))
        elif self.selected=="image" and self.bg_images:
            bg=self.bg_images[self.current_idx]
            bg.ox=self._drag_ref["ox"]-dx; bg.oy=self._drag_ref["oy"]-dy
        elif self.selected and self.selected.startswith("ov_"):
            idx=int(self.selected[3:])
            if idx<len(self.overlays):
                ov=self.overlays[idx]
                ov.fx=max(0,min(0.95,self._drag_ref[f"ov_{idx}_fx"]+dx))
                ov.fy=max(0,min(0.95,self._drag_ref[f"ov_{idx}_fy"]+dy))
        self._refresh_preview()

    def _cvrelease(self,e): pass

    def _cvscroll(self,e):
        delta=1 if e.delta>0 else -1
        hit=self._hit(e.x,e.y)
        if hit and hit.startswith("ov_"):
            idx=int(hit[3:])
            if idx<len(self.overlays):
                self.overlays[idx].size=max(20,min(1000,self.overlays[idx].size+delta*15))
        elif self.bg_images:
            bg=self.bg_images[self.current_idx]
            bg.scale=max(0.1,min(10.0,bg.scale+delta*0.05))
        self._rp()

    def _cvhover(self,e):
        h=self._hit(e.x,e.y)
        if h!=self._hover:
            self._hover=h
            self.cv.config(cursor="fleur" if h!="image" else "crosshair")
            self._refresh_preview()

    def _cvleave(self,e):
        self._hover=None; self._refresh_preview()


    def _push_undo(self):
        bg=self.bg_images[self.current_idx] if self.bg_images else None
        s={"tx":self.text_fx,"ty":self.text_fy,
           "ox":bg.ox if bg else 0,"oy":bg.oy if bg else 0,
           "scale":bg.scale if bg else 1}
        for i,ov in enumerate(self.overlays):
            s[f"ov_{i}"]={"fx":ov.fx,"fy":ov.fy,"size":ov.size}
        self._undo_stack.append(s)
        if len(self._undo_stack)>30: self._undo_stack.pop(0)

    def _undo(self,event=None):
        if not self._undo_stack: return
        s=self._undo_stack.pop()
        self.text_fx=s["tx"]; self.text_fy=s["ty"]
        if self.bg_images:
            bg=self.bg_images[self.current_idx]
            bg.ox=s["ox"]; bg.oy=s["oy"]; bg.scale=s["scale"]
        for i,ov in enumerate(self.overlays):
            key=f"ov_{i}"
            if key in s: ov.fx=s[key]["fx"]; ov.fy=s[key]["fy"]; ov.size=s[key]["size"]
        self._refresh_preview()

    # ══════════════════════════════════════════════════════════════════════════
    # ADICIONAR IMAGENS
    # ══════════════════════════════════════════════════════════════════════════
    def _add_from_image(self):
        files=filedialog.askopenfilenames(title="Selecionar imagens",
            filetypes=[("Imagens","*.png *.jpg *.jpeg *.bmp *.webp"),("Todos","*.*")])
        for f in files: self.bg_images.append(BgImage(f))
        if files:
            self._refresh_list(); self._refresh_preview()

    def _remove_bg(self,idx):
        self.bg_images.pop(idx)
        if self.current_idx>=len(self.bg_images):
            self.current_idx=max(0,len(self.bg_images)-1)
        self._refresh_list(); self._refresh_preview()

    def _paste(self,event=None):
        try:
            img=ImageGrab.grabclipboard()
            if img is None:
                messagebox.showinfo("KioThumb 3","NENHUMA IMAGEM ENCONTRADA!!\nAperta Print Screen primeiro, bro.")
                return
            if isinstance(img,Image.Image):
                tmp=tempfile.mktemp(suffix=".png"); img.save(tmp)
                self.bg_images.append(BgImage(tmp))
                self._refresh_list(); self._refresh_preview()
        except Exception as ex:
            messagebox.showerror("KioThumb 3",f"ERRO AO COLAR:\n{ex}")

    # ══════════════════════════════════════════════════════════════════════════
    # SOBREPOSIÇÕES
    # ══════════════════════════════════════════════════════════════════════════
    def _add_overlay(self):
        p=filedialog.askopenfilename(title="Adicionar sobreposição",
            filetypes=[("PNG","*.png"),("Imagens","*.png *.jpg *.jpeg"),("Todos","*.*")])
        if not p: return
        try:
            self.overlays.append(Overlay(p))
            self._refresh_ov_list(); self._rp()
        except Exception as ex:
            messagebox.showerror("KioThumb 3",f"ERRO:\n{ex}")

    def _remove_overlay(self,idx):
        self.overlays.pop(idx)
        if self.selected_ov==idx: self.selected_ov=None
        self._refresh_ov_list(); self._rp()

    # ══════════════════════════════════════════════════════════════════════════
    # CORES E FONTE
    # ══════════════════════════════════════════════════════════════════════════
    def _pick_text(self):
        c=colorchooser.askcolor(color=self.text_color,title="Cor do texto")
        if c and c[1]: self.text_color=c[1]; self._tcol.config(bg=c[1]); self._rp()

    def _pick_text2(self):
        c=colorchooser.askcolor(color=self.text_color2,title="2ª cor do degradê")
        if c and c[1]: self.text_color2=c[1]; self._tcol2.config(bg=c[1]); self._rp()

    def _pick_outline(self):
        c=colorchooser.askcolor(color=self.outline_color,title="Cor do contorno")
        if c and c[1]: self.outline_color=c[1]; self._ocol.config(bg=c[1]); self._rp()

    def _pick_shadow(self):
        c=colorchooser.askcolor(color=self.shadow_color,title="Cor da sombra")
        if c and c[1]: self.shadow_color=c[1]; self._scol.config(bg=c[1]); self._rp()

    def _fav_current_font(self):
        cur = self.font_var.get().lstrip("★ ").strip()
        if cur == "─────────────": return
        self._toggle_fav_font(cur)
        # Atualiza visual do botão
        if cur in self._fav_fonts:
            self._fav_btn.config(bg=ACCENT_Y, fg=BG)
        else:
            self._fav_btn.config(bg=SURFACE2, fg=ACCENT_Y)

    def _import_font(self):
        p=filedialog.askopenfilename(title="Importar fonte",filetypes=[("Fontes","*.ttf *.otf")])
        if not p: return
        name=os.path.basename(p)
        self.custom_fonts[name]=p
        self.font_combo["values"]=list(self.font_combo["values"])+[name]
        self.font_var.set(name)
        self._imp_lbl.config(text=f"✔ {name}")
        self._rp()

    # ══════════════════════════════════════════════════════════════════════════
    # AJUDA SARCÁSTICA
    # ══════════════════════════════════════════════════════════════════════════
    def _show_help(self):
        HelpWindow(self)

    # ══════════════════════════════════════════════════════════════════════════
    # PRÉVIA EM GRADE
    # ══════════════════════════════════════════════════════════════════════════
    def _show_grid_preview(self):
        if not self.bg_images:
            messagebox.showinfo("KioThumb 3","ADICIONE PELO MENOS UMA IMAGEM!!"); return
        GridPreview(self,self.bg_images,self.qty_var.get(),
                    self.start_var.get(),self._compose)

    # ══════════════════════════════════════════════════════════════════════════
    # GERAÇÃO
    # ══════════════════════════════════════════════════════════════════════════
    def _generate(self):
        qty=self.qty_var.get(); n=len(self.bg_images)
        if n==0:
            messagebox.showwarning("KioThumb 3","ADICIONE PELO MENOS UMA IMAGEM!!"); return
        if n>1 and n<qty:
            ok=messagebox.askyesno("KioThumb 3 — ATENÇÃO!!",
                f"Você pediu {qty} thumbnail(s) mas adicionou {n} imagem(ns).\n"
                f"A imagem #{n} vai ser repetida nas restantes.\n\nCONTINUAR?")
            if not ok: return

        folder=filedialog.askdirectory(title="Onde salvar as thumbnails?")
        if not folder: return

        fmt=self.export_fmt.get(); ext=".png" if fmt=="PNG" else ".jpg"
        pref="".join(c for c in self.prefix_var.get().strip()
                     if c.isalnum() or c in "-_") or "thumb"
        start=self.start_var.get()

        existing=[i for i in range(qty)
                  if os.path.exists(os.path.join(folder,f"{pref}{start+i}{ext}"))]
        if existing:
            ok=messagebox.askyesno("KioThumb 3 — ATENÇÃO!!",
                f"{len(existing)} arquivo(s) já existem na pasta.\nSUBSTITUIR?")
            if not ok: return

        self._gen_btn.config(state="disabled",text="GERANDO... AGUARDE...")
        self.update_idletasks()

        def worker():
            try:
                for i in range(qty):
                    num=start+i
                    bg=self.bg_images[i] if i<n else self.bg_images[n-1]
                    img=self._compose(bg,num,YT_W,YT_H)
                    path=os.path.join(folder,f"{pref}{num}{ext}")
                    if fmt=="PNG": img.save(path,"PNG")
                    else:          img.convert("RGB").save(path,"JPEG",
                                       quality=self.jpeg_quality.get(),optimize=True)
                self.after(0,lambda: messagebox.showinfo("KioThumb 3",
                    f"✔ {qty} THUMBNAIL(S) SALVA(S) COM SUCESSO!!\n\n{folder}"))
            except Exception as ex:
                self.after(0,lambda: messagebox.showerror("KioThumb 3",f"ERRO!!\n{ex}"))
            finally:
                self.after(0,lambda: self._gen_btn.config(
                    state="normal",text="★ ▶ GERAR THUMBNAILS ★"))

        threading.Thread(target=worker,daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    # SALVAR / ABRIR PROJETO
    # ══════════════════════════════════════════════════════════════════════════
    def _save_project(self):
        path=filedialog.asksaveasfilename(title="Salvar projeto",
            defaultextension=".json",
            initialfile=self._proj_var.get()+".json",
            filetypes=[("Projeto KioThumb","*.json")])
        if not path: return
        data={
            "project_name":self._proj_var.get(),
            "prefix":self.prefix_var.get(),
            "start":self.start_var.get(),
            "qty":self.qty_var.get(),
            "font":self.font_var.get(),
            "font_size":self.font_size_var.get(),
            "text_color":self.text_color,
            "outline_on":self.outline_on.get(),
            "outline_color":self.outline_color,
            "outline_sz":self.outline_sz_var.get(),
            "shadow_on":self.shadow_on.get(),
            "shadow_color":self.shadow_color,
            "shadow_opacity":self.shadow_opacity.get(),
            "shadow_dist":self.shadow_dist.get(),
            "gradient_on":self.gradient_on.get(),
            "text_color2":self.text_color2,
            "export_fmt":self.export_fmt.get(),
            "jpeg_quality":self.jpeg_quality.get(),
            "text_fx":self.text_fx,"text_fy":self.text_fy,
            "bg_images":[b.to_dict() for b in self.bg_images],
            "overlays":[o.to_dict() for o in self.overlays]
        }
        with open(path,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2,ensure_ascii=False)
        self._save_to_recent(path,self._proj_var.get())
        messagebox.showinfo("KioThumb 3",f"PROJETO SALVO!!\n{path}")

    def _open_project(self):
        path=filedialog.askopenfilename(title="Abrir projeto",
            filetypes=[("Projeto KioThumb","*.json")])
        if path: self._load_project(path)

    def _load_project(self,path):
        try:
            with open(path,"r",encoding="utf-8") as f: data=json.load(f)
            self._proj_var.set(data.get("project_name","Projeto"))
            self.prefix_var.set(data.get("prefix","#"))
            self.start_var.set(data.get("start",1))
            self.qty_var.set(data.get("qty",1))
            self.font_var.set(data.get("font","comic.ttf"))
            self.font_size_var.set(data.get("font_size",72))
            self.text_color=data.get("text_color","#FFFF00"); self._tcol.config(bg=self.text_color)
            self.outline_on.set(data.get("outline_on",True))
            self.outline_color=data.get("outline_color","#FF00FF"); self._ocol.config(bg=self.outline_color)
            self.outline_sz_var.set(data.get("outline_sz",3))
            self.shadow_on.set(data.get("shadow_on",False))
            self.shadow_color=data.get("shadow_color","#000000"); self._scol.config(bg=self.shadow_color)
            self.shadow_opacity.set(data.get("shadow_opacity",80))
            self.shadow_dist.set(data.get("shadow_dist",6))
            self.gradient_on.set(data.get("gradient_on",False))
            self.text_color2=data.get("text_color2","#FF00FF"); self._tcol2.config(bg=self.text_color2)
            self.export_fmt.set(data.get("export_fmt","PNG"))
            self.jpeg_quality.set(data.get("jpeg_quality",92))
            self.text_fx=data.get("text_fx",0.05); self.text_fy=data.get("text_fy",0.78)
            self.bg_images=[BgImage.from_dict(d) for d in data.get("bg_images",[])]
            self.overlays=[o for o in (Overlay.from_dict(d) for d in data.get("overlays",[])) if o]
            self.current_idx=0
            self._refresh_list(); self._refresh_ov_list(); self._refresh_preview()
            self._save_to_recent(path,data.get("project_name","Projeto"))
        except Exception as ex:
            messagebox.showerror("KioThumb 3",f"ERRO AO ABRIR:\n{ex}")

    def _save_to_recent(self,path,name):
        rec=os.path.join(APP_DIR,"recent.json")
        try:
            recents=[]
            if os.path.exists(rec):
                with open(rec) as f: recents=json.load(f)
            recents=[r for r in recents if r["path"]!=path]
            recents.insert(0,{"path":path,"name":name})
            with open(rec,"w") as f: json.dump(recents[:8],f)
            self._load_recent_projects()
        except: pass

    def _load_recent_projects(self):
        rec=os.path.join(APP_DIR,"recent.json")
        self._recent_menu.delete(0,"end")
        try:
            if os.path.exists(rec):
                with open(rec) as f: recents=json.load(f)
                for r in recents:
                    self._recent_menu.add_command(
                        label=f"{r['name']}  —  {os.path.basename(r['path'])}",
                        command=lambda p=r["path"]: self._load_project(p))
        except: pass

    # ══════════════════════════════════════════════════════════════════════════
    # RECURSOS
    # ══════════════════════════════════════════════════════════════════════════
    def _update_res(self):
        try:
            import psutil
            proc=psutil.Process(os.getpid())
            cpu=proc.cpu_percent(interval=None)
            ram=proc.memory_info().rss/1024/1024
            self._res_lbl.config(text=f"cpu {cpu:.0f}%  ram {ram:.0f}mb")
            if ram>800:
                messagebox.showwarning("KioThumb 3","MEMÓRIA CHEIA!! Encerrando.")
                self.destroy(); return
        except: pass
        self.after(4000,self._update_res)

# ══════════════════════════════════════════════════════════════════════════════
if __name__=="__main__":
    try:    import psutil
    except: import subprocess; subprocess.check_call([sys.executable,"-m","pip","install","psutil"]); import psutil
    KioThumb3().mainloop()
