import json
from tkinter import BooleanVar
from tkinter import Toplevel
from tkinter import font as tkfont

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import time
import os

from BruteForce import BruteForce
from BoyerMoore import BoyerMoore, GoodSuffixHeuristic, BadCharacterHeuristic
from FileTextReader import DocumentReader
from TextPatternGenerator import TextPatternGenerator

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from mainv3 import SearchFileFrame

class SearchResult:
    def __init__(self, positions=None, comparisons=0, elapsed_ms=0.0):
        self.positions = positions or []
        self.comparisons = comparisons
        self.elapsed_ms = elapsed_ms


def create_modern_button(
    parent,
    text,
    command,
    style,
    **kwargs
):
    return ttk.Button(
        parent,
        text=text,
        command=command,
        style=style,
        cursor="hand2",
        **kwargs
    )


# =========================
# String matching algorithms
# =========================
def brute_force_search(text: str, pattern: str) -> SearchResult:
    start = time.perf_counter()
    positions = []
    comparisons = 0

    n = len(text)
    m = len(pattern)

    if m == 0:
        return SearchResult([], 0, 0.0)

    for i in range(n - m + 1):
        match = True
        for j in range(m):
            comparisons += 1
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)

    elapsed_ms = (time.perf_counter() - start) * 1000
    return SearchResult(positions, comparisons, elapsed_ms)


def build_bad_char_table(pattern: str):
    table = {}
    for i, ch in enumerate(pattern):
        table[ch] = i
    return table


def boyer_moore_search(text: str, pattern: str) -> SearchResult:
    start = time.perf_counter()
    positions = []
    comparisons = 0

    n = len(text)
    m = len(pattern)

    if m == 0:
        return SearchResult([], 0, 0.0)

    bad_char = build_bad_char_table(pattern)
    s = 0

    while s <= n - m:
        j = m - 1

        while j >= 0:
            comparisons += 1
            if pattern[j] == text[s + j]:
                j -= 1
            else:
                break

        if j < 0:
            positions.append(s)
            s += (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
        else:
            shift = max(1, j - bad_char.get(text[s + j], -1))
            s += shift

    elapsed_ms = (time.perf_counter() - start) * 1000
    return SearchResult(positions, comparisons, elapsed_ms)


# =============
# Main desktop UI
# =============
class DesktopSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("String Search Desktop App")
        self.geometry("1100x700")
        self.minsize(980, 620)
        self.configure(bg="#f4f6f8")

        self.logo_img = None
        self.current_frame = None
        self.nav_buttons = {}
        self.active_menu = "search"

        self._setup_style()
        self._build_layout()
        self.show_frame("search")

    def _set_active_nav(self, active_name: str):
        self.active_menu = active_name

        for name, btn in self.nav_buttons.items():
            btn_style = "NavButton.Active.TButton" if name == active_name else "NavButton.TButton"
            btn.configure(style=btn_style)

    def _on_nav_click(self, name: str):
        self._set_active_nav(name)
        self.show_frame(name)   

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # =========================================
        # Global Option Database for Combobox Popdown
        # =========================================
        self.option_add("TCombobox*Listbox.background", "#ffffff")
        self.option_add("TCombobox*Listbox.foreground", "#374151")
        self.option_add("TCombobox*Listbox.selectBackground", "#10b981")
        self.option_add("TCombobox*Listbox.selectForeground", "#ffffff")
        self.option_add("TCombobox*Listbox.font", ("Cambria", 11))
        self.option_add("TCombobox*Listbox.relief", "flat")
        self.option_add("TCombobox*Listbox.borderWidth", "0")
        # =========================================

        style.configure("Nav.TFrame", background="#0f172a")
        style.configure("Main.TFrame", background="#f4f6f8")
        style.configure("Card.TFrame", background="#ffffff")

        #
        style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            background="#cbd5e1",
            darkcolor="#cbd5e1",
            lightcolor="#cbd5e1",
            troughcolor="#f1f5f9",
            bordercolor="#f1f5f9",
            arrowcolor="#475569",
            relief="flat",
            borderwidth=0
        )

        style.map(
            "Modern.Vertical.TScrollbar",
            background=[
                ("active", "#94a3b8"),
                ("pressed", "#64748b")
            ],
            arrowcolor=[
                ("active", "#334155"),
                ("pressed", "#1e293b")
            ]
        )

        style.configure(
            "Modern.Horizontal.TScrollbar",
            gripcount=0,
            background="#cbd5e1",
            darkcolor="#cbd5e1",
            lightcolor="#cbd5e1",
            troughcolor="#f1f5f9",
            bordercolor="#f1f5f9",
            arrowcolor="#475569",
            relief="flat",
            borderwidth=0
        )

        style.map(
            "Modern.Horizontal.TScrollbar",
            background=[
                ("active", "#94a3b8"),
                ("pressed", "#64748b")
            ],
            arrowcolor=[
                ("active", "#334155"),
                ("pressed", "#1e293b")
            ]
        )
        #

        #
        style.configure(
            "Custom.Treeview",
            background="#ffffff",
            foreground="#111827",
            rowheight=34,
            fieldbackground="#ffffff",
            borderwidth=0,
            font=("Cambria", 10)
        )

        style.configure(
            "Custom.Treeview.Heading",
            background="#e5e7eb",
            foreground="#111827",
            relief="flat",
            font=("Cambria", 10, "bold"),
            padding=8
        )

        style.map(
            "Custom.Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")]
        )

        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#d1d5db")]
        )
        #

        style.configure(
            "Nav.TButton",
            font=("Cambria", 11, "bold"),
            padding=10,
            anchor="w"
        )
        style.map(
            "Nav.TButton",
            background=[("active", "#374151")],
            foreground=[("active", "#ffffff")]
        )

        style.configure(
            "NavButton.TButton",
            font=("Cambria", 11, "bold"),
            foreground="#cbd5e1",
            background="#111827",
            borderwidth=0,
            relief="flat",
            padding=(16, 12),
            anchor="w"
        )
        style.map(
            "NavButton.TButton",
            background=[("active", "#0f766e"), ("pressed", "#0d9488")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")]
        )

        style.configure(
            "NavButton.Active.TButton",
            font=("Cambria", 11, "bold"),
            foreground="#ffffff",
            background="#0d9488",
            borderwidth=0,
            relief="flat",
            padding=(16, 12),
            anchor="w"
        )
        style.map(
            "NavButton.Active.TButton",
            background=[("active", "#0f766e"), ("pressed", "#0d9488")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")]
        )

        style.configure("Title.TLabel", font=("Cambria", 18, "bold"), background="#f4f6f8")
        style.configure("Label.TLabel", font=("Cambria", 11), background="#ffffff")
        style.configure("Info.TLabel", font=("Cambria", 10), background="#ffffff")
        style.configure("ResultTitle.TLabel", font=("Cambria", 12, "bold"), background="#ffffff")

        style.configure(
            "TCombobox",
            foreground="#111827",
            fieldbackground="#ffffff",
            background="#ffffff",
            bordercolor="#d1d5db",
            lightcolor="#ffffff",
            darkcolor="#ffffff",
            arrowcolor="#10b981",
            padding=(6, 2, 6, 2),
            relief="flat",
            borderwidth=1,
            font=("Cambria", 10)
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#ffffff"), ("disabled", "#f3f4f6"), ("!disabled", "#ffffff")],
            background=[("readonly", "#ffffff"), ("disabled", "#f3f4f6"), ("active", "#ffffff")],
            bordercolor=[("focus", "#10b981"), ("!focus", "#d1d5db")],
            arrowcolor=[("active", "#10b981"), ("pressed", "#0f766e"), ("focus", "#10b981")]
        )

        style.configure(
            "Modern.TEntry",
            foreground="#111827",
            fieldbackground="#ffffff",
            bordercolor="#d1d5db",
            lightcolor="#ffffff",
            darkcolor="#ffffff",
            # padding=(10, 8, 10, 8),
            padding=(7, 5, 7, 5),

            relief="flat",
            borderwidth=1,
            font=("Cambria", 11)
        )
        style.map(
            "Modern.TEntry",
            fieldbackground=[("readonly", "#f3f4f6"), ("disabled", "#f3f4f6"), ("!disabled", "#ffffff")],
            bordercolor=[("focus", "#10b981"), ("!focus", "#d1d5db")]
        )

        style.configure(
            "Search.TButton",
            foreground="#ffffff",
            background="#10b981",
            bordercolor="#10b981",
            lightcolor="#10b981",
            darkcolor="#10b981",
            relief="flat",
            borderwidth=0,
            padding=(18, 7),
            font=("Cambria", 10, "bold")
        )
        style.map(
            "Search.TButton",
            background=[("active", "#059669"), ("pressed", "#047857")],
            bordercolor=[("active", "#059669"), ("pressed", "#047857"), ("focus", "#10b981")]
        )

        style.configure(
            "Clear.TButton",
            foreground="#ffffff",
            background="#64748b",
            bordercolor="#64748b",
            lightcolor="#64748b",
            darkcolor="#64748b",
            relief="flat",
            borderwidth=0,
            padding=(16, 7),
            font=("Cambria", 10, "bold")
        )
        style.map(
            "Clear.TButton",
            background=[("active", "#475569"), ("pressed", "#334155")],
            bordercolor=[("active", "#475569"), ("pressed", "#334155"), ("focus", "#64748b")]
        )

        style.configure(
            "Simulation.TButton",
            foreground="#ffffff",
            background="#8b5cf6",
            relief="flat",
            borderwidth=0,
            padding=(14, 7),
            font=("Cambria", 10, "bold")
        )
        style.map(
            "Simulation.TButton",
            background=[("active", "#7c3aed"), ("pressed", "#6d28d9")]
        )

        style.configure(
            "Step.TButton",
            foreground="#ffffff",
            background="#0d9488",
            relief="flat",
            borderwidth=0,
            padding=(14, 7),
            font=("Cambria", 10, "bold")
        )
        style.map(
            "Step.TButton",
            background=[("active", "#0f766e"), ("pressed", "#115e59")]
        )

        style.configure(
            "AutoPlay.TButton",
            foreground="#ffffff",
            background="#f97316",
            relief="flat",
            borderwidth=0,
            padding=(14, 7),
            font=("Cambria", 10, "bold")
        )
        style.map(
            "AutoPlay.TButton",
            background=[("active", "#ea580c"), ("pressed", "#c2410c")]
        )

        style.configure(
            "Stop.TButton",
            foreground="#ffffff",
            background="#ef4444",
            relief="flat",
            borderwidth=0,
            padding=(14, 7),
            font=("Cambria", 10, "bold")
        )
        style.map(
            "Stop.TButton",
            background=[("active", "#dc2626"), ("pressed", "#b91c1c")]
        )

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.nav_frame = ttk.Frame(self, style="Nav.TFrame", width=259)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)

        self.content_frame = ttk.Frame(self, style="Main.TFrame")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._build_navbar()

    def _build_navbar(self):
        logo_container = tk.Frame(self.nav_frame, bg="#0f172a")
        logo_container.pack(fill="x", pady=(18, 10), padx=14)

        brand_box = tk.Frame(logo_container, bg="#0f172a")
        brand_box.pack(fill="x")

        logo_path = "ptit_logo1.png"
        if os.path.exists(logo_path):
            try:
                # Load original image
                original_logo = tk.PhotoImage(file=logo_path)

                # Calculate subsample factor to make it about 64px high
                # subsample only takes integers
                factor = original_logo.height() // 64
                if factor < 1:
                    factor = 1

                self.logo_img = original_logo.subsample(factor, factor)
                logo_label = tk.Label(
                    brand_box,
                    image=self.logo_img,
                    bg="#0f172a"
                )
                logo_label.pack(anchor="w", pady=(0, 10))
            except Exception:
                fallback = tk.Label(
                    brand_box,
                    text="PTIT",
                    fg="#dc2626",
                    bg="white",
                    font=("Cambria", 18, "bold"),
                    width=4,
                    height=2
                )
                fallback.pack(anchor="w", pady=(0, 10))
        else:
            fallback = tk.Label(
                brand_box,
                text="PTIT",
                fg="#dc2626",
                bg="white",
                font=("Cambria", 18, "bold"),
                width=4,
                height=2
            )
            fallback.pack(anchor="w", pady=(0, 10))

        app_name = tk.Label(
            logo_container,
            text="String Search App",
            fg="white",
            bg="#0f172a",
            font=("Cambria", 14, "bold"),
            anchor="w"
        )
        app_name.pack(fill="x")

        subtitle = tk.Label(
            logo_container,
            text="Desktop pattern matching tool",
            fg="#94a3b8",
            bg="#0f172a",
            font=("Cambria", 9),
            anchor="w"
        )
        subtitle.pack(fill="x", pady=(4, 0))

        separator = tk.Frame(self.nav_frame, bg="#1e293b", height=1)
        separator.pack(fill="x", padx=14, pady=(12, 16))

        menu_frame = tk.Frame(self.nav_frame, bg="#0f172a")
        menu_frame.pack(fill="x", padx=12, pady=0)

        def create_nav_button(name, text, icon=""):
            btn = ttk.Button(
                menu_frame,
                text=f"{icon}  {text}" if icon else text,
                command=lambda: self._on_nav_click(name),
                style="NavButton.TButton",
                cursor="hand2"
            )
            btn.pack(fill="x", pady=5)
            self.nav_buttons[name] = btn

        create_nav_button("search", "Algorithm Visualization", "🔎")
        create_nav_button("performance", "Check Performance", "📊")
        # create_nav_button("file_search", "Search File", "📁")

        self._set_active_nav(self.active_menu)

        bottom_container = tk.Frame(self.nav_frame, bg="#0f172a")
        bottom_container.pack(side="bottom", fill="x", padx=14, pady=14)

        bottom_separator = tk.Frame(bottom_container, bg="#1e293b", height=1)
        bottom_separator.pack(fill="x", pady=(0, 12))

        hint = tk.Label(
            bottom_container,
            text="  ",
            justify="left",
            fg="#94a3b8",
            bg="#0f172a",
            font=("Cambria", 9)
        )
        hint.pack(fill="x")

    def show_frame(self, name: str):
        if self.current_frame is not None:
            self.current_frame.destroy()

        if name == "search":
            self.current_frame = SearchSingleFrame(self.content_frame)
        elif name == "performance":
            self.current_frame = CheckPerformanceFrame(self.content_frame)
        elif name == "file_search":
            self.current_frame = SearchFileFrame(self.content_frame)

        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)

        if hasattr(self, "nav_buttons"):
            self._set_active_nav(name)


class SearchSingleFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.text_widget = None
        self.reader = DocumentReader()
        self.pattern_var = tk.StringVar()
        self.algorithm_var = tk.StringVar(value="Brute Force")
        self.case_sensitive_var = tk.BooleanVar(value=False)
        self.result_vars = {
            "positions": tk.StringVar(value="[]"),
            "count": tk.StringVar(value="0"),
            "time": tk.StringVar(value="0.000 ms"),
            "comparisons": tk.StringVar(value="0")
        }
        self.simulation_steps = []
        self.current_step_index = -1
        self.sim_auto_job = None

        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Algorithm Visualization", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        left_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_card.grid_columnconfigure(0, weight=1)
        left_card.grid_rowconfigure(1, weight=1)

        right_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        right_card.grid(row=1, column=1, sticky="nsew")
        right_card.grid_columnconfigure(0, weight=1)

        sim_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        sim_card.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        sim_card.grid_columnconfigure(0, weight=1)
        sim_card.grid_rowconfigure(2, weight=1)

        ttk.Label(left_card, text="Text", style="Label.TLabel").grid(row=0, column=0, sticky="w")
        
        # Text widget wrapper frame with emerald border
        text_frame = tk.Frame(left_card, bg="#ffffff", highlightthickness=0, relief="flat")
        text_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 12))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        # self.text_widget = ScrolledText(
        #     text_frame,
        #     wrap="word",
        #     font=("Menlo", 12),
        #     height=18,
        #     bg="#ffffff",
        #     fg="#111827",
        #     insertbackground="#10b981",
        #     selectbackground="#10b981",
        #     selectforeground="#ffffff",
        #     relief="flat",
        #     borderwidth=1,
        #     # bordercolor="#d1d5db",
        #     highlightthickness=0
        # )
        self.text_widget = ScrolledText(
            text_frame,
            wrap="word",
            font=("Menlo", 12),
            height=18,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#10b981",
            selectbackground="#10b981",
            selectforeground="#ffffff",
            
            # Border & Color
            relief="flat",
            highlightthickness=1,                
            highlightbackground="#d1d5db",       
            highlightcolor="#10b981",             
            
            padx=8, 
            pady=5
        )

        self.text_widget.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.text_widget.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.text_widget.insert(
            "1.0",
            "Ví dụ: Boyer Moore là một thuật toán tìm kiếm chuỗi. Boyer Moore có thể nhanh hơn Brute Force trong nhiều trường hợp."
        )

        actions = tk.Frame(left_card, bg="#ffffff")
        actions.grid(row=2, column=0, sticky="ew")
        actions.grid_columnconfigure(1, weight=1)

        ttk.Label(actions, text="Pattern", style="Label.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        pattern_entry = ttk.Entry(actions, textvariable=self.pattern_var, font=("Cambria", 11), style="Modern.TEntry")
        pattern_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(actions, text="Algorithm", style="Label.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        algo_combo = ttk.Combobox(
            actions,
            textvariable=self.algorithm_var,
            state="readonly",
            values=["Brute Force", "Boyer Moore"]
        )
        algo_combo.grid(row=1, column=1, sticky="ew", pady=6)

        tk.Checkbutton(
            actions,
            text="Case sensitive",
            variable=self.case_sensitive_var,
            bg="#ffffff",
            fg="#374151",
            activebackground="#ffffff",
            activeforeground="#374151",
            selectcolor="#10b981",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            font=("Cambria", 10),
            anchor="w"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=6)

        button_row = tk.Frame(actions, bg="#ffffff")
        # button_row.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
        button_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

        # tk.Button(
        #     button_row,
        #     text="Search",
        #     command=self.run_search,
        #     bg="#16a34a",
        #     fg="white",
        #     activebackground="#15803d",
        #     activeforeground="white",
        #     bd=0,
        #     relief="flat",
        #     font=("Cambria", 11, "bold"),
        #     padx=18,
        #     pady=8,
        # ).pack(side="left")

        # tk.Button(
        #     button_row,
        #     text="Clear Highlight",
        #     command=self.clear_highlight,
        #     bg="#6b7280",
        #     fg="white",
        #     activebackground="#4b5563",
        #     activeforeground="white",
        #     bd=0,
        #     relief="flat",
        #     font=("Cambria", 10, "bold"),
        #     padx=16,
        #     pady=8,
        # ).pack(side="left", padx=8)

        create_modern_button(
            button_row,
            text="Upload File",
            command=self.upload_file,
            style="Simulation.TButton"
        ).pack(side="left")

        # Nút Search
        create_modern_button(
            button_row,
            text="Search",
            command=self.run_search,
            style="Search.TButton"
        ).pack(side="left", padx=8)

        create_modern_button(
            button_row,
            text="Clear Highlight",
            command=self.clear_highlight,
            style="Clear.TButton"
        ).pack(side="left", padx=8)

        ttk.Label(right_card, text="Results", style="ResultTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))

        self._result_item(right_card, 2, "Number of Occurrences", self.result_vars["count"])
        self._result_item(right_card, 1, "Found at Positions", self.result_vars["positions"])
        self._result_item(right_card, 4, "Number of Comparisons", self.result_vars["comparisons"])
        self._result_item(right_card, 3, "Processing Time", self.result_vars["time"])

        note = tk.Label(
            right_card,
            text=(
                # "Ghi chú:"
                # "- Kết quả vị trí được tính theo chỉ số bắt đầu từ 0."
                # "- Các cụm tìm thấy sẽ được tô màu vàng trong ô Text."
                ""
            ),
            justify="left",
            bg="#ffffff",
            fg="#374151",
            font=("Cambria", 10)
        )
        note.grid(row=5, column=0, sticky="ew", pady=(18, 0))

        ttk.Label(sim_card, text="Algorithm Simulation", style="ResultTitle.TLabel").grid(row=0, column=0, sticky="w")

        sim_controls = tk.Frame(sim_card, bg="#ffffff")
        sim_controls.grid(row=1, column=0, sticky="ew", pady=(10, 12))

        create_modern_button(
            sim_controls,
            text="Create Simulation",
            command=self.generate_simulation,
            style="Simulation.TButton"
        ).pack(side="left")

        create_modern_button(
            sim_controls,
            text="Previous Step",
            command=self.prev_step,
            style="Step.TButton"
        ).pack(side="left", padx=6)

        create_modern_button(
            sim_controls,
            text="Next Step",
            command=self.next_step,
            style="Step.TButton"
        ).pack(side="left", padx=6)

        create_modern_button(
            sim_controls,
            text="Auto Play",
            command=self.auto_play,
            style="AutoPlay.TButton"
        ).pack(side="left", padx=6)

        create_modern_button(
            sim_controls,
            text="Stop",
            command=self.stop_auto_play,
            style="Stop.TButton"
        ).pack(side="left", padx=6)

        # Simulation text widget wrapper frame with emerald border
        sim_text_frame = tk.Frame(sim_card, bg="#ffffff", highlightthickness=0, relief="flat")
        sim_text_frame.grid(row=2, column=0, sticky="nsew")
        sim_text_frame.grid_columnconfigure(0, weight=1)
        sim_text_frame.grid_rowconfigure(0, weight=1)
        
        self.sim_text = ScrolledText(
            sim_text_frame,
            # wrap="word",
            # font=("Menlo", 12),
            # height=12,
            # bg="#ffffff",
            # fg="#111827",
            # insertbackground="#10b981",
            # selectbackground="#10b981",
            # selectforeground="#ffffff",
            # relief="flat",
            # borderwidth=0,
            # highlightthickness=0
            wrap="word",
            font=("Menlo", 12),
            height=18,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#10b981",
            selectbackground="#10b981",
            selectforeground="#ffffff",
            
            relief="flat",
            highlightthickness=1,                
            highlightbackground="#d1d5db",       
            highlightcolor="#10b981",             
            
            padx=8, 
            pady=5, 
            state="disabled"

        )
        self.sim_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.text_widget.tag_configure("highlight", background="#fde047", foreground="#111827")
        self.text_widget.tag_configure("sim_window", background="#93c5fd", foreground="#111827")
        self.text_widget.tag_configure("sim_compare", background="#fca5a5", foreground="#111827")
        self.text_widget.tag_configure("sim_match", background="#86efac", foreground="#111827")

    # def _result_item(self, parent, row, label_text, value_var):
    #     container = tk.Frame(parent, bg="#f9fafb", bd=1, relief="solid", highlightthickness=0)
    #     container.grid(row=row, column=0, sticky="ew", pady=6)
    #     container.grid_columnconfigure(0, weight=1)

    #     label = tk.Label(container, text=label_text, bg="#f9fafb", fg="#374151", font=("Cambria", 10, "bold"))
    #     label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

    #     value = tk.Label(container, textvariable=value_var, bg="#f9fafb", fg="#111827", font=("Consolas", 11), justify="left", wraplength=300)
    #     value.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
    def _result_item(self, parent, row, label_text, value_var):
        container = tk.Frame(
            parent, 
            bg="#ffffff", 
            highlightbackground="#e2e8f0", # Viền xám rất nhạt
            highlightthickness=1, 
            relief="flat"
        )
        container.grid(row=row, column=0, sticky="ew", pady=6)
        container.grid_columnconfigure(1, weight=1) 

        accent = tk.Frame(container, bg="#10b981", width=4)
        accent.grid(row=0, column=0, rowspan=2, sticky="ns")

        label = tk.Label(
            container, 
            text=label_text.upper(), 
            bg="#ffffff", 
            fg="#64748b", # Màu Slate-500
            font=("Cambria", 8, "bold")
        )
        label.grid(row=0, column=1, sticky="w", padx=12, pady=(10, 0))

        value = tk.Label(
            container, 
            textvariable=value_var, 
            bg="#ffffff", 
            fg="#0f172a", #
            font=("Cambria Semibold", 11), 
            justify="left", 
            wraplength=350 
        )
        value.grid(row=1, column=1, sticky="w", padx=12, pady=(2, 10))

    def clear_highlight(self):
        self.text_widget.tag_remove("highlight", "1.0", tk.END)
        self.text_widget.tag_remove("sim_window", "1.0", tk.END)
        self.text_widget.tag_remove("sim_compare", "1.0", tk.END)
        self.text_widget.tag_remove("sim_match", "1.0", tk.END)

        self.sim_text.config(state="normal")
        self.sim_text.delete("1.0", tk.END)
        self.sim_text.config(state="disabled")

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file",
            filetypes=[
                ("Supported files", "*.txt *.pdf *.docx *.csv *.xlsx *.py *.js *.ts *.java *.cpp *.c *.html *.css *.json *.xml"),
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx"),
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("TypeScript files", "*.ts"),
                ("C/C++ files", "*.c *.cpp *.h *.hpp"),
                ("Web files", "*.html *.css"),
                ("JSON/XML files", "*.json *.xml"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # self.text_widget.config(state="normal")
            content = self.reader.read(file_path)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", content)
            self.clear_highlight()
            self.result_vars["positions"].set("[]")
            self.result_vars["count"].set("0")
            self.result_vars["time"].set("0.000 ms")
            self.result_vars["comparisons"].set("0")
            # self.text_widget.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")

    def run_search(self):
        text = self.text_widget.get("1.0", "end-1c")
        pattern = self.pattern_var.get()
        algorithm = self.algorithm_var.get()

        self.clear_highlight()

        if not pattern:
            messagebox.showwarning("Thiếu pattern", "Vui lòng nhập pattern cần tìm.")
            return

        if len(pattern) > len(text):
            self.result_vars["positions"].set("[]")
            self.result_vars["count"].set("0")
            self.result_vars["time"].set("0.000 ms")
            self.result_vars["comparisons"].set("0")
            messagebox.showinfo("Thông báo", "Pattern dài hơn text nên không có kết quả.")
            return
        case_sensitive = self.case_sensitive_var.get()
        if algorithm == "Brute Force":
            brute_force = BruteForce(text, pattern, case_sensitive=case_sensitive)
            result = brute_force.search()
        else:
            BoyerMoore.initialize(text, pattern, case_sensitive=case_sensitive)
            BoyerMoore.mainloop()
            result = BoyerMoore.RESULT

        self.result_vars["positions"].set(str(result.positions))
        self.result_vars["count"].set(str(len(result.positions)))
        self.result_vars["time"].set(f"{result.elapsed_ms:.3f} ms")
        self.result_vars["comparisons"].set(str(result.comparisons))

        self.highlight_matches(result.positions, len(pattern))

    def highlight_matches(self, positions, pattern_length):
        for pos in positions:
            start_index = f"1.0 + {pos} chars"
            end_index = f"1.0 + {pos + pattern_length} chars"
            self.text_widget.tag_add("highlight", start_index, end_index)

    def generate_simulation(self):
        self.stop_auto_play()
        text = self.text_widget.get("1.0", "end-1c")
        pattern = self.pattern_var.get()
        algorithm = self.algorithm_var.get()

        self.clear_highlight()
        self.sim_text.delete("1.0", tk.END)
        self.simulation_steps = []
        self.current_step_index = -1

        if not pattern:
            messagebox.showwarning("Thiếu pattern", "Vui lòng nhập pattern cần mô phỏng.")
            return

        if algorithm == "Brute Force":
            bf = BruteForce(text, pattern, case_sensitive=self.case_sensitive_var.get())
            self.simulation_steps = bf.build_bruteforce_steps()
        else:
            BoyerMoore.initialize(text, pattern, case_sensitive=self.case_sensitive_var.get())
            self.simulation_steps = BoyerMoore.build_BoyerMoore_steps() #self.build_boyermoore_steps(text, pattern)

        if not self.simulation_steps:
            self.sim_text.insert(tk.END, "Không có bước mô phỏng.")
            return

        self.current_step_index = 0
        self.show_step()

    def build_bruteforce_steps(self, text, pattern):
        steps = []
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return steps

        for i in range(n - m + 1):
            steps.append({
                "window_start": i,
                "compare_index": None,
                "matched_until": -1,
                "message": f"Đưa pattern vào vị trí i = {i}."
            })
            matched = True
            for j in range(m):
                is_match = text[i + j] == pattern[j]
                steps.append({
                    "window_start": i,
                    "compare_index": i + j,
                    "matched_until": i + j - 1 if is_match else i + j - 1,
                    "message": (
                        f"So sánh text[{i + j}] = '{text[i + j]}' với pattern[{j}] = '{pattern[j]}' -> "
                        + ("KHỚP" if is_match else "KHÔNG KHỚP")
                    )
                })
                if not is_match:
                    matched = False
                    steps.append({
                        "window_start": i,
                        "compare_index": i + j,
                        "matched_until": i + j - 1,
                        "message": "Mismatch, dịch pattern sang phải 1 vị trí."
                    })
                    break
            if matched:
                steps.append({
                    "window_start": i,
                    "compare_index": None,
                    "matched_until": i + m - 1,
                    "message": f"Tìm thấy pattern tại vị trí {i}."
                })
        return steps

    def build_boyermoore_steps(self, text, pattern):
        steps = []
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return steps

        bad_char = build_bad_char_table(pattern)
        s = 0

        while s <= n - m:
            steps.append({
                "window_start": s,
                "compare_index": None,
                "matched_until": -1,
                "message": f"Canh pattern tại vị trí s = {s}, bắt đầu so sánh từ phải sang trái."
            })
            j = m - 1
            matched_right_count = 0

            while j >= 0:
                is_match = pattern[j] == text[s + j]
                matched_until = s + m - 1 if matched_right_count > 0 else -1
                steps.append({
                    "window_start": s,
                    "compare_index": s + j,
                    "matched_until": matched_until,
                    "message": (
                        f"So sánh text[{s + j}] = '{text[s + j]}' với pattern[{j}] = '{pattern[j]}' -> "
                        + ("KHỚP" if is_match else "KHÔNG KHỚP")
                    )
                })
                if is_match:
                    matched_right_count += 1
                    j -= 1
                else:
                    break

            if j < 0:
                steps.append({
                    "window_start": s,
                    "compare_index": None,
                    "matched_until": s + m - 1,
                    "message": f"Tìm thấy pattern tại vị trí {s}."
                })
                shift = (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
                steps.append({
                    "window_start": s,
                    "compare_index": None,
                    "matched_until": s + m - 1,
                    "message": f"Dịch pattern sang phải {shift} vị trí."
                })
                s += shift
            else:
                bad_index = bad_char.get(text[s + j], -1)
                shift = max(1, j - bad_index)
                steps.append({
                    "window_start": s,
                    "compare_index": s + j,
                    "matched_until": -1,
                    "message": f"Mismatch tại text[{s + j}], bad character shift = {shift}."
                })
                s += shift
        return steps

    def show_step(self):
        if not self.simulation_steps or self.current_step_index < 0:
            return

        step = self.simulation_steps[self.current_step_index]
        self.clear_highlight()

        text = self.text_widget.get("1.0", "end-1c")
        pattern = self.pattern_var.get()
        window_start = step["window_start"]
        compare_index = step["compare_index"]
        matched_until = step["matched_until"]

        if pattern and 0 <= window_start < len(text):
            start_index = f"1.0 + {window_start} chars"
            end_index = f"1.0 + {min(window_start + len(pattern), len(text))} chars"
            self.text_widget.tag_add("sim_window", start_index, end_index)

        if compare_index is not None:
            cmp_start = f"1.0 + {compare_index} chars"
            cmp_end = f"1.0 + {compare_index + 1} chars"
            self.text_widget.tag_add("sim_compare", cmp_start, cmp_end)

        if matched_until is not None and matched_until >= window_start:
            match_start = f"1.0 + {window_start} chars"
            match_end = f"1.0 + {matched_until + 1} chars"
            self.text_widget.tag_add("sim_match", match_start, match_end)

        self.sim_text.config(state="normal")
        self.sim_text.delete("1.0", tk.END)
        self.sim_text.insert(
            tk.END,
            f"Bước {self.current_step_index + 1}/{len(self.simulation_steps)} \n"
            f"Thuật toán: {self.algorithm_var.get()} \n"
            f"Pattern: {pattern} \n"
            f"Mô tả: {step['message']}"
        )
        self.sim_text.config(state="disabled")
    def next_step(self):
        if not self.simulation_steps:
            return
        if self.current_step_index < len(self.simulation_steps) - 1:
            self.current_step_index += 1
            self.show_step()

    def prev_step(self):
        if not self.simulation_steps:
            return
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.show_step()

    def auto_play(self):
        if not self.simulation_steps:
            self.generate_simulation()
            if not self.simulation_steps:
                return

        if self.current_step_index < 0:
            self.current_step_index = 0
            self.show_step()

        self.stop_auto_play()
        self._auto_play_loop()

    def _auto_play_loop(self):
        if self.current_step_index < len(self.simulation_steps) - 1:
            self.current_step_index += 1
            self.show_step()
            self.sim_auto_job = self.after(900, self._auto_play_loop)

    def stop_auto_play(self):
        if self.sim_auto_job is not None:
            self.after_cancel(self.sim_auto_job)
            self.sim_auto_job = None

class SearchFileFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self.reader = DocumentReader()
        self.file_path = None

        self.pattern_var = tk.StringVar()
        self.algorithm_var = tk.StringVar(value="Brute Force")
        self.case_sensitive_var = tk.BooleanVar(value=False)
        self.file_name_var = tk.StringVar(value="No file selected")

        self.result_vars = {
            "positions": tk.StringVar(value="[]"),
            "count": tk.StringVar(value="0"),
            "time": tk.StringVar(value="0.000 ms"),
            "comparisons": tk.StringVar(value="0")
        }

        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Search File", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        left_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_card.grid_columnconfigure(0, weight=1)
        
        left_card.grid_rowconfigure(2, weight=1) 

        right_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        right_card.grid(row=1, column=1, sticky="nsew")
        right_card.grid_columnconfigure(0, weight=1)

        ttk.Label(left_card, text="File Name", style="Label.TLabel").grid(row=0, column=0, sticky="w")
        tk.Label(
            left_card,
            textvariable=self.file_name_var,
            bg="#ffffff",
            fg="#111827",
            font=("Cambria", 10, "italic")
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))

        file_text_frame = tk.Frame(left_card, bg="#d1d5db", highlightthickness=0, relief="flat")
        file_text_frame.grid(row=2, column=0, sticky="nsew", pady=(8, 12))
        file_text_frame.grid_columnconfigure(0, weight=1)
        file_text_frame.grid_rowconfigure(0, weight=1)
        
        self.file_text_widget = ScrolledText(
            file_text_frame,
            wrap="word",
            font=("Menlo", 12),
            height=10, 
            bg="#ffffff",
            fg="#111827",
            insertbackground="#10b981",
            selectbackground="#10b981",
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.file_text_widget.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        top_buttons = tk.Frame(left_card, bg="#ffffff")
        top_buttons.grid(row=3, column=0, sticky="w", pady=(0, 8))

        ttk.Button(top_buttons, text="Upload File", command=self.upload_file, style="Simulation.TButton").pack(side="left")
        ttk.Button(top_buttons, text="Clear Highlight", command=self.clear_highlight, style="Clear.TButton").pack(side="left", padx=8)

        search_box = tk.Frame(left_card, bg="#ffffff")
        search_box.grid(row=4, column=0, sticky="ew")
        search_box.grid_columnconfigure(1, weight=1)
        search_box.grid_columnconfigure(1, weight=1)

        ttk.Label(search_box, text="Pattern", style="Label.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(search_box, textvariable=self.pattern_var, font=("Cambria", 11), style="Modern.TEntry").grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(search_box, text="Algorithm", style="Label.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Combobox(
            search_box,
            textvariable=self.algorithm_var,
            state="readonly",
            values=["Brute Force", "Boyer Moore"]
        ).grid(row=1, column=1, sticky="ew", pady=6)

        tk.Checkbutton(
            search_box,
            text="Case sensitive",
            variable=self.case_sensitive_var,
            bg="#ffffff",
            fg="#374151",
            activebackground="#ffffff",
            activeforeground="#374151",
            selectcolor="#10b981",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            font=("Cambria", 10),
            anchor="w"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=6)

        ttk.Button(
            search_box,
            text="Search In File",
            command=self.run_search_in_file,
            style="Search.TButton"
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

        ttk.Label(right_card, text="Results", style="ResultTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))

        self._result_item(right_card, 1, "Found at Positions", self.result_vars["positions"])
        self._result_item(right_card, 2, "Number of Occurrences", self.result_vars["count"])
        self._result_item(right_card, 3, "Processing Time", self.result_vars["time"])
        self._result_item(right_card, 4, "Number of Comparisons", self.result_vars["comparisons"])

   

        note = tk.Label(
            right_card,
            text=(
                "Hỗ trợ file: .txt, .pdf, .docx\n"
                "Nội dung file sẽ được hiển thị ở khung bên trái.\n"
                "Các kết quả tìm thấy sẽ được tô vàng."
            ),
            justify="left",
            bg="#ffffff",
            fg="#374151",
            font=("Cambria", 10)
        )
        note.grid(row=5, column=0, sticky="ew", pady=(18, 0))

        self.file_text_widget.tag_configure("highlight", background="#fde047", foreground="#111827")

    # def _result_item(self, parent, row, label_text, value_var):
    #     container = tk.Frame(parent, bg="#f9fafb", bd=1, relief="solid", highlightthickness=0)
    #     container.grid(row=row, column=0, sticky="ew", pady=6)
    #     container.grid_columnconfigure(0, weight=1)

    #     label = tk.Label(container, text=label_text, bg="#f9fafb", fg="#374151", font=("Cambria", 10, "bold"))
    #     label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

    #     value = tk.Label(container, textvariable=value_var, bg="#f9fafb", fg="#111827", font=("Consolas", 11), justify="left", wraplength=300)
    #     value.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
    def _result_item(self, parent, row, label_text, value_var):
        container = tk.Frame(
            parent, 
            bg="#ffffff", 
            highlightbackground="#e2e8f0", # Viền xám rất nhạt
            highlightthickness=1, 
            relief="flat"
        )
        container.grid(row=row, column=0, sticky="ew", pady=6)
        container.grid_columnconfigure(1, weight=1) 

        accent = tk.Frame(container, bg="#10b981", width=4)
        accent.grid(row=0, column=0, rowspan=2, sticky="ns")

        label = tk.Label(
            container, 
            text=label_text.upper(), 
            bg="#ffffff", 
            fg="#64748b", # Màu Slate-500
            font=("Cambria", 8, "bold")
        )
        label.grid(row=0, column=1, sticky="w", padx=12, pady=(10, 0))

        value = tk.Label(
            container, 
            textvariable=value_var, 
            bg="#ffffff", 
            fg="#0f172a", 
            font=("Cambria Semibold", 11), 
            justify="left", 
            wraplength=350 
        )
        value.grid(row=1, column=1, sticky="w", padx=12, pady=(2, 10))

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file",
            filetypes=[
                ("Supported files", "*.txt *.pdf *.docx *.csv *.xlsx *.py *.js *.ts *.java *.cpp *.c *.html *.css *.json *.xml"),
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx"),
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("TypeScript files", "*.ts"),
                ("C/C++ files", "*.c *.cpp *.h *.hpp"),
                ("Web files", "*.html *.css"),
                ("JSON/XML files", "*.json *.xml"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            content = self.reader.read(file_path)
            self.file_path = file_path
            self.file_name_var.set(os.path.basename(file_path))

            self.file_text_widget.delete("1.0", tk.END)
            self.file_text_widget.insert("1.0", content)

            self.clear_highlight()

            self.result_vars["positions"].set("[]")
            self.result_vars["count"].set("0")
            self.result_vars["time"].set("0.000 ms")
            self.result_vars["comparisons"].set("0")

        except Exception as e:
            messagebox.showerror("Lỗi đọc file", str(e))

    def clear_highlight(self):
        self.file_text_widget.tag_remove("highlight", "1.0", tk.END)

    def run_search_in_file(self):
        text = self.file_text_widget.get("1.0", "end-1c")
        pattern = self.pattern_var.get()
        algorithm = self.algorithm_var.get()

        self.clear_highlight()

        if not text.strip():
            messagebox.showwarning("Chưa có file", "Vui lòng upload file trước.")
            return

        if not pattern:
            messagebox.showwarning("Thiếu pattern", "Vui lòng nhập cụm từ cần tìm.")
            return

        if len(pattern) > len(text):
            self.result_vars["positions"].set("[]")
            self.result_vars["count"].set("0")
            self.result_vars["time"].set("0.000 ms")
            self.result_vars["comparisons"].set("0")
            messagebox.showinfo("Thông báo", "Pattern dài hơn nội dung file nên không có kết quả.")
            return

        case_sensitive = self.case_sensitive_var.get()
        if algorithm == "Brute Force":
            brute_force = BruteForce(text, pattern, case_sensitive=case_sensitive)
            result = brute_force.search()
        else:
            BoyerMoore.initialize(text, pattern, case_sensitive=case_sensitive)
            BoyerMoore.mainloop()
            result = BoyerMoore.RESULT

        self.result_vars["positions"].set(str(result.positions))
        self.result_vars["count"].set(str(len(result.positions)))
        self.result_vars["time"].set(f"{result.elapsed_ms:.3f} ms")
        self.result_vars["comparisons"].set(str(result.comparisons))

        self.highlight_matches(result.positions, len(pattern))

    def highlight_matches(self, positions, pattern_length):
        for pos in positions:
            start_index = f"1.0 + {pos} chars"
            end_index = f"1.0 + {pos + pattern_length} chars"
            self.file_text_widget.tag_add("highlight", start_index, end_index)


def run_bruteforce_benchmark(text: str, pattern: str, case_sensitive: bool = False):
    brute_force = BruteForce(text, pattern, case_sensitive=case_sensitive)
    result = brute_force.search()
    return {
        "positions": result.positions,
        "count": len(result.positions),
        "time_ms": result.elapsed_ms,
        "comparisons": result.comparisons
    }


def run_boyermoore_benchmark(text: str, pattern: str, case_sensitive: bool = False):
    BoyerMoore.initialize(text, pattern, case_sensitive=case_sensitive)
    BoyerMoore.mainloop()
    result = BoyerMoore.RESULT
    return {
        "positions": result.positions,
        "count": len(result.positions),
        "time_ms": result.elapsed_ms,
        "comparisons": result.comparisons
    }
class CheckPerformanceFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.generated_data = []
        self.performance_results = []

        self.case_sensitive_var = tk.BooleanVar(value=False)

        self.text_length_var = tk.StringVar(value="5")
        self.pattern_length_var = tk.StringVar(value="1")
        self.is_random_length_text_var = tk.BooleanVar(value=False)
        self.is_random_length_pattern_var = tk.BooleanVar(value=False)
        self.languages_var = tk.StringVar(value="en,vi,fr")

        self.language_var = tk.StringVar(value="en")

        self.num_records_var = tk.StringVar(value="10")
        self.min_text_length_var = tk.StringVar(value="5")
        self.max_text_length_var = tk.StringVar(value="10")
        self.min_pattern_length_var = tk.StringVar(value="3")
        self.max_pattern_length_var = tk.StringVar(value="5")
        self.allow_pattern_not_in_text_var = tk.BooleanVar(value=True)
        self.seed_var = tk.StringVar(value="42")

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        title = ttk.Label(self, text="Check Performance", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        form_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        form_card.grid_columnconfigure(1, weight=1)

        preview_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        preview_card.grid(row=1, column=1, sticky="nsew")
        # preview_card.grid_columnconfigure(0, weight=1)
        # preview_card.grid_rowconfigure(1, weight=3)
        # preview_card.grid_rowconfigure(2, weight=2)
        preview_card.grid_rowconfigure(1, weight=1) 
        preview_card.grid_rowconfigure(2, weight=0) 
        preview_card.grid_rowconfigure(3, weight=1) 

        ttk.Label(form_card, text="Data Generation Parameters", style="ResultTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        fields = [
            ("Text Length", self.text_length_var),
            ("Pattern Length", self.pattern_length_var),
            # ("Languages (en,vi,fr)", self.languages_var),
            ("Number of Records", self.num_records_var),
            ("Minimum Text Length", self.min_text_length_var),
            ("Maximum Text Length", self.max_text_length_var),
            ("Minimum Pattern Length", self.min_pattern_length_var),
            ("Maximum Pattern Length", self.max_pattern_length_var),
            ("Seed", self.seed_var),
        ]

        row_idx = 1
        for label_text, var in fields:
            ttk.Label(form_card, text=label_text, style="Label.TLabel").grid(
                row=row_idx, column=0, sticky="w", padx=(0, 8), pady=6
            )
            ttk.Entry(form_card, textvariable=var, font=("Cambria", 10), style="Modern.TEntry").grid(
                row=row_idx, column=1, sticky="ew", pady=6
            )

            if row_idx == 2:
                row_idx += 1
                ttk.Label(form_card, text="language", style="Label.TLabel").grid(
                    row=row_idx, column=0, sticky="w", padx=(0, 8), pady=6
                )
                lang_combo = ttk.Combobox(
                    form_card, 
                    textvariable=self.language_var,
                    values= list(TextPatternGenerator.LANGUAGE_CHARSETS.keys()),
                    state="readonly", 
                    font=("Cambria", 10)
                )
                lang_combo.grid(row=row_idx, column=1, sticky="ew", pady=6)

            row_idx += 1

        tk.Checkbutton(
            form_card,
            text="Randomize Text Length",
            variable=self.is_random_length_text_var,
            bg="#ffffff",
            fg="#374151",
            activebackground="#ffffff",
            activeforeground="#374151",
            selectcolor="#10b981",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            font=("Cambria", 10),
            anchor="w"
        ).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=4)
        row_idx += 1

        tk.Checkbutton(
            form_card,
            text="Randomize Pattern Length",
            variable=self.is_random_length_pattern_var,
            bg="#ffffff",
            fg="#374151",
            activebackground="#ffffff",
            activeforeground="#374151",
            selectcolor="#10b981",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            font=("Cambria", 10),
            anchor="w"
        ).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=4)
        row_idx += 1

        tk.Checkbutton(
            form_card,
            text="Allow Pattern Not In Text",
            variable=self.allow_pattern_not_in_text_var,
            bg="#ffffff",
            fg="#374151",
            activebackground="#ffffff",
            activeforeground="#374151",
            selectcolor="#10b981",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            font=("Cambria", 10),
            anchor="w"
        ).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=4)
        row_idx += 1

        tk.Checkbutton(
            form_card,
            text="Case Sensitive",
            variable=self.case_sensitive_var,
            bg="#ffffff",
            fg="#374151",
            activebackground="#ffffff",
            activeforeground="#374151",
            selectcolor="#10b981",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            font=("Cambria", 10),
            anchor="w"
        ).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=4)
        row_idx += 1

        btn_row = tk.Frame(form_card, bg="#ffffff")
        btn_row.grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(12, 0))

        create_modern_button(
            btn_row,
            text="Generate Data",
            command=self.generate_data,
            style="Search.TButton"
        ).pack(side="left")

        create_modern_button(
            btn_row,
            text="Check Performance",
            command=self.check_performance,
            style="Simulation.TButton"
        ).pack(side="left", padx=8)

        ttk.Label(preview_card, text="Generated Data List", style="ResultTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )

        table_container = tk.Frame(preview_card, bg="#ffffff")
        table_container.grid(row=1, column=0, sticky="nsew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        columns = (
            "stt",
            # "language",
            "text",
            "pattern",
            "text_length",
            "pattern_length",
            "pattern_in_text"
        )

        self.preview_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=18,
            style="Custom.Treeview"
        )

        self.preview_tree.heading("stt", text="NO.")
        # self.preview_tree.heading("language", text="Language")
        self.preview_tree.heading("text", text="Text")
        self.preview_tree.heading("pattern", text="Pattern")
        self.preview_tree.heading("text_length", text="Text Length")
        self.preview_tree.heading("pattern_length", text="Pattern Length")
        self.preview_tree.heading("pattern_in_text", text="Pattern In Text")

        self.preview_tree.column("stt", width=50, anchor="center")
        # self.preview_tree.column("language", width=90, anchor="center")
        self.preview_tree.column("text", width=260, anchor="w")
        self.preview_tree.column("pattern", width=140, anchor="w")
        self.preview_tree.column("text_length", width=100, anchor="center")
        self.preview_tree.column("pattern_length", width=110, anchor="center")
        self.preview_tree.column("pattern_in_text", width=120, anchor="center")

        self.preview_tree.tag_configure("oddrow", background="#f9fafb")
        self.preview_tree.tag_configure("evenrow", background="#ffffff")

        scroll_y = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.preview_tree.yview,
            style="Modern.Vertical.TScrollbar"
        )

        scroll_x = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.preview_tree.xview,
            style="Modern.Horizontal.TScrollbar"
        )

        self.preview_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        self.preview_tree.bind("<<TreeviewSelect>>", self.on_preview_select)

        ttk.Label(preview_card, text="Record Details", style="ResultTitle.TLabel").grid(
            row=2, column=0, sticky="w", pady=(12, 4) # Giảm pady dưới để tiết kiệm diện tích
        )

        # self.preview_detail = ScrolledText(
        #     preview_card,
        #     wrap="word",
        #     font=("Consolas", 10),
        #     height=5,
        #     bg="#f9fafb",
        #     fg="#111827",
        #     insertbackground="#10b981",
        #     selectbackground="#10b981",
        #     selectforeground="#ffffff",
        #     relief="flat",
        #     borderwidth=1
        # )
        self.preview_detail = ScrolledText(
            preview_card,
            # wrap="word",
            # font=("Menlo", 12),
            # height=5,
            # bg="#ffffff",            
            # fg="#111827",
            # insertbackground="#10b981",
            # selectbackground="#dcfce7", 
            # selectforeground="#166534", 
            # relief="flat",
            # borderwidth=0,
            # highlightthickness=2,
            # highlightbackground="#d1d5db" 
            wrap="word",
            font=("Menlo", 12),
            height=18,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#10b981",
            selectbackground="#10b981",
            selectforeground="#ffffff",
            
            # Border & Color
            relief="flat",
            highlightthickness=1,                
            highlightbackground="#d1d5db",       
            highlightcolor="#10b981",             
            
            padx=8, 
            pady=5, 
            state="disabled"
        )

        self.preview_detail.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

    def _short_text(self, value, max_len=50):
        if value is None:
            return ""
        value = str(value)
        if len(value) <= max_len:
            return value
        return value[:max_len] + "..."

    def _parse_languages(self):
        # raw = self.languages_var.get().strip()
        # languages = [x.strip() for x in raw.split(",") if x.strip()]
        # if not languages:
        #     raise ValueError("languages không được rỗng.")
        # return languages

        selected_lang = self.language_var.get().strip()
        if not selected_lang:
            return ["en"] # fallback mặc định
        return [selected_lang]

    def _get_generator(self):
        return TextPatternGenerator(
            text_length=int(self.text_length_var.get()),
            pattern_length=int(self.pattern_length_var.get()),
            is_random_length_text=self.is_random_length_text_var.get(),
            is_random_length_pattern=self.is_random_length_pattern_var.get(),
            languages=self._parse_languages(),
            num_records=int(self.num_records_var.get()),
            min_text_length=int(self.min_text_length_var.get()),
            max_text_length=int(self.max_text_length_var.get()),
            min_pattern_length=int(self.min_pattern_length_var.get()),
            max_pattern_length=int(self.max_pattern_length_var.get()),
            allow_pattern_not_in_text=self.allow_pattern_not_in_text_var.get(),
            seed=int(self.seed_var.get()) if self.seed_var.get().strip() else None,
        )

    def generate_data(self):
        try:
            generator = self._get_generator()
            self.generated_data = generator.generate()
            self.performance_results = []

            for item_id in self.preview_tree.get_children():
                self.preview_tree.delete(item_id)

            self.preview_detail.delete("1.0", tk.END)

            for idx, item in enumerate(self.generated_data, start=1):
                row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.preview_tree.insert(
                    "",
                    "end",
                    values=(
                        idx,
                        # item["language"],
                        self._short_text(item["text"], 50),
                        self._short_text(item["pattern"], 20),
                        item["text_length"],
                        item["pattern_length"],
                        item["pattern_in_text"]
                    ),
                    tags=(row_tag,)
                )

            if self.generated_data:
                first_id = self.preview_tree.get_children()[0]
                self.preview_tree.selection_set(first_id)
                self.preview_tree.focus(first_id)
                self.on_preview_select(None)

        except Exception as e:
            messagebox.showerror("Lỗi generate data", str(e))

    def on_preview_select(self, event):
        selected = self.preview_tree.selection()
        if not selected:
            return

        item_id = selected[0]
        values = self.preview_tree.item(item_id, "values")
        stt = int(values[0]) - 1

        if stt < 0 or stt >= len(self.generated_data):
            return

        data = self.generated_data[stt]

        self.preview_detail.config(state="normal")
        self.preview_detail.delete("1.0", tk.END)
        self.preview_detail.insert(
            tk.END,
            (
                # f"language        : {data['language']}\n"
                f"text            : {data['text']}\n"
                f"pattern         : {data['pattern']}\n"
                f"text_length     : {data['text_length']}\n"
                f"pattern_length  : {data['pattern_length']}\n"
                f"pattern_in_text : {data['pattern_in_text']}\n"
            )
        )
        self.preview_detail.config(state="disabled")


    def check_performance(self):
        if not self.generated_data:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng bấm Generate Data trước.")
            return

        try:
            case_sensitive = self.case_sensitive_var.get()
            self.performance_results = []

            for item in self.generated_data:
                text = item["text"]
                pattern = item["pattern"]

                bf = run_bruteforce_benchmark(text, pattern, case_sensitive=case_sensitive)
                bm = run_boyermoore_benchmark(text, pattern, case_sensitive=case_sensitive)

                self.performance_results.append({
                    "language": item["language"],
                    "text": text,
                    "pattern": pattern,
                    "text_length": len(text),
                    "pattern_length": len(pattern),
                    "bruteforce_positions": bf["positions"],
                    "bruteforce_count": bf["count"],
                    "bruteforce_time_ms": bf["time_ms"],
                    "bruteforce_comparisons": bf["comparisons"],
                    "boyermoore_positions": bm["positions"],
                    "boyermoore_count": bm["count"],
                    "boyermoore_time_ms": bm["time_ms"],
                    "boyermoore_comparisons": bm["comparisons"],
                })

            self.show_performance_dialog()

        except Exception as e:
            messagebox.showerror("Lỗi check performance", str(e))

    def show_performance_dialog(self):
        dialog = Toplevel(self)
        dialog.title("Performance Result")
        dialog.geometry("1450x850")
        dialog.configure(bg="#f4f6f8")

        container = ttk.Frame(dialog, style="Main.TFrame", padding=12)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        container.grid_rowconfigure(0, weight=1)

        left_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left_card.grid_columnconfigure(0, weight=1)
        left_card.grid_rowconfigure(1, weight=3)
        left_card.grid_rowconfigure(3, weight=2)

        right_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        right_card.grid(row=0, column=1, sticky="nsew")
        right_card.grid_columnconfigure(0, weight=1)
        right_card.grid_rowconfigure(1, weight=1)

        ttk.Label(left_card, text="Benchmark Results List", style="ResultTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )

        table_frame = tk.Frame(left_card, bg="#ffffff")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "stt",
            # "language",
            "text",
            "pattern",
            "text_length",
            "pattern_length",
            "bf_count",
            "bm_count",
            "bf_time",
            "bm_time",
            "bf_comp",
            "bm_comp"
        )

        perf_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=18,
            style="Custom.Treeview"
        )


        headings = {
            "stt": "NO.",
            # "language": "Language",
            "text": "Text",
            "pattern": "Pattern",
            "text_length": "Text Length",
            "pattern_length": "Pattern Length",
            "bf_count": "BF Count",
            "bm_count": "BM Count",
            "bf_time": "BF Time (ms)",
            "bm_time": "BM Time (ms)",
            "bf_comp": "BF Comparisons",
            "bm_comp": "BM Comparisons",
        }

        for col, title in headings.items():
            perf_tree.heading(col, text=title)

        perf_tree.column("stt", width=50, anchor="center")
        # perf_tree.column("language", width=80, anchor="center")
        perf_tree.column("text", width=220, anchor="w")
        perf_tree.column("pattern", width=120, anchor="w")
        perf_tree.column("text_length", width=90, anchor="center")
        perf_tree.column("pattern_length", width=100, anchor="center")
        perf_tree.column("bf_count", width=80, anchor="center")
        perf_tree.column("bm_count", width=80, anchor="center")
        perf_tree.column("bf_time", width=110, anchor="center")
        perf_tree.column("bm_time", width=110, anchor="center")
        perf_tree.column("bf_comp", width=120, anchor="center")
        perf_tree.column("bm_comp", width=120, anchor="center")

        perf_tree.tag_configure("oddrow", background="#f9fafb")
        perf_tree.tag_configure("evenrow", background="#ffffff")

        perf_scroll_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=perf_tree.yview,
            style="Modern.Vertical.TScrollbar"
        )

        perf_scroll_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=perf_tree.xview,
            style="Modern.Horizontal.TScrollbar"
        )
        
        perf_tree.configure(yscrollcommand=perf_scroll_y.set, xscrollcommand=perf_scroll_x.set)

        perf_tree.grid(row=0, column=0, sticky="nsew")
        perf_scroll_y.grid(row=0, column=1, sticky="ns")
        perf_scroll_x.grid(row=1, column=0, sticky="ew")

        ttk.Label(left_card, text="Record Details", style="ResultTitle.TLabel").grid(
            row=2, column=0, sticky="w", pady=(12, 8)
        )

        detail_text = ScrolledText(
            left_card,
            # wrap="word",
            # font=("Menlo", 12),
            # height=12,
            # bg="#f9fafb",
            # fg="#111827",
            # insertbackground="#10b981",
            # selectbackground="#10b981",
            # selectforeground="#ffffff",
            # relief="flat",
            # # borderwidth=1, 
            # borderwidth=0,
            # highlightthickness=2,
            # highlightbackground="#d1d5db" 
            wrap="word",
            font=("Menlo", 12),
            height=18,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#10b981",
            selectbackground="#10b981",
            selectforeground="#ffffff",
            
            # Border & Color
            relief="flat",
            highlightthickness=1,                
            highlightbackground="#d1d5db",       
            highlightcolor="#10b981",             
            
            padx=8, 
            pady=5, 
            state="disabled"
        )
        detail_text.grid(row=3, column=0, sticky="nsew")

        for idx, item in enumerate(self.performance_results, start=1):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"

            perf_tree.insert(
                "",
                "end",
                values=(
                    idx,
                    # item["language"],
                    self._short_text(item["text"], 40),
                    self._short_text(item["pattern"], 20),
                    item["text_length"],
                    item["pattern_length"],
                    item["bruteforce_count"],
                    item["boyermoore_count"],
                    f"{item['bruteforce_time_ms']:.6f}",
                    f"{item['boyermoore_time_ms']:.6f}",
                    item["bruteforce_comparisons"],
                    item["boyermoore_comparisons"]
                ),
                tags=(row_tag,)
            )

        def on_perf_select(event=None):
            selected = perf_tree.selection()
            if not selected:
                return

            item_id = selected[0]
            values = perf_tree.item(item_id, "values")
            stt = int(values[0]) - 1

            if stt < 0 or stt >= len(self.performance_results):
                return

            data = self.performance_results[stt]
            detail_text.config(state="normal")
            detail_text.delete("1.0", tk.END)
            detail_text.insert(
                tk.END,
                (
                    f"language                : {data['language']}\n"
                    f"text                    : {data['text']}\n"
                    f"pattern                 : {data['pattern']}\n"
                    f"text_length             : {data['text_length']}\n"
                    f"pattern_length          : {data['pattern_length']}\n"
                    f"Brute Force positions   : {data['bruteforce_positions']}\n"
                    f"Brute Force count       : {data['bruteforce_count']}\n"
                    f"Brute Force time (ms)   : {data['bruteforce_time_ms']:.6f}\n"
                    f"Brute Force comparisons : {data['bruteforce_comparisons']}\n"
                    f"Boyer Moore positions   : {data['boyermoore_positions']}\n"
                    f"Boyer Moore count       : {data['boyermoore_count']}\n"
                    f"Boyer Moore time (ms)   : {data['boyermoore_time_ms']:.6f}\n"
                    f"Boyer Moore comparisons : {data['boyermoore_comparisons']}\n"
                )
            )
            detail_text.config(state="disabled")

        perf_tree.bind("<<TreeviewSelect>>", on_perf_select)

        if self.performance_results:
            first_id = perf_tree.get_children()[0]
            perf_tree.selection_set(first_id)
            perf_tree.focus(first_id)
            on_perf_select()

        total_bf_time = sum(x["bruteforce_time_ms"] for x in self.performance_results)
        total_bm_time = sum(x["boyermoore_time_ms"] for x in self.performance_results)
        total_bf_comp = sum(x["bruteforce_comparisons"] for x in self.performance_results)
        total_bm_comp = sum(x["boyermoore_comparisons"] for x in self.performance_results)

        avg_bf_time = total_bf_time / len(self.performance_results) if self.performance_results else 0
        avg_bm_time = total_bm_time / len(self.performance_results) if self.performance_results else 0
        avg_bf_comp = total_bf_comp / len(self.performance_results) if self.performance_results else 0
        avg_bm_comp = total_bm_comp / len(self.performance_results) if self.performance_results else 0

        # summary = tk.Label(
        #     right_card,
        #     text=(
        #         f"Tổng số record: {len(self.performance_results)}\n\n"
        #         f"Tổng thời gian BF: {total_bf_time:.6f} ms\n"
        #         f"Tổng thời gian BM: {total_bm_time:.6f} ms\n\n"
        #         f"TB thời gian BF: {avg_bf_time:.6f} ms\n"
        #         f"TB thời gian BM: {avg_bm_time:.6f} ms\n\n"
        #         f"Tổng so sánh BF: {total_bf_comp}\n"
        #         f"Tổng so sánh BM: {total_bm_comp}\n\n"
        #         f"TB so sánh BF: {avg_bf_comp:.2f}\n"
        #         f"TB so sánh BM: {avg_bm_comp:.2f}"
        #     ),
        #     justify="left",
        #     bg="#ffffff",
        #     fg="#111827",
        #     font=("Cambria", 11)
        # )
        # summary.grid(row=0, column=0, sticky="nw", pady=(0, 16))
        summary_container = tk.Frame(right_card, bg="#ffffff", padx=10, pady=10)
        summary_container.grid(row=0, column=0, sticky="nw", pady=(0, 16))

        def _add_metric_row(parent, row, label, bf_val, bm_val, is_header=False):
            font_label = ("Cambria", 10, "bold") if is_header else ("Cambria", 10)
            font_val = ("Consolas", 10, "bold") if not is_header else ("Cambria", 10, "bold")
            bg = "#f8fafc" if is_header else "#ffffff"
            
            tk.Label(parent, text=label, bg=bg, fg="#64748b", font=font_label, width=20, anchor="w").grid(row=row, column=0, pady=2, padx=5)
            tk.Label(parent, text=bf_val, bg=bg, fg="#ef4444" if not is_header else "#111827", font=font_val, width=15).grid(row=row, column=1, pady=2)
            tk.Label(parent, text=bm_val, bg=bg, fg="#10b981" if not is_header else "#111827", font=font_val, width=15).grid(row=row, column=2, pady=2)

        _add_metric_row(summary_container, 0, "METRICS", "BRUTE FORCE", "BOYER MOORE", is_header=True)

        _add_metric_row(summary_container, 1, "Total Time (ms)", f"{total_bf_time:.4f}", f"{total_bm_time:.4f}")
        _add_metric_row(summary_container, 2, "Average Time (ms)", f"{avg_bf_time:.4f}", f"{avg_bm_time:.4f}")
        _add_metric_row(summary_container, 3, "Total Comparisons", f"{total_bf_comp}", f"{total_bm_comp}")
        _add_metric_row(summary_container, 4, "Average Comparisons", f"{avg_bf_comp:.2f}", f"{avg_bm_comp:.2f}")

        tk.Label(summary_container, text=f"Total Records Processed: {len(self.performance_results)}", 
                bg="#ffffff", fg="#111827", font=("Cambria", 11, "bold")).grid(row=5, column=0, columnspan=3, pady=(15, 0), sticky="w")

        # fig = Figure(figsize=(5.5, 5.0), dpi=100)
        # ax1 = fig.add_subplot(211)
        # ax2 = fig.add_subplot(212)

        # ax1.bar(["Brute Force", "Boyer Moore"], [avg_bf_time, avg_bm_time])
        # ax1.set_title("Average Processing Time (ms)")
        # ax1.set_ylabel("ms")

        # ax2.bar(["Brute Force", "Boyer Moore"], [avg_bf_comp, avg_bm_comp])
        # ax2.set_title("Average Comparisons")
        # ax2.set_ylabel("count")

        # fig.tight_layout()

        # canvas = FigureCanvasTkAgg(fig, master=right_card)
        # canvas.draw()
        # canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        # Thiết lập màu sắc và font chữ
        colors = ["#94a3b8", "#10b981"] # Xám cho BF, Xanh cho BM
        font_settings = {'family': 'sans-serif', 'weight': 'normal', 'size': 10}

        fig = Figure(figsize=(5.5, 5.0), dpi=100, facecolor='#ffffff')
        fig.subplots_adjust(hspace=0.4) # Tạo khoảng cách giữa 2 biểu đồ

        # --- Biểu đồ 1: Time Performance ---
        ax1 = fig.add_subplot(211)
        bars1 = ax1.bar(["Brute Force", "Boyer Moore"], [avg_bf_time, avg_bm_time], color=colors, width=0.6)
        ax1.set_title("Average Processing Time (ms)", pad=15, fontsize=11, fontweight='bold', color='#1e293b')
        ax1.set_ylabel("ms", color='#64748b')

        # --- Biểu đồ 2: Comparison Efficiency ---
        ax2 = fig.add_subplot(212)
        bars2 = ax2.bar(["Brute Force", "Boyer Moore"], [avg_bf_comp, avg_bm_comp], color=colors, width=0.6)
        ax2.set_title("Average Comparisons", pad=15, fontsize=11, fontweight='bold', color='#1e293b')
        ax2.set_ylabel("count", color='#64748b')

        for ax in [ax1, ax2]:
            ax.set_facecolor('#ffffff')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e2e8f0')
            ax.spines['bottom'].set_color('#e2e8f0')
            ax.tick_params(axis='x', colors='#1e293b')
            ax.tick_params(axis='y', colors='#64748b')
            ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#f1f5f9') 
            ax.set_axisbelow(True) 

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=right_card)
        canvas.draw()
        canvas.get_tk_widget().config(bg="#ffffff", highlightthickness=0) 
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(10, 0))

if __name__ == "__main__":
    app = DesktopSearchApp()
    app.mainloop()
