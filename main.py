import tkinter as tk
from tkinter import ttk, messagebox
import json
import hashlib
import itertools
import heapq
import secrets
import re
from pathlib import Path
from datetime import datetime
# ============================================================
# CAMPUS LOST & FOUND MANAGEMENT SYSTEM
# Python | Tkinter | JSON
# Plum, Rose, Lavender and Gold Theme
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"
ITEMS_FILE = DATA_DIR / "items.json"
CLAIMS_FILE = DATA_DIR / "claims.json"
LOCATIONS_FILE = DATA_DIR / "campus_locations.json"
PLUM = "#35234F"
DEEP_PLUM = "#261735"
PLUM_LIGHT = "#513B70"
ROSE = "#E7A9C0"
ROSE_DARK = "#B85F83"
LAVENDER = "#E3CFF2"
LAVENDER_LIGHT = "#F0E2F5"
CREAM = "#FFF4D6"
WHITE = "#FBEFF7"
GOLD = "#E6C66D"
GOLD_LIGHT = "#FFF2BD"
TEXT = "#302638"
MUTED = "#786D80"
GREEN = "#176B3A"
GREEN_LIGHT = "#D9F2E2"
RED = "#A32323"
RED_LIGHT = "#FBE1E1"
AMBER = "#79530B"
AMBER_LIGHT = "#FFF0CC"
BORDER = "#E3D7E8"
BG = "#F3E5F4"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
CATEGORIES = [
    "Electronics", "Documents", "Books",
    "Clothing", "Accessories", "Others"
]
# ============================================================
# STORAGE
# ============================================================
def ensure_storage():
    """Create missing files without overwriting existing records."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in (USERS_FILE, ITEMS_FILE, CLAIMS_FILE):
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
    if not LOCATIONS_FILE.exists():
        LOCATIONS_FILE.write_text(
            json.dumps({"locations": [], "connections": []}, indent=4),
            encoding="utf-8"
        )
def load_records(path):
    ensure_storage()
    try:
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
        if not isinstance(records, list):
            messagebox.showerror(
                "Storage Error",
                f"{path.name} must contain a JSON list."
            )
            return []
        return records
    except (json.JSONDecodeError, OSError) as error:
        messagebox.showerror(
            "Storage Error",
            f"Could not read {path.name}.\n\n{error}"
        )
        return []
def save_records(path, records):
    ensure_storage()
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        messagebox.showerror(
            "Storage Error",
            f"Could not save {path.name}.\n\n{error}"
        )
        return False
# ============================================================
# PASSWORD SECURITY
# ============================================================
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200000
    ).hex()
    return salt, password_hash
def verify_password(password, salt, stored_hash):
    try:
        _, entered_hash = hash_password(password, salt)
        return secrets.compare_digest(entered_hash, stored_hash)
    except (ValueError, TypeError):
        return False
# ============================================================
# APPLICATION
# ============================================================
class CampusLostFoundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Lost & Found | Find What Matters")
        self.root.geometry("1280x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg=BG)
        self.current_user = None
        self.current_screen = None
        self.history = []
        self.screen_frame = None
        self.screen_container = None
        self.page_canvas = None
        self.page_scrollbar = None
        self.page_window = None
        self.setup_styles()
        self.navigate(self.build_home, remember=False)
    # --------------------------------------------------------
    # STYLES AND NAVIGATION
    # ---------------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            rowheight=38,
            fieldbackground=WHITE,
            font=FONT,
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Treeview.Heading",
            background=PLUM,
            foreground=WHITE,
            font=FONT_BOLD,
            padding=(10, 11),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", LAVENDER)],
            foreground=[("selected", DEEP_PLUM)]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", PLUM_LIGHT)],
            foreground=[("active", WHITE)]
        )
        style.configure(
            "TCombobox",
            padding=8,
            font=FONT,
            fieldbackground=WHITE,
            background=WHITE,
            foreground=TEXT,
            arrowcolor=PLUM
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", WHITE)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", LAVENDER)],
            selectforeground=[("readonly", DEEP_PLUM)]
        )
        style.configure(
            "Vertical.TScrollbar",
            background=LAVENDER,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=PLUM,
            width=13
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=LAVENDER,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=PLUM,
            width=13
        )
    def navigate(self, screen_function, remember=True):
        if remember and self.current_screen is not None:
            self.history.append(self.current_screen)
        self.current_screen = screen_function

        # Destroy the complete previous scrolling page, not only its inner frame.
        if self.screen_container is not None:
            self.screen_container.destroy()

        self.screen_container = tk.Frame(self.root, bg=BG)
        self.screen_container.pack(fill="both", expand=True)

        self.page_canvas = tk.Canvas(
            self.screen_container,
            bg=BG,
            highlightthickness=0,
            bd=0
        )
        self.page_scrollbar = ttk.Scrollbar(
            self.screen_container,
            orient="vertical",
            command=self.page_canvas.yview,
            style="Vertical.TScrollbar"
        )
        self.page_canvas.configure(
            yscrollcommand=self.page_scrollbar.set
        )

        self.page_scrollbar.pack(side="right", fill="y")
        self.page_canvas.pack(side="left", fill="both", expand=True)

        self.screen_frame = tk.Frame(self.page_canvas, bg=BG)
        self.page_window = self.page_canvas.create_window(
            (0, 0),
            window=self.screen_frame,
            anchor="nw"
        )

        def update_scroll_region(_event=None):
            if self.page_canvas is not None:
                self.page_canvas.configure(
                    scrollregion=self.page_canvas.bbox("all")
                )

        def fit_page_width(event):
            if self.page_canvas is not None and self.page_window is not None:
                self.page_canvas.itemconfigure(
                    self.page_window, width=event.width
                )

        self.screen_frame.bind("<Configure>", update_scroll_region)
        self.page_canvas.bind("<Configure>", fit_page_width)

        # Windows mouse wheel and keyboard scrolling.
        def mousewheel(event):
            if self.page_canvas is None:
                return
            if getattr(event, "delta", 0):
                self.page_canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )

        def linux_scroll_up(event):
            if self.page_canvas is not None:
                self.page_canvas.yview_scroll(-1, "units")

        def linux_scroll_down(event):
            if self.page_canvas is not None:
                self.page_canvas.yview_scroll(1, "units")

        self.page_canvas.bind_all("<MouseWheel>", mousewheel)
        self.page_canvas.bind_all("<Button-4>", linux_scroll_up)
        self.page_canvas.bind_all("<Button-5>", linux_scroll_down)
        self.page_canvas.bind_all(
            "<Prior>",
            lambda event: self.page_canvas.yview_scroll(-1, "pages")
            if self.page_canvas is not None else None
        )
        self.page_canvas.bind_all(
            "<Next>",
            lambda event: self.page_canvas.yview_scroll(1, "pages")
            if self.page_canvas is not None else None
        )
        self.page_canvas.bind_all(
            "<Home>",
            lambda event: self.page_canvas.yview_moveto(0)
            if self.page_canvas is not None else None
        )
        self.page_canvas.bind_all(
            "<End>",
            lambda event: self.page_canvas.yview_moveto(1)
            if self.page_canvas is not None else None
        )

        screen_function()
        self.root.after_idle(update_scroll_region)
    def go_back(self):
        if self.history:
            previous_screen = self.history.pop()
            self.navigate(previous_screen, remember=False)
        elif self.current_user:
            if self.is_admin():
                self.navigate(self.build_admin_dashboard, remember=False)
            else:
                self.navigate(self.build_dashboard, remember=False)
        else:
            self.navigate(self.build_home, remember=False)
    def go_home(self):
        self.current_user = None
        self.history.clear()
        self.navigate(self.build_home, remember=False)
    def logout(self):
        self.current_user = None
        self.history.clear()
        self.navigate(self.build_home, remember=False)
    def make_button(self, parent, text, command, primary=True, width=None):
        """Consistent rounded-looking, high-contrast rose/lilac/gold action button."""
        label = str(text).strip().lower()
        if any(word in label for word in ("delete", "reject", "remove")):
            background, foreground = "#B84D68", WHITE
            active_background, active_foreground = "#963B55", WHITE
        elif any(word in label for word in ("approve", "accept", "save", "submit", "report", "sign in", "create")):
            background, foreground = PLUM, WHITE
            active_background, active_foreground = ROSE_DARK, WHITE
        elif any(word in label for word in ("log out", "logout", "back", "cancel")):
            background, foreground = GOLD_LIGHT, PLUM
            active_background, active_foreground = GOLD, DEEP_PLUM
        elif primary:
            background, foreground = ROSE_DARK, WHITE
            active_background, active_foreground = PLUM_LIGHT, WHITE
        else:
            background, foreground = LAVENDER, PLUM
            active_background, active_foreground = ROSE, DEEP_PLUM

        button = tk.Button(
            parent, text=text, command=command, font=FONT_BOLD,
            bg=background, fg=foreground,
            activebackground=active_background,
            activeforeground=active_foreground,
            relief="flat", bd=0, padx=18, pady=10,
            cursor="hand2", highlightthickness=1,
            highlightbackground=background, highlightcolor=GOLD,
            takefocus=True
        )
        if width:
            button.configure(width=width)
        button.bind("<Enter>", lambda _e: button.configure(bg=active_background))
        button.bind("<Leave>", lambda _e: button.configure(bg=background))
        return button
    def create_header(self, parent, title, subtitle=""):
        header = tk.Frame(parent, bg=DEEP_PLUM, padx=30, pady=18)
        header.pack(fill="x")
        # Rose-gold accent line gives every page a consistent visual identity.
        tk.Frame(header, bg=GOLD, height=3).pack(fill="x", side="top", pady=(0, 14))
        top = tk.Frame(header, bg=DEEP_PLUM)
        top.pack(fill="x")
        if self.current_screen != self.build_home:
            self.make_button(
                top, "←  Back", self.go_back, primary=False
            ).pack(side="left", padx=(0, 15))
        title_area = tk.Frame(top, bg=DEEP_PLUM)
        title_area.pack(side="left", fill="x", expand=True)
        tk.Label(
            title_area, text=title,
            font=("Georgia", 21, "bold"),
            bg=DEEP_PLUM, fg=WHITE
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                header, text=subtitle,
                font=("Segoe UI", 10),
                bg=DEEP_PLUM, fg="#E9DDEC",
                wraplength=1050, justify="left"
            ).pack(anchor="w", pady=(7, 0))
        return header
    def create_entry(self, parent, label, show=None):
        tk.Label(
            parent, text=label, font=FONT_BOLD,
            bg=WHITE, fg=PLUM
        ).pack(anchor="w", pady=(10, 4))

        # Password fields include a visible eye control to toggle masking.
        field_bg = "#FFF9E8" if show else "#FFF5FA"
        if show:
            field = tk.Frame(parent, bg=WHITE)
            field.pack(fill="x")
            entry = tk.Entry(
                field, font=FONT, relief="flat", bd=0,
                bg=field_bg, fg=TEXT, insertbackground=PLUM,
                show=show, highlightthickness=1,
                highlightbackground=BORDER, highlightcolor=ROSE
            )
            entry.pack(side="left", fill="x", expand=True, ipady=9)
            visible = {"value": False}
            eye = tk.Button(
                field, text="◉", font=("Segoe UI Symbol", 12, "bold"),
                bg=LAVENDER, fg=PLUM, activebackground=ROSE,
                activeforeground=PLUM, relief="flat", bd=0,
                padx=12, cursor="hand2", takefocus=True,
                command=lambda: None
            )
            def toggle_password():
                visible["value"] = not visible["value"]
                entry.configure(show="" if visible["value"] else "*")
                eye.configure(text="◎" if visible["value"] else "◉",
                              bg=GOLD_LIGHT if visible["value"] else LAVENDER)
            eye.configure(command=toggle_password)
            eye.pack(side="right", fill="y", padx=(5, 0))
            eye.bind("<Enter>", lambda _e: eye.configure(bg=ROSE))
            eye.bind("<Leave>", lambda _e: eye.configure(
                bg=GOLD_LIGHT if visible["value"] else LAVENDER))
        else:
            entry = tk.Entry(
                parent, font=FONT, relief="flat", bd=0,
                bg=field_bg, fg=TEXT, insertbackground=PLUM,
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ROSE
            )
            entry.pack(fill="x", ipady=9)
        return entry
    def create_labeled_text(self, parent, label, height=4):
        tk.Label(
            parent,
            text=label,
            font=FONT_BOLD,
            bg=BG,
            fg=PLUM
        ).pack(anchor="w", pady=(10, 4))
        text_box = tk.Text(
            parent,
            height=height,
            font=FONT,
            wrap="word",
            relief="flat",
            bd=0,
            bg=WHITE,
            fg=TEXT,
            insertbackground=PLUM,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ROSE
        )
        text_box.pack(fill="x")
        return text_box
    def next_id(self, records, prefix):
        highest = 0
        for record in records:
            record_id = str(
                record.get("id", record.get("item_id", ""))
            ).strip()
            if record_id.startswith(prefix):
                number = record_id[len(prefix):]
                if number.isdigit():
                    highest = max(highest, int(number))
        return f"{prefix}{highest + 1:03d}"
    def page_content(self, padding=25):
        content = tk.Frame(
            self.screen_frame, bg=BG, padx=padding, pady=padding
        )
        content.pack(fill="both", expand=True)
        return content
    def make_card(self, parent, padding=18):
        """Create a premium themed card with a rotating rose/lilac/gold accent."""
        card = tk.Frame(
            parent,
            bg=WHITE,
            padx=padding,
            pady=padding,
            highlightbackground="#DCCDDD",
            highlightthickness=1,
            bd=0
        )
        # A slim colour ribbon gives dashboards, forms, and management panels
        # a consistent visual identity without changing their functionality.
        accents = (PLUM, ROSE_DARK, GOLD, PLUM_LIGHT, ROSE)
        if not hasattr(self, "_card_accent_index"):
            self._card_accent_index = 0
        accent = accents[self._card_accent_index % len(accents)]
        self._card_accent_index += 1
        ribbon = tk.Frame(card, bg=accent, height=4)
        ribbon.pack(fill="x", pady=(0, 12))
        ribbon.pack_propagate(False)
        return card
    def is_admin(self):
        return (
            self.current_user is not None
            and str(self.current_user.get("role", "")).upper() == "ADMIN"
        )
    def is_student(self):
        return (
            self.current_user is not None
            and str(self.current_user.get("role", "")).upper() == "STUDENT"
        )
    def item_id(self, item):
        return str(item.get("id", item.get("item_id", ""))).strip()
    def item_name(self, item):
        return item.get("name", item.get("item_name", ""))
    def item_date(self, item):
        return item.get("date", item.get("item_date", ""))
    def review_status(self, item):
        # Older reports remain compatible with the original app.
        return str(item.get("review_status", "APPROVED")).upper()
    # --------------------------------------------------------
    # HOME PAGE
    # --------------------------------------------------------
    def build_home(self):
        self.screen_frame.configure(bg=CREAM)

        # Hero banner: dark plum, rose-gold details, and a clear first action.
        hero = tk.Frame(self.screen_frame, bg=DEEP_PLUM, padx=38, pady=24)
        hero.pack(fill="x")
        tk.Frame(hero, bg=GOLD, height=3).pack(fill="x", pady=(0, 20))
        hero_body = tk.Frame(hero, bg=DEEP_PLUM)
        hero_body.pack(fill="x")
        left = tk.Frame(hero_body, bg=DEEP_PLUM)
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))
        tk.Label(
            left, text="✦  CAMPUS COMMUNITY", font=("Segoe UI", 10, "bold"),
            bg=DEEP_PLUM, fg=ROSE
        ).pack(anchor="w", pady=(0, 8))
        tk.Label(
            left, text="Lost & Found", font=("Georgia", 36, "bold"),
            bg=DEEP_PLUM, fg=WHITE
        ).pack(anchor="w")
        tk.Label(
            left, text="A little care goes a long way.",
            font=("Georgia", 15, "italic"), bg=DEEP_PLUM, fg=GOLD
        ).pack(anchor="w", pady=(4, 10))
        tk.Label(
            left,
            text="A thoughtful, simple way to report, discover and reunite\n"
                 "belongings with the people who matter.",
            font=("Segoe UI", 11), bg=DEEP_PLUM, fg="#E9DDEC",
            justify="left"
        ).pack(anchor="w")

        right = tk.Frame(
            hero_body, bg=PLUM, padx=23, pady=19,
            highlightbackground="#6D557D", highlightthickness=1
        )
        right.pack(side="right", fill="y", padx=(8, 0))
        tk.Label(
            right, text="✧", font=("Georgia", 30),
            bg=PLUM, fg=GOLD
        ).pack(anchor="center")
        tk.Label(
            right, text="LOST SOMETHING?", font=("Segoe UI", 10, "bold"),
            bg=PLUM, fg=WHITE
        ).pack(anchor="center", pady=(3, 4))
        tk.Label(
            right, text="Found something?\nHelp it find its way home.",
            font=("Segoe UI", 9), bg=PLUM, fg="#E9DDEC",
            justify="center"
        ).pack(anchor="center")

        content = tk.Frame(self.screen_frame, bg=CREAM, padx=36, pady=20)
        content.pack(fill="both", expand=True)
        intro = tk.Frame(content, bg=CREAM)
        intro.pack(fill="x", pady=(0, 15))
        tk.Label(
            intro, text="Welcome to your campus community",
            font=("Georgia", 21, "bold"), bg=CREAM, fg=PLUM
        ).pack(anchor="w")
        tk.Label(
            intro, text="Choose your space to get started.",
            font=("Segoe UI", 10), bg=CREAM, fg=MUTED
        ).pack(anchor="w", pady=(4, 0))

        cards = tk.Frame(content, bg=CREAM)
        cards.pack(fill="x")
        self.home_card(
            cards, "01", "Student Login",
            "Sign in to report lost or found items, search listings and follow your claims.",
            "Sign in to account  →", self.open_student_login, PLUM,
            symbol="↗"
        ).pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.home_card(
            cards, "02", "New Student",
            "Create your campus account and help belongings find their way back home.",
            "Create an account  →", self.open_registration, ROSE_DARK,
            symbol="✦"
        ).pack(side="left", fill="both", expand=True, padx=5)
        self.home_card(
            cards, "03", "Administrator",
            "Review reports, manage ownership claims and keep the system organised.",
            "Administrator login  →", self.open_admin_login, PLUM_LIGHT,
            symbol="⌘"
        ).pack(side="left", fill="both", expand=True, padx=(10, 0))

        # A slim three-step guide adds useful visual structure without fake data.
        guide = tk.Frame(content, bg=LAVENDER_LIGHT, padx=18, pady=12,
                         highlightbackground=BORDER, highlightthickness=1)
        guide.pack(fill="x", pady=(17, 0))
        tk.Label(
            guide, text="HOW IT WORKS", font=("Segoe UI", 9, "bold"),
            bg=LAVENDER_LIGHT, fg=ROSE_DARK
        ).pack(anchor="w", pady=(0, 8))
        steps = tk.Frame(guide, bg=LAVENDER_LIGHT)
        steps.pack(fill="x")
        for number, title, detail in [
            ("01", "Report", "Share the item details"),
            ("02", "Reconnect", "Search campus listings"),
            ("03", "Recover", "Track your claim")
        ]:
            step = tk.Frame(steps, bg=LAVENDER_LIGHT)
            step.pack(side="left", fill="x", expand=True, padx=(0, 8))
            tk.Label(step, text=number, font=("Georgia", 15, "bold"),
                     bg=LAVENDER_LIGHT, fg=ROSE_DARK).pack(side="left", padx=(0, 9))
            labels = tk.Frame(step, bg=LAVENDER_LIGHT)
            labels.pack(side="left", anchor="w")
            tk.Label(labels, text=title, font=("Segoe UI", 10, "bold"),
                     bg=LAVENDER_LIGHT, fg=PLUM).pack(anchor="w")
            tk.Label(labels, text=detail, font=("Segoe UI", 9),
                     bg=LAVENDER_LIGHT, fg=MUTED).pack(anchor="w")
        tk.Label(
            content, text="CAMPUS LOST & FOUND  ·  REPORT  ·  RECONNECT  ·  RECOVER",
            font=("Segoe UI", 8, "bold"), bg=CREAM, fg=ROSE_DARK
        ).pack(anchor="center", pady=(13, 0))

    def home_card(
        self, parent, number, title, description,
        button_text, command, accent, symbol="✦"
    ):
        card = tk.Frame(
            parent, bg=WHITE, padx=19, pady=17,
            highlightbackground="#DCCDDD", highlightthickness=1
        )
        tk.Frame(card, bg=accent, height=4).pack(fill="x", pady=(0, 13))
        top = tk.Frame(card, bg=WHITE)
        top.pack(fill="x")
        tk.Label(
            top, text=number, font=("Georgia", 18, "bold"),
            bg=WHITE, fg=accent
        ).pack(side="left", anchor="w")
        tk.Label(
            top, text=symbol, font=("Segoe UI", 19, "bold"),
            bg=WHITE, fg=GOLD
        ).pack(side="right", anchor="e")
        tk.Label(
            card, text=title, font=("Segoe UI", 14, "bold"),
            bg=WHITE, fg=PLUM
        ).pack(anchor="w", pady=(9, 0))
        tk.Label(
            card, text=description, font=("Segoe UI", 9),
            bg=WHITE, fg=MUTED, wraplength=300,
            justify="left", height=4, anchor="nw"
        ).pack(fill="x", pady=(8, 13))
        self.make_button(card, button_text, command).pack(fill="x", side="bottom")
        def on_enter(_event):
            card.configure(highlightbackground=accent, highlightthickness=2)
        def on_leave(_event):
            card.configure(highlightbackground="#DCCDDD", highlightthickness=1)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for child in card.winfo_children():
            child.bind("<Enter>", on_enter, add="+")
            child.bind("<Leave>", on_leave, add="+")
        return card
    # --------------------------------------------------------
    # STUDENT REGISTRATION
    # --------------------------------------------------------
    def open_registration(self):
        self.navigate(self.build_registration)
    def build_registration(self):
        self.create_header(
            self.screen_frame,
            "Create Student Account",
            "Register once to access campus lost and found."
        )
        page = self.page_content(24)
        page.configure(bg=BG)

        center = tk.Frame(page, bg=BG)
        center.pack(fill="both", expand=True)

        form = self.make_card(center, 30)
        form.configure(bg=WHITE, highlightbackground=ROSE, highlightthickness=2)
        form.pack(fill="y", expand=False, padx=120, pady=8, anchor="n")

        tk.Label(
            form, text="Begin with a fresh start",
            font=("Georgia", 23, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w", pady=(0, 5))
        tk.Label(
            form,
            text="Create your student account to report items and reconnect belongings with their owners.",
            font=("Segoe UI", 10), bg=WHITE, fg=MUTED,
            wraplength=620, justify="left"
        ).pack(anchor="w", pady=(0, 12))

        name_entry = self.create_entry(form, "Full Name")
        email_entry = self.create_entry(form, "Email Address")
        password_entry = self.create_entry(form, "Password", show="*")
        confirm_entry = self.create_entry(form, "Confirm Password", show="*")

        tk.Label(
            form,
            text="Use a valid email and a password of at least 8 characters.",
            font=("Segoe UI", 9), bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(10, 15))

        def register():
            name = name_entry.get().strip()
            email = email_entry.get().strip().lower()
            password = password_entry.get()
            confirm = confirm_entry.get()
            if not all((name, email, password, confirm)):
                messagebox.showwarning(
                    "Missing Information", "Please fill in every field.",
                    parent=self.root
                )
                return
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                messagebox.showwarning(
                    "Invalid Email", "Please enter a valid email address.",
                    parent=self.root
                )
                return
            if len(password) < 8:
                messagebox.showwarning(
                    "Weak Password",
                    "Your password must contain at least 8 characters.",
                    parent=self.root
                )
                return
            if password != confirm:
                messagebox.showwarning(
                    "Password Mismatch", "The passwords do not match.",
                    parent=self.root
                )
                return
            users = load_records(USERS_FILE)
            if any(
                str(user.get("email", "")).strip().lower() == email
                for user in users
            ):
                messagebox.showerror(
                    "Account Exists",
                    "An account with this email already exists.",
                    parent=self.root
                )
                return
            salt, password_hash = hash_password(password)
            users.append({
                "id": self.next_id(users, "U"),
                "name": name,
                "email": email,
                "salt": salt,
                "password_hash": password_hash,
                "role": "STUDENT",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            if save_records(USERS_FILE, users):
                messagebox.showinfo(
                    "Registration Successful",
                    "Your account has been created. You can now log in.",
                    parent=self.root
                )
                self.navigate(self.build_student_login)

        self.make_button(
            form, "Create Account", register
        ).pack(fill="x", pady=(5, 10))
        self.make_button(
            form, "Back to Home", self.go_home, primary=False
        ).pack(fill="x")
    # --------------------------------------------------------
    # STUDENT LOGIN
    # --------------------------------------------------------
    def open_student_login(self):
        self.navigate(self.build_student_login)
    def build_student_login(self):
        self.create_header(
            self.screen_frame,
            "Student Login",
            "Welcome back. Sign in to continue."
        )
        page = self.page_content(24)
        center = tk.Frame(page, bg=BG)
        center.pack(fill="both", expand=True)

        form = self.make_card(center, 32)
        form.configure(bg=WHITE, highlightbackground=ROSE, highlightthickness=2)
        form.pack(fill="y", expand=False, padx=150, pady=20, anchor="n")

        tk.Label(
            form, text="Welcome back",
            font=("Georgia", 25, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w", pady=(0, 5))
        tk.Label(
            form,
            text="Sign in to search campus listings, report items and follow ownership claims.",
            font=("Segoe UI", 10), bg=WHITE, fg=MUTED,
            wraplength=600, justify="left"
        ).pack(anchor="w", pady=(0, 14))

        email_entry = self.create_entry(form, "Email Address")
        password_entry = self.create_entry(form, "Password", show="*")

        def login():
            email = email_entry.get().strip().lower()
            password = password_entry.get()
            if not email or not password:
                messagebox.showwarning(
                    "Missing Information", "Enter your email and password.",
                    parent=self.root
                )
                return
            for user in load_records(USERS_FILE):
                if (
                    str(user.get("email", "")).strip().lower() == email
                    and str(user.get("role", "")).upper() == "STUDENT"
                    and verify_password(
                        password,
                        user.get("salt", ""),
                        user.get("password_hash", "")
                    )
                ):
                    self.current_user = user
                    self.history.clear()
                    self.navigate(self.build_dashboard, remember=False)
                    return
            messagebox.showerror(
                "Login Failed", "Incorrect email or password.",
                parent=self.root
            )

        self.make_button(
            form, "Sign In", login
        ).pack(fill="x", pady=(22, 10))
        self.make_button(
            form, "Register New Account",
            self.open_registration, primary=False
        ).pack(fill="x")
        password_entry.bind("<Return>", lambda event: login())
    # --------------------------------------------------------
    # STUDENT DASHBOARD STATISTICS
    # --------------------------------------------------------
    def get_dashboard_stats(self):
        items = load_records(ITEMS_FILE)
        claims = load_records(CLAIMS_FILE)
        users = load_records(USERS_FILE)
        email = str(
            self.current_user.get("email", "")
        ).strip().casefold() if self.current_user else ""
        visible_items = [
            item for item in items
            if self.review_status(item) == "APPROVED"
        ]
        my_claims = [
            claim for claim in claims
            if str(claim.get("claimant_email", "")).strip().casefold() == email
        ]
        return {
            "total_items": len(visible_items),
            "lost_items": sum(
                1 for item in visible_items
                if str(item.get("status", "")).upper() == "LOST"
            ),
            "found_items": sum(
                1 for item in visible_items
                if str(item.get("status", "")).upper() == "FOUND"
            ),
            "my_claims": len(my_claims),
            "pending_claims": sum(
                1 for claim in my_claims
                if str(claim.get("status", "PENDING")).upper() == "PENDING"
            ),
            "approved_claims": sum(
                1 for claim in my_claims
                if str(claim.get("status", "")).upper()
                in ("APPROVED", "ACCEPTED")
            ),
            "rejected_claims": sum(
                1 for claim in my_claims
                if str(claim.get("status", "")).upper()
                in ("REJECTED", "DECLINED")
            ),
            "registered_students": sum(
                1 for user in users
                if str(user.get("role", "")).upper() == "STUDENT"
            )
        }
    # --------------------------------------------------------
    # STUDENT DASHBOARD
    # --------------------------------------------------------
    def open_student_dashboard(self):
        self.history.clear()
        self.navigate(self.build_dashboard, remember=False)
    def build_dashboard(self):
        if not self.is_student():
            self.navigate(self.build_home, remember=False)
            return
        self.create_header(
            self.screen_frame,
            "Your Student Dashboard",
            f"Welcome back, {self.current_user.get('name', 'Student')} "
            "— everything you need, in one place."
        )
        content = self.page_content(22)

        dashboard_toolbar = tk.Frame(content, bg=BG)
        dashboard_toolbar.pack(fill="x", pady=(0, 12))
        self.make_button(
            dashboard_toolbar, "Log Out", self.logout, primary=False
        ).pack(side="right")

        heading = tk.Frame(content, bg=BG)
        heading.pack(fill="x", pady=(0, 15))
        tk.Label(
            heading, text="Your Campus, Your Belongings",
            font=("Georgia", 22, "bold"), bg=BG, fg=PLUM
        ).pack(anchor="w")
        tk.Label(
            heading, text="Small details help bring lost belongings home.",
            font=FONT_SUBTITLE, bg=BG, fg=MUTED
        ).pack(anchor="w", pady=(5, 0))
        stats_frame = tk.Frame(content, bg=BG)
        stats_frame.pack(fill="x", pady=(0, 16))
        for title, key, accent in [
            ("Total Items", "total_items", PLUM),
            ("Lost Items", "lost_items", ROSE_DARK),
            ("Found Items", "found_items", GREEN),
            ("My Claims", "my_claims", PLUM_LIGHT)
        ]:
            self.stat_card(
                stats_frame, title, key, accent
            ).pack(side="left", fill="x", expand=True, padx=4)
        middle = tk.Frame(content, bg=BG)
        middle.pack(fill="both", expand=True)
        actions_card = self.make_card(middle, 17)
        actions_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(
            actions_card, text="Quick Actions",
            font=("Segoe UI", 15, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w")
        tk.Label(
            actions_card, text="What would you like to do today?",
            font=("Segoe UI", 9), bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(4, 12))
        for text, command in [
            ("＋  Report Lost Item", lambda: self.report_item("LOST")),
            ("✧  Report Found Item", lambda: self.report_item("FOUND")),
            ("⌕  Search Campus Items", self.search_items),
            ("♡  View My Claims", self.my_claims),
            ("⌖  Campus Locations & Shortest Route", self.open_campus_locations)
        ]:
            self.make_button(
                actions_card, text, command
            ).pack(fill="x", pady=4)
        charts_card = self.make_card(middle, 15)
        charts_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(
            charts_card, text="Campus Item Overview",
            font=("Segoe UI", 15, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w")
        tk.Label(
            charts_card, text="Approved item records only",
            font=("Segoe UI", 9), bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(4, 4))
        self.draw_item_chart(charts_card)
        claim_summary = self.make_card(content, 14)
        claim_summary.pack(fill="x", pady=(14, 0))
        stats = self.get_dashboard_stats()
        tk.Label(
            claim_summary, text="Your Claim Summary",
            font=("Segoe UI", 13, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w")
        claim_line = tk.Frame(claim_summary, bg=WHITE)
        claim_line.pack(fill="x", pady=(10, 0))
        for title, key, accent in [
            ("Pending", "pending_claims", GOLD),
            ("Approved", "approved_claims", GREEN),
            ("Rejected", "rejected_claims", RED)
        ]:
            self.small_summary(
                claim_line, title, stats[key], accent
            ).pack(side="left", expand=True, fill="x")
        bottom = tk.Frame(content, bg=BG)
        bottom.pack(fill="x", pady=(13, 0))
        self.make_button(
            bottom, "Logout", self.logout, primary=False
        ).pack(side="left")
        self.make_button(
            bottom, "Refresh Statistics", self.open_student_dashboard
        ).pack(side="right")
    def stat_card(self, parent, title, stat_type, accent):
        card = tk.Frame(
            parent, bg=WHITE, padx=13, pady=13,
            highlightbackground=BORDER, highlightthickness=1
        )
        tk.Frame(
            card, bg=accent, height=3
        ).pack(fill="x", pady=(0, 10))
        value = self.get_dashboard_stats().get(stat_type, 0)
        tk.Label(
            card, text=str(value),
            font=("Segoe UI", 24, "bold"), bg=WHITE, fg=accent
        ).pack(anchor="w")
        tk.Label(
            card, text=title,
            font=("Segoe UI", 9, "bold"), bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(3, 0))
        return card
    def small_summary(self, parent, title, value, accent):
        frame = tk.Frame(parent, bg=WHITE, padx=8)
        tk.Label(
            frame, text=str(value),
            font=("Segoe UI", 18, "bold"), bg=WHITE, fg=accent
        ).pack(anchor="w")
        tk.Label(
            frame, text=title,
            font=("Segoe UI", 9), bg=WHITE, fg=MUTED
        ).pack(anchor="w")
        return frame
    def draw_donut(self, parent, values, center_label, center_value):
        canvas = tk.Canvas(
            parent, height=175, bg=WHITE, highlightthickness=0
        )
        canvas.pack(fill="x", pady=5)
        total = sum(value for _, value, _ in values)
        if total == 0:
            canvas.create_oval(
                45, 18, 155, 128, outline=BORDER, width=15
            )
            canvas.create_text(
                100, 62, text="No data",
                fill=PLUM, font=("Segoe UI", 12, "bold")
            )
            canvas.create_text(
                100, 84, text="yet", fill=MUTED, font=FONT
            )
            tk.Label(
                parent, text="Statistics will appear when records are saved.",
                font=("Segoe UI", 9), bg=WHITE, fg=MUTED,
                wraplength=320, justify="left"
            ).pack(anchor="w")
            return
        start = 90
        for label, value, color in values:
            if value <= 0:
                continue
            extent = value / total * 360
            canvas.create_arc(
                45, 12, 155, 122,
                start=start, extent=extent,
                style="arc", outline=color, width=17
            )
            start += extent
        canvas.create_text(
            100, 57, text=str(center_value),
            fill=PLUM, font=("Segoe UI", 22, "bold")
        )
        canvas.create_text(
            100, 82, text=center_label,
            fill=MUTED, font=("Segoe UI", 9)
        )
        for label, value, color in values:
            row = tk.Frame(parent, bg=WHITE)
            row.pack(anchor="w", pady=2)
            tk.Label(
                row, text="●", fg=color, bg=WHITE
            ).pack(side="left", padx=(0, 6))
            tk.Label(
                row, text=f"{label}: {value}",
                font=("Segoe UI", 9), fg=TEXT, bg=WHITE
            ).pack(side="left")
    def draw_item_chart(self, parent):
        items = [
            item for item in load_records(ITEMS_FILE)
            if self.review_status(item) == "APPROVED"
        ]
        lost = sum(
            1 for item in items
            if str(item.get("status", "")).upper() == "LOST"
        )
        found = sum(
            1 for item in items
            if str(item.get("status", "")).upper() == "FOUND"
        )
        self.draw_donut(
            parent,
            [("Lost", lost, ROSE_DARK), ("Found", found, GREEN)],
            "items", lost + found
        )
    # --------------------------------------------------------
    # REPORT LOST OR FOUND ITEM
    # --------------------------------------------------------
    def report_item(self, item_status):
        if not self.is_student():
            return
        self.navigate(lambda: self.build_report_item(item_status))
    def build_report_item(self, item_status):
        self.create_header(
            self.screen_frame,
            f"Report {item_status.title()} Item",
            "Provide accurate details to help identify the item."
        )
        form = self.page_content(28)
        name_entry = self.create_entry(form, "Item Name")
        tk.Label(
            form, text="Category", font=FONT_BOLD, bg=BG, fg=PLUM
        ).pack(anchor="w", pady=(10, 4))
        category_var = tk.StringVar(value="Electronics")
        ttk.Combobox(
            form, textvariable=category_var, values=CATEGORIES,
            state="readonly", font=FONT
        ).pack(fill="x", ipady=5)
        location_entry = self.create_entry(
            form, "Location Where Item Was Lost/Found"
        )
        date_entry = self.create_entry(form, "Date (YYYY-MM-DD)")
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        description_box = self.create_labeled_text(
            form, "Description / Identifying Features", 4
        )
        def submit():
            name = name_entry.get().strip()
            category = category_var.get().strip()
            location = location_entry.get().strip()
            item_date = date_entry.get().strip()
            description = description_box.get("1.0", "end").strip()
            if not all((name, category, location, item_date)):
                messagebox.showwarning(
                    "Missing Information",
                    "Complete the item name, category, location and date.",
                    parent=self.root
                )
                return
            try:
                datetime.strptime(item_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date", "Enter the date in YYYY-MM-DD format.",
                    parent=self.root
                )
                return
            if len(description) < 5:
                messagebox.showwarning(
                    "Description Required",
                    "Provide at least 5 characters describing the item.",
                    parent=self.root
                )
                return
            items = load_records(ITEMS_FILE)
            new_item = {
                "id": self.next_id(items, "I"),
                "name": name,
                "category": category,
                "location": location,
                "date": item_date,
                "description": description,
                "status": item_status,
                "review_status": "PENDING",
                "reported_by": self.current_user.get("email"),
                "reporter_name": self.current_user.get("name"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            items.append(new_item)
            if save_records(ITEMS_FILE, items):
                messagebox.showinfo(
                    "Report Submitted",
                    f"{item_status.title()} item submitted for admin review.\n"
                    f"Item ID: {new_item['id']}\n"
                    "It will appear in student search after approval.",
                    parent=self.root
                )
                self.open_student_dashboard()
        self.make_button(
            form, "Submit Report", submit
        ).pack(fill="x", pady=(15, 8))
        self.make_button(
            form, "Cancel / Back", self.go_back, primary=False
        ).pack(fill="x")
    # --------------------------------------------------------
    # SEARCH ALGORITHM HELPERS
    # --------------------------------------------------------
    @staticmethod
    def _kmp_lps(pattern):
        """Build the KMP longest-prefix-suffix table in O(m) time."""
        lps = [0] * len(pattern)
        length = 0
        index = 1
        while index < len(pattern):
            if pattern[index] == pattern[length]:
                length += 1
                lps[index] = length
                index += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[index] = 0
                index += 1
        return lps

    @classmethod
    def kmp_contains(cls, text, pattern):
        """Return whether pattern occurs in text using KMP in O(n + m)."""
        if pattern == "":
            return True
        lps = cls._kmp_lps(pattern)
        text_index = pattern_index = 0
        while text_index < len(text):
            if text[text_index] == pattern[pattern_index]:
                text_index += 1
                pattern_index += 1
                if pattern_index == len(pattern):
                    return True
            elif pattern_index:
                pattern_index = lps[pattern_index - 1]
            else:
                text_index += 1
        return False

    # --------------------------------------------------------
    # ITEM LOOKUP
    # --------------------------------------------------------
    def find_saved_item(self, selected_values):
        if not selected_values:
            return None
        selected_id = str(selected_values[0]).strip()
        for item in load_records(ITEMS_FILE):
            if self.item_id(item).casefold() == selected_id.casefold():
                return item
        return None
    # --------------------------------------------------------
    # SEARCH ITEMS
    # --------------------------------------------------------
    def search_items(self):
        if not self.is_student():
            return
        self.navigate(self.build_search_items)
    def build_search_items(self):
        self.create_header(
            self.screen_frame,
            "Search Campus Items",
            "Search approved records, view details or submit an ownership claim."
        )
        main = self.page_content(18)
        search_frame = tk.Frame(main, bg=BG)
        search_frame.pack(fill="x", pady=(0, 12))
        tk.Label(
            search_frame, text="Search:", font=FONT_BOLD,
            bg=BG, fg=PLUM
        ).pack(side="left", padx=(0, 8))
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=search_var, font=FONT,
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=BORDER
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=7)
        tk.Label(
            search_frame, text="Status:", font=FONT_BOLD,
            bg=BG, fg=PLUM
        ).pack(side="left", padx=(12, 6))
        status_var = tk.StringVar(value="ALL")
        status_box = ttk.Combobox(
            search_frame, textvariable=status_var,
            values=["ALL", "LOST", "FOUND", "CLAIMED"],
            state="readonly", width=12
        )
        status_box.pack(side="left")
        tk.Label(
            search_frame, text="Sort:", font=FONT_BOLD,
            bg=BG, fg=PLUM
        ).pack(side="left", padx=(12, 6))
        sort_var = tk.StringVar(value="Newest ID")
        sort_box = ttk.Combobox(
            search_frame, textvariable=sort_var,
            values=["Newest ID", "Oldest ID", "Name A-Z"],
            state="readonly", width=13
        )
        sort_box.pack(side="left")
        table_frame = tk.Frame(main, bg=BG)
        table_frame.pack(fill="both", expand=True)
        columns = (
            "id", "name", "category", "location",
            "date", "status", "reporter"
        )
        tree = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )
        tree.tag_configure("LOST", background=RED_LIGHT, foreground=RED)
        tree.tag_configure("FOUND", background=GREEN_LIGHT, foreground=GREEN)
        tree.tag_configure("CLAIMED", background=LAVENDER, foreground=DEEP_PLUM)
        headings = {
            "id": ("Item ID", 85),
            "name": ("Item Name", 170),
            "category": ("Category", 125),
            "location": ("Location", 160),
            "date": ("Date", 105),
            "status": ("Status", 95),
            "reporter": ("Reported By", 160)
        }
        for column, (heading, width) in headings.items():
            tree.heading(column, text=heading)
            tree.column(column, width=width, minwidth=65, anchor="w")
        vertical_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        horizontal_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=tree.xview
        )
        tree.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )
        tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        result_label = tk.Label(
            main, text="", font=FONT, bg=BG, fg=MUTED
        )
        result_label.pack(anchor="w", pady=(10, 8))
        def refresh_results(*_):
            keyword = search_var.get().strip().casefold()
            selected_status = status_var.get()
            items = load_records(ITEMS_FILE)
            filtered = []
            for item in items:
                if self.review_status(item) != "APPROVED":
                    continue
                searchable_fields = [
                    self.item_id(item),
                    str(self.item_name(item)),
                    str(item.get("category", "")),
                    str(item.get("location", "")),
                    str(item.get("description", "")),
                    str(item.get("status", "")),
                    str(item.get("reporter_name", ""))
                ]
                item_status = str(item.get("status", "")).upper()
                # KMP pattern matching is used internally for the existing search.
                # This changes the search implementation, not the website interface.
                text_matches = (
                    not keyword
                    or any(self.kmp_contains(str(field).casefold(), keyword)
                           for field in searchable_fields)
                )
                if (
                    text_matches
                    and (selected_status == "ALL" or item_status == selected_status)
                ):
                    filtered.append(item)
            if sort_var.get() == "Newest ID":
                filtered.sort(key=lambda item: self.item_id(item), reverse=True)
            elif sort_var.get() == "Oldest ID":
                filtered.sort(key=lambda item: self.item_id(item))
            else:
                filtered.sort(
                    key=lambda item: str(self.item_name(item)).casefold()
                )
            tree.delete(*tree.get_children())
            for item in filtered:
                tree.insert(
                    "", "end",
                    values=(
                        self.item_id(item),
                        self.item_name(item),
                        item.get("category", ""),
                        item.get("location", ""),
                        self.item_date(item),
                        item.get("status", ""),
                        item.get("reporter_name", item.get("reported_by", ""))
                    ),
                    tags=(str(item.get("status", "")).upper(),)
                )
            result_label.config(
                text=f"{len(filtered)} approved item(s) found  •  "
                     f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}"
            )
        def get_selected_item():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(
                    "No Item Selected",
                    "Please select an item from the table first.",
                    parent=self.root
                )
                return None
            item = self.find_saved_item(tree.item(selected[0], "values"))
            if item is None:
                messagebox.showerror(
                    "Item Not Found", "No matching saved record was found.",
                    parent=self.root
                )
                return None
            return item
        def view_details():
            item = get_selected_item()
            if item is not None:
                self.navigate(lambda: self.build_item_details(item))
        def submit_claim():
            item = get_selected_item()
            if item is None:
                return
            if str(item.get("status", "")).upper() != "FOUND":
                messagebox.showwarning(
                    "Cannot Claim",
                    "Only FOUND items can be claimed.",
                    parent=self.root
                )
                return
            current_email = str(
                self.current_user.get("email", "")
            ).strip().casefold()
            reporter_email = str(
                item.get("reported_by", "")
            ).strip().casefold()
            if current_email == reporter_email:
                messagebox.showwarning(
                    "Cannot Claim Your Own Report",
                    "You cannot claim an item you reported yourself.",
                    parent=self.root
                )
                return
            claims = load_records(CLAIMS_FILE)
            item_id = self.item_id(item)
            duplicate = any(
                str(claim.get("item_id", "")).strip() == item_id
                and str(claim.get("claimant_email", "")).strip().casefold()
                == current_email
                and str(claim.get("status", "PENDING")).upper() == "PENDING"
                for claim in claims
            )
            if duplicate:
                messagebox.showwarning(
                    "Claim Already Submitted",
                    "You already have a pending claim for this item.",
                    parent=self.root
                )
                return
            self.navigate(lambda: self.build_claim_form(item))
        controls = tk.Frame(main, bg=BG)
        controls.pack(fill="x", pady=(5, 0))
        self.make_button(
            controls, "Search", refresh_results
        ).pack(side="left", padx=(0, 8))
        self.make_button(
            controls, "View Details", view_details, primary=False
        ).pack(side="left", padx=8)
        self.make_button(
            controls, "Claim Selected Item", submit_claim
        ).pack(side="left", padx=8)
        self.make_button(
            controls, "Dashboard", self.open_student_dashboard,
            primary=False
        ).pack(side="right")
        search_entry.bind("<Return>", refresh_results)
        status_box.bind("<<ComboboxSelected>>", refresh_results)
        sort_box.bind("<<ComboboxSelected>>", refresh_results)
        refresh_results()
    # --------------------------------------------------------
    # ITEM DETAILS
    # --------------------------------------------------------
    def build_item_details(self, item):
        self.create_header(
            self.screen_frame,
            "Item Details",
            "Review the complete information for this item."
        )
        content = self.page_content(30)
        card = self.make_card(content, 22)
        card.pack(fill="x")
        details = [
            ("Item ID", self.item_id(item)),
            ("Name", self.item_name(item)),
            ("Category", item.get("category", "")),
            ("Location", item.get("location", "")),
            ("Date", self.item_date(item)),
            ("Item Status", item.get("status", "")),
            ("Review Status", self.review_status(item)),
            ("Reported By", item.get("reporter_name", item.get("reported_by", ""))),
            ("Created At", item.get("created_at", ""))
        ]
        for label, value in details:
            row = tk.Frame(card, bg=WHITE)
            row.pack(fill="x", pady=5)
            tk.Label(
                row, text=f"{label}:",
                font=FONT_BOLD, bg=WHITE, fg=PLUM,
                width=16, anchor="w"
            ).pack(side="left")
            tk.Label(
                row, text=str(value),
                font=FONT, bg=WHITE, fg=TEXT,
                wraplength=650, justify="left", anchor="w"
            ).pack(side="left", fill="x", expand=True)
        tk.Label(
            content, text="Description",
            font=FONT_BOLD, bg=BG, fg=PLUM
        ).pack(anchor="w", pady=(20, 5))
        description_box = tk.Text(
            content, height=5, font=FONT, wrap="word",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER
        )
        description_box.pack(fill="x")
        description_box.insert(
            "1.0", item.get("description", "No description provided.")
        )
        description_box.configure(state="disabled")

        bottom = tk.Frame(content, bg=BG)
        bottom.pack(fill="x", pady=(18, 0))

        self.make_button(
            bottom, "Back", self.go_back, primary=False
        ).pack(side="left")

        if (
            self.is_student()
            and str(item.get("status", "")).upper() == "FOUND"
            and self.review_status(item) == "APPROVED"
        ):
            self.make_button(
                bottom, "Claim This Item",
                lambda: self.start_claim_from_details(item)
            ).pack(side="left", padx=10)

        self.make_button(
            bottom, "Dashboard",
            self.open_student_dashboard if self.is_student()
            else self.open_admin_dashboard,
            primary=False
        ).pack(side="right")

    def start_claim_from_details(self, item):
        if not self.is_student():
            return

        if self.review_status(item) != "APPROVED":
            messagebox.showwarning(
                "Report Not Approved",
                "Only approved reports can be claimed.",
                parent=self.root
            )
            return

        if str(item.get("status", "")).upper() != "FOUND":
            messagebox.showwarning(
                "Cannot Claim", "Only FOUND items can be claimed.",
                parent=self.root
            )
            return

        current_email = str(
            self.current_user.get("email", "")
        ).strip().casefold()
        reporter_email = str(
            item.get("reported_by", "")
        ).strip().casefold()

        if current_email == reporter_email:
            messagebox.showwarning(
                "Cannot Claim Your Own Report",
                "You cannot claim an item you reported yourself.",
                parent=self.root
            )
            return

        if str(item.get("status", "")).upper() == "CLAIMED":
            messagebox.showwarning(
                "Already Claimed", "This item has already been claimed.",
                parent=self.root
            )
            return

        claims = load_records(CLAIMS_FILE)

        if any(
            str(claim.get("item_id", "")).strip() == self.item_id(item)
            and str(claim.get("claimant_email", "")).strip().casefold()
            == current_email
            and str(claim.get("status", "PENDING")).upper() == "PENDING"
            for claim in claims
        ):
            messagebox.showwarning(
                "Claim Already Submitted",
                "You already have a pending claim for this item.",
                parent=self.root
            )
            return

        self.navigate(lambda: self.build_claim_form(item))

    # --------------------------------------------------------
    # CLAIM SUBMISSION
    # --------------------------------------------------------

    def build_claim_form(self, item):
        item_id = self.item_id(item)

        self.create_header(
            self.screen_frame,
            "Claim Found Item",
            f"Item: {self.item_name(item)} ({item_id})"
        )

        form = self.page_content(28)

        tk.Label(
            form,
            text=(
                "Explain why this item belongs to you. "
                "Mention identifying details."
            ),
            font=FONT, bg=BG, fg=MUTED,
            wraplength=750, justify="left"
        ).pack(anchor="w", pady=(0, 10))

        explanation_box = self.create_labeled_text(
            form, "Ownership Explanation", 7
        )

        def save_claim():
            explanation = explanation_box.get("1.0", "end").strip()

            if len(explanation) < 10:
                messagebox.showwarning(
                    "More Information Required",
                    "Provide at least 10 characters explaining ownership.",
                    parent=self.root
                )
                return

            latest_items = load_records(ITEMS_FILE)
            latest_item = next(
                (saved for saved in latest_items
                 if self.item_id(saved) == item_id),
                None
            )

            if (
                latest_item is None
                or self.review_status(latest_item) != "APPROVED"
                or str(latest_item.get("status", "")).upper() != "FOUND"
            ):
                messagebox.showerror(
                    "Item Unavailable",
                    "This item is no longer available to claim.",
                    parent=self.root
                )
                return

            if str(latest_item.get("status", "")).upper() == "CLAIMED":
                messagebox.showerror(
                    "Already Claimed",
                    "This item has already been claimed.",
                    parent=self.root
                )
                return

            latest_claims = load_records(CLAIMS_FILE)
            current_email = str(
                self.current_user.get("email", "")
            ).strip().casefold()

            duplicate = any(
                str(claim.get("item_id", "")).strip() == item_id
                and str(claim.get("claimant_email", "")).strip().casefold()
                == current_email
                and str(claim.get("status", "PENDING")).upper() == "PENDING"
                for claim in latest_claims
            )

            if duplicate:
                messagebox.showwarning(
                    "Duplicate Claim",
                    "You already have a pending claim for this item.",
                    parent=self.root
                )
                return

            new_claim = {
                "id": self.next_id(latest_claims, "C"),
                "item_id": item_id,
                "item_name": self.item_name(latest_item),
                "claimant_email": self.current_user.get("email"),
                "claimant_name": self.current_user.get("name"),
                "explanation": explanation,
                "status": "PENDING",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            latest_claims.append(new_claim)

            if save_records(CLAIMS_FILE, latest_claims):
                messagebox.showinfo(
                    "Claim Submitted",
                    f"Claim ID: {new_claim['id']}\n"
                    "Your claim is awaiting administrator review.",
                    parent=self.root
                )
                self.open_student_dashboard()

        self.make_button(
            form, "Submit Claim", save_claim
        ).pack(fill="x", pady=(15, 8))

        self.make_button(
            form, "Cancel / Back", self.go_back, primary=False
        ).pack(fill="x")

    # --------------------------------------------------------
    # MY CLAIMS
    # --------------------------------------------------------

    def my_claims(self):
        if not self.is_student():
            return
        self.navigate(self.build_my_claims)

    def build_my_claims(self):
        self.create_header(
            self.screen_frame,
            "My Claims",
            "View the claims you have submitted and their current status."
        )

        main = self.page_content(20)
        columns = ("claim_id", "item_id", "item_name", "status", "created_at")

        table_frame = tk.Frame(main, bg=BG)
        table_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )

        headings = {
            "claim_id": ("Claim ID", 100),
            "item_id": ("Item ID", 100),
            "item_name": ("Item Name", 220),
            "status": ("Claim Status", 140),
            "created_at": ("Submitted At", 190)
        }

        for column, (heading, width) in headings.items():
            tree.heading(column, text=heading)
            tree.column(column, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        result_label = tk.Label(
            main, text="", font=FONT, bg=BG, fg=MUTED
        )
        result_label.pack(anchor="w", pady=10)

        def refresh_claims():
            tree.delete(*tree.get_children())
            claims = load_records(CLAIMS_FILE)
            email = str(
                self.current_user.get("email", "")
            ).strip().casefold()

            records = [
                claim for claim in claims
                if str(claim.get("claimant_email", "")).strip().casefold()
                == email
            ]
            records.sort(
                key=lambda claim: claim.get("created_at", ""),
                reverse=True
            )

            for claim in records:
                tree.insert(
                    "", "end",
                    values=(
                        claim.get("id", ""),
                        claim.get("item_id", ""),
                        claim.get("item_name", ""),
                        claim.get("status", "PENDING"),
                        claim.get("created_at", "")
                    )
                )

            result_label.config(
                text=f"You have submitted {len(records)} claim(s)."
            )

        def show_claim_details():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "No Claim Selected", "Please select a claim first.",
                    parent=self.root
                )
                return

            claim_id = str(tree.item(selection[0], "values")[0])
            email = str(self.current_user.get("email", "")).casefold()

            claim = next(
                (
                    record for record in load_records(CLAIMS_FILE)
                    if str(record.get("id", "")) == claim_id
                    and str(record.get("claimant_email", "")).casefold() == email
                ),
                None
            )

            if claim is None:
                messagebox.showerror(
                    "Not Found", "Claim record could not be found.",
                    parent=self.root
                )
                return

            self.navigate(lambda: self.build_claim_details(claim))

        controls = tk.Frame(main, bg=BG)
        controls.pack(fill="x", pady=(8, 0))

        self.make_button(
            controls, "View Claim Details", show_claim_details
        ).pack(side="left")

        self.make_button(
            controls, "Refresh", refresh_claims, primary=False
        ).pack(side="left", padx=10)

        self.make_button(
            controls, "Dashboard", self.open_student_dashboard,
            primary=False
        ).pack(side="right")

        tree.bind("<Double-1>", lambda event: show_claim_details())
        refresh_claims()

    def build_claim_details(self, claim):
        self.create_header(
            self.screen_frame,
            "Claim Details",
            "Review the details and current status of your claim."
        )

        content = self.page_content(30)
        card = self.make_card(content, 22)
        card.pack(fill="x")

        for label, value in [
            ("Claim ID", claim.get("id", "")),
            ("Item ID", claim.get("item_id", "")),
            ("Item Name", claim.get("item_name", "")),
            ("Status", claim.get("status", "")),
            ("Submitted At", claim.get("created_at", "")),
            ("Reviewed At", claim.get("reviewed_at", "Not reviewed yet"))
        ]:
            row = tk.Frame(card, bg=WHITE)
            row.pack(fill="x", pady=5)

            tk.Label(
                row, text=f"{label}:",
                font=FONT_BOLD, bg=WHITE, fg=PLUM,
                width=16, anchor="w"
            ).pack(side="left")

            tk.Label(
                row, text=str(value),
                font=FONT, bg=WHITE, fg=TEXT,
                wraplength=650, justify="left", anchor="w"
            ).pack(side="left", fill="x", expand=True)

        tk.Label(
            content, text="Ownership Explanation",
            font=FONT_BOLD, bg=BG, fg=PLUM
        ).pack(anchor="w", pady=(20, 5))

        explanation = tk.Text(
            content, height=6, font=FONT, wrap="word",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER
        )
        explanation.pack(fill="x")
        explanation.insert("1.0", claim.get("explanation", ""))
        explanation.configure(state="disabled")

        self.make_button(
            content, "Back", self.go_back, primary=False
        ).pack(fill="x", pady=(18, 8))

        self.make_button(
            content, "Dashboard", self.open_student_dashboard
        ).pack(fill="x")

    # ========================================================
    # ADMIN AUTHENTICATION
    # ========================================================

    def open_admin_login(self):
        self.navigate(self.build_admin_login)

    def build_admin_login(self):
        admins = [
            user for user in load_records(USERS_FILE)
            if str(user.get("role", "")).upper() == "ADMIN"
        ]
        first_setup = len(admins) == 0

        self.create_header(
            self.screen_frame,
            "First-Time Admin Setup" if first_setup else "Administrator Login",
            (
                "Create your administrator account. This setup is available "
                "only when no admin account exists."
                if first_setup else
                "Sign in to manage reports, claims and campus records."
            )
        )

        page = self.page_content(24)
        center = tk.Frame(page, bg=BG)
        center.pack(fill="both", expand=True)

        form = self.make_card(center, 32)
        form.configure(bg=WHITE, highlightbackground=ROSE, highlightthickness=2)
        form.pack(fill="y", expand=False, padx=150, pady=20, anchor="n")

        tk.Label(
            form, text="Administrator Access",
            font=("Georgia", 24, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w", pady=(0, 5))
        tk.Label(
            form,
            text="A secure workspace for reviewing reports and ownership claims.",
            font=("Segoe UI", 10), bg=WHITE, fg=MUTED,
            wraplength=600, justify="left"
        ).pack(anchor="w", pady=(0, 14))

        email_entry = self.create_entry(form, "Administrator Email")
        password_entry = self.create_entry(form, "Password", show="*")

        name_entry = None
        confirm_entry = None

        if first_setup:
            name_entry = self.create_entry(form, "Administrator Name")
            confirm_entry = self.create_entry(
                form, "Confirm Password", show="*"
            )

        def authenticate():
            email = email_entry.get().strip().lower()
            password = password_entry.get()

            if not email or not password:
                messagebox.showwarning(
                    "Missing Information",
                    "Enter your email and password.",
                    parent=self.root
                )
                return

            users = load_records(USERS_FILE)
            admins_now = [
                user for user in users
                if str(user.get("role", "")).upper() == "ADMIN"
            ]

            # First admin account: no hardcoded credentials.
            if not admins_now:
                name = name_entry.get().strip()
                confirm = confirm_entry.get()

                if not name:
                    messagebox.showwarning(
                        "Missing Name",
                        "Enter the administrator's name.",
                        parent=self.root
                    )
                    return

                if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                    messagebox.showwarning(
                        "Invalid Email",
                        "Enter a valid email address.",
                        parent=self.root
                    )
                    return

                if len(password) < 8:
                    messagebox.showwarning(
                        "Weak Password",
                        "Use a password with at least 8 characters.",
                        parent=self.root
                    )
                    return

                if password != confirm:
                    messagebox.showwarning(
                        "Password Mismatch",
                        "The passwords do not match.",
                        parent=self.root
                    )
                    return

                if any(
                    str(user.get("email", "")).strip().lower() == email
                    for user in users
                ):
                    messagebox.showerror(
                        "Email Already Registered",
                        "This email is already associated with an account.",
                        parent=self.root
                    )
                    return

                salt, password_hash = hash_password(password)

                admin = {
                    "id": self.next_id(users, "U"),
                    "name": name,
                    "email": email,
                    "salt": salt,
                    "password_hash": password_hash,
                    "role": "ADMIN",
                    "created_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }

                users.append(admin)

                if save_records(USERS_FILE, users):
                    messagebox.showinfo(
                        "Admin Account Created",
                        "Administrator account created. Sign in with your credentials.",
                        parent=self.root
                    )
                    self.navigate(self.build_admin_login, remember=False)
                return

            for admin in admins_now:
                if (
                    str(admin.get("email", "")).strip().lower() == email
                    and verify_password(
                        password,
                        admin.get("salt", ""),
                        admin.get("password_hash", "")
                    )
                ):
                    self.current_user = admin
                    self.history.clear()
                    self.navigate(
                        self.build_admin_dashboard, remember=False
                    )
                    return

            messagebox.showerror(
                "Login Failed",
                "Incorrect administrator email or password.",
                parent=self.root
            )

        self.make_button(
            form,
            "Create Admin Account" if first_setup else "Sign In",
            authenticate
        ).pack(fill="x", pady=(20, 10))

        self.make_button(
            form, "Back to Home", self.go_home, primary=False
        ).pack(fill="x")

        password_entry.bind("<Return>", lambda event: authenticate())

    # ========================================================
    # ADMIN STATISTICS AND DASHBOARD
    # ========================================================

    def get_admin_stats(self):
        users = load_records(USERS_FILE)
        items = load_records(ITEMS_FILE)
        claims = load_records(CLAIMS_FILE)

        return {
            "students": sum(
                1 for user in users
                if str(user.get("role", "")).upper() == "STUDENT"
            ),
            "total_items": len(items),
            "pending_reports": sum(
                1 for item in items
                if self.review_status(item) == "PENDING"
            ),
            "approved_reports": sum(
                1 for item in items
                if self.review_status(item) == "APPROVED"
            ),
            "rejected_reports": sum(
                1 for item in items
                if self.review_status(item) == "REJECTED"
            ),
            "pending_claims": sum(
                1 for claim in claims
                if str(claim.get("status", "PENDING")).upper() == "PENDING"
            ),
            "approved_claims": sum(
                1 for claim in claims
                if str(claim.get("status", "")).upper()
                in ("APPROVED", "ACCEPTED")
            ),
            "rejected_claims": sum(
                1 for claim in claims
                if str(claim.get("status", "")).upper()
                in ("REJECTED", "DECLINED")
            )
        }

    def admin_stat_card(self, parent, title, value, accent):
        card = tk.Frame(
            parent, bg=WHITE, padx=13, pady=12,
            highlightbackground=BORDER, highlightthickness=1
        )

        tk.Frame(
            card, bg=accent, height=3
        ).pack(fill="x", pady=(0, 9))

        tk.Label(
            card, text=str(value),
            font=("Segoe UI", 23, "bold"), bg=WHITE, fg=accent
        ).pack(anchor="w")

        tk.Label(
            card, text=title,
            font=("Segoe UI", 9, "bold"), bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(3, 0))

        return card

    def open_admin_dashboard(self):
        self.history.clear()
        self.navigate(self.build_admin_dashboard, remember=False)

    def build_admin_dashboard(self):
        if not self.is_admin():
            self.navigate(self.build_home, remember=False)
            return

        stats = self.get_admin_stats()

        self.create_header(
            self.screen_frame,
            "Administrator Dashboard",
            f"Welcome, {self.current_user.get('name', 'Administrator')}. "
            "Review reports, manage claims and monitor system activity."
        )

        content = self.page_content(20)

        dashboard_toolbar = tk.Frame(content, bg=BG)
        dashboard_toolbar.pack(fill="x", pady=(0, 12))
        self.make_button(
            dashboard_toolbar, "Log Out", self.logout, primary=False
        ).pack(side="right")

        tk.Label(
            content, text="System Overview",
            font=("Georgia", 22, "bold"), bg=BG, fg=PLUM
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Every statistic below comes from your saved JSON records.",
            font=FONT_SUBTITLE, bg=BG, fg=MUTED
        ).pack(anchor="w", pady=(4, 14))

        stats_frame = tk.Frame(content, bg=BG)
        stats_frame.pack(fill="x", pady=(0, 16))

        for title, key, accent in [
            ("Registered Students", "students", PLUM),
            ("Total Reports", "total_items", ROSE_DARK),
            ("Pending Reports", "pending_reports", GOLD),
            ("Pending Claims", "pending_claims", PLUM_LIGHT)
        ]:
            self.admin_stat_card(
                stats_frame, title, stats[key], accent
            ).pack(side="left", fill="x", expand=True, padx=4)

        # Keep ownership-claim totals above the expanding dashboard panels
        # so the summary remains visible without scrolling.
        claim_summary = self.make_card(content, 12)
        claim_summary.pack(fill="x", pady=(0, 14))

        summary_header = tk.Frame(claim_summary, bg=WHITE)
        summary_header.pack(fill="x")
        tk.Label(
            summary_header, text="Ownership Claim Summary",
            font=("Segoe UI", 13, "bold"), bg=WHITE, fg=PLUM
        ).pack(side="left", anchor="w")
        tk.Label(
            summary_header,
            text="Live totals from saved ownership claims",
            font=("Segoe UI", 9), bg=WHITE, fg=MUTED
        ).pack(side="right", anchor="e")

        line = tk.Frame(claim_summary, bg=WHITE)
        line.pack(fill="x", pady=(9, 0))

        for title, key, accent in [
            ("Pending Claims", "pending_claims", GOLD),
            ("Approved Claims", "approved_claims", GREEN),
            ("Rejected Claims", "rejected_claims", RED)
        ]:
            self.small_summary(
                line, title, stats[key], accent
            ).pack(side="left", expand=True, fill="x", padx=4)

        body = tk.Frame(content, bg=BG)
        body.pack(fill="both", expand=True)

        actions = self.make_card(body, 18)
        actions.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            actions, text="Management",
            font=("Segoe UI", 16, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w")

        tk.Label(
            actions, text="Choose a section to review.",
            font=FONT, bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(4, 12))

        self.make_button(
            actions, "Review Item Reports", self.open_admin_reports
        ).pack(fill="x", pady=5)

        self.make_button(
            actions, "Review Ownership Claims", self.open_admin_claims
        ).pack(fill="x", pady=5)

        self.make_button(
            actions, "Campus Locations & Shortest Route", self.open_campus_locations
        ).pack(fill="x", pady=5)

        self.make_button(
            actions, "Refresh Dashboard", self.open_admin_dashboard,
            primary=False
        ).pack(fill="x", pady=5)

        self.make_button(
            actions, "Logout", self.logout, primary=False
        ).pack(fill="x", pady=(14, 5))

        overview = self.make_card(body, 15)
        overview.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            overview, text="Report Review Status",
            font=("Segoe UI", 15, "bold"), bg=WHITE, fg=PLUM
        ).pack(anchor="w")

        tk.Label(
            overview,
            text="Approved, pending and rejected reports",
            font=("Segoe UI", 9), bg=WHITE, fg=MUTED
        ).pack(anchor="w", pady=(4, 5))

        self.draw_donut(
            overview,
            [
                ("Approved", stats["approved_reports"], GREEN),
                ("Pending", stats["pending_reports"], GOLD),
                ("Rejected", stats["rejected_reports"], RED)
            ],
            "reports",
            stats["approved_reports"]
            + stats["pending_reports"]
            + stats["rejected_reports"]
        )


    # --------------------------------------------------------
    # CAMPUS LOCATIONS AND DIJKSTRA SHORTEST-PATH ROUTING
    # --------------------------------------------------------
    def load_campus_map(self):
        """Load the user-configured campus graph without adding fake locations."""
        ensure_storage()
        try:
            with LOCATIONS_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Campus location data must be a JSON object.")
            locations = data.get("locations", [])
            connections = data.get("connections", [])
            if not isinstance(locations, list) or not isinstance(connections, list):
                raise ValueError("Locations and connections must be lists.")
            return {"locations": locations, "connections": connections}
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror(
                "Campus Location Data Error",
                f"Could not read campus_locations.json.\n\n{error}",
                parent=self.root
            )
            return {"locations": [], "connections": []}

    def save_campus_map(self, data):
        try:
            with LOCATIONS_FILE.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except OSError as error:
            messagebox.showerror(
                "Save Error", f"Could not save campus locations.\n\n{error}",
                parent=self.root
            )
            return False

    @staticmethod
    def dijkstra_shortest_path(locations, connections, start, destination):
        """Return shortest path and distance using Dijkstra's algorithm."""
        if start == destination:
            return [start], 0.0
        graph = {name: [] for name in locations}
        for edge in connections:
            a = str(edge.get("from", ""))
            b = str(edge.get("to", ""))
            try:
                distance = float(edge.get("distance", 0))
            except (TypeError, ValueError):
                continue
            if a in graph and b in graph and distance >= 0:
                graph[a].append((b, distance))
                graph[b].append((a, distance))
        distances = {name: float("inf") for name in graph}
        previous = {}
        distances[start] = 0.0
        queue = [(0.0, start)]
        while queue:
            current_distance, current = heapq.heappop(queue)
            if current_distance > distances[current]:
                continue
            if current == destination:
                break
            for neighbour, weight in graph[current]:
                candidate = current_distance + weight
                if candidate < distances[neighbour]:
                    distances[neighbour] = candidate
                    previous[neighbour] = current
                    heapq.heappush(queue, (candidate, neighbour))
        if distances[destination] == float("inf"):
            return None, None
        path = [destination]
        while path[-1] != start:
            path.append(previous[path[-1]])
        path.reverse()
        return path, distances[destination]

    def open_campus_locations(self):
        if not self.current_user:
            self.navigate(self.build_home, remember=False)
            return
        if not (self.is_student() or self.is_admin()):
            return
        self.navigate(self.build_campus_locations)

    def build_campus_locations(self):
        self.create_header(
            self.screen_frame,
            "Campus Locations & Shortest Route",
            "Add your campus buildings and walking distances. Dijkstra's algorithm "
            "will calculate the shortest route using the connections you enter."
        )
        content = self.page_content(18)
        data = self.load_campus_map()
        location_names = [str(x.get("name", "")).strip() for x in data["locations"]
                          if isinstance(x, dict) and str(x.get("name", "")).strip()]

        info = tk.Frame(content, bg=LAVENDER_LIGHT, padx=14, pady=12,
                        highlightbackground=BORDER, highlightthickness=1)
        info.pack(fill="x", pady=(0, 14))
        tk.Label(
            info,
            text="First add the actual campus locations, then connect locations with "
                 "the distance between them. No sample locations or distances are inserted.",
            font=FONT, bg=LAVENDER_LIGHT, fg=PLUM, wraplength=1000,
            justify="left"
        ).pack(anchor="w")

        columns = tk.Frame(content, bg=BG)
        columns.pack(fill="x", pady=(0, 14))
        locations_card = self.make_card(columns, 14)
        locations_card.pack(side="left", fill="both", expand=True, padx=(0, 7))
        connections_card = self.make_card(columns, 14)
        connections_card.pack(side="left", fill="both", expand=True, padx=(7, 0))

        tk.Label(locations_card, text="1. Add Campus Location",
                 font=("Segoe UI", 13, "bold"), bg=WHITE, fg=PLUM).pack(anchor="w")
        location_name_var = tk.StringVar()
        tk.Label(locations_card, text="Building / place name", font=FONT_BOLD,
                 bg=WHITE, fg=PLUM).pack(anchor="w", pady=(10, 4))
        location_name_entry = tk.Entry(locations_card, textvariable=location_name_var,
                                       font=FONT, relief="flat", highlightthickness=1,
                                       highlightbackground=BORDER)
        location_name_entry.pack(fill="x", ipady=7)

        def add_location():
            name = location_name_var.get().strip()
            if not name:
                messagebox.showwarning("Location Required", "Enter a campus location name.", parent=self.root)
                return
            current = self.load_campus_map()
            if any(str(x.get("name", "")).casefold() == name.casefold()
                   for x in current["locations"] if isinstance(x, dict)):
                messagebox.showwarning("Already Exists", "That location is already saved.", parent=self.root)
                return
            current["locations"].append({"name": name})
            if self.save_campus_map(current):
                messagebox.showinfo("Location Saved", f"{name} was added.", parent=self.root)
                self.navigate(self.build_campus_locations, remember=False)

        self.make_button(locations_card, "Add Location", add_location).pack(fill="x", pady=(10, 7))
        tk.Label(locations_card, text="Saved locations", font=FONT_BOLD,
                 bg=WHITE, fg=PLUM).pack(anchor="w", pady=(7, 4))
        locations_text = tk.Text(locations_card, height=7, font=FONT, wrap="word",
                                 bg="#FFF9FC", fg=TEXT, relief="flat",
                                 highlightthickness=1, highlightbackground=BORDER)
        locations_text.pack(fill="both", expand=True)
        locations_text.insert("1.0", "\n".join(f"• {name}" for name in location_names)
                              if location_names else "No locations added yet.")
        locations_text.configure(state="disabled")

        tk.Label(connections_card, text="2. Connect Two Locations",
                 font=("Segoe UI", 13, "bold"), bg=WHITE, fg=PLUM).pack(anchor="w")
        from_var = tk.StringVar(value=location_names[0] if location_names else "")
        to_var = tk.StringVar(value=location_names[1] if len(location_names) > 1 else "")
        distance_var = tk.StringVar()
        tk.Label(connections_card, text="From", font=FONT_BOLD,
                 bg=WHITE, fg=PLUM).pack(anchor="w", pady=(10, 4))
        from_box = ttk.Combobox(connections_card, textvariable=from_var,
                                values=location_names, state="readonly")
        from_box.pack(fill="x", ipady=4)
        tk.Label(connections_card, text="To", font=FONT_BOLD,
                 bg=WHITE, fg=PLUM).pack(anchor="w", pady=(8, 4))
        to_box = ttk.Combobox(connections_card, textvariable=to_var,
                              values=location_names, state="readonly")
        to_box.pack(fill="x", ipady=4)
        tk.Label(connections_card, text="Distance (metres, or another consistent unit)",
                 font=FONT_BOLD, bg=WHITE, fg=PLUM, wraplength=340,
                 justify="left").pack(anchor="w", pady=(8, 4))
        distance_entry = tk.Entry(connections_card, textvariable=distance_var,
                                  font=FONT, relief="flat", highlightthickness=1,
                                  highlightbackground=BORDER)
        distance_entry.pack(fill="x", ipady=7)

        def add_connection():
            a, b = from_var.get().strip(), to_var.get().strip()
            try:
                distance = float(distance_var.get().strip())
            except ValueError:
                messagebox.showwarning("Invalid Distance", "Enter a numeric distance greater than zero.", parent=self.root)
                return
            if not a or not b or a == b:
                messagebox.showwarning("Locations Required", "Choose two different saved locations.", parent=self.root)
                return
            if distance <= 0:
                messagebox.showwarning("Invalid Distance", "Distance must be greater than zero.", parent=self.root)
                return
            current = self.load_campus_map()
            known = {str(x.get("name", "")) for x in current["locations"] if isinstance(x, dict)}
            if a not in known or b not in known:
                messagebox.showwarning("Refresh Required", "Add and select saved locations first.", parent=self.root)
                return
            for edge in current["connections"]:
                if {str(edge.get("from", "")), str(edge.get("to", ""))} == {a, b}:
                    messagebox.showwarning("Connection Exists", "A connection between these locations is already saved.", parent=self.root)
                    return
            current["connections"].append({"from": a, "to": b, "distance": distance})
            if self.save_campus_map(current):
                messagebox.showinfo("Connection Saved", f"Connected {a} and {b} with distance {distance:g}.", parent=self.root)
                self.navigate(self.build_campus_locations, remember=False)

        self.make_button(connections_card, "Save Connection", add_connection).pack(fill="x", pady=(10, 7))
        tk.Label(connections_card, text="Saved connections", font=FONT_BOLD,
                 bg=WHITE, fg=PLUM).pack(anchor="w", pady=(7, 4))
        current_connections = data["connections"]
        connection_lines = []
        for edge in current_connections:
            if isinstance(edge, dict):
                connection_lines.append(
                    f"{edge.get('from', '?')} ↔ {edge.get('to', '?')}  ·  "
                    f"{edge.get('distance', '?')} units"
                )
        connections_text = tk.Text(connections_card, height=5, font=FONT, wrap="word",
                                   bg="#FFF9FC", fg=TEXT, relief="flat",
                                   highlightthickness=1, highlightbackground=BORDER)
        connections_text.pack(fill="both", expand=True)
        connections_text.insert("1.0", "\n".join(connection_lines) if connection_lines else "No connections added yet.")
        connections_text.configure(state="disabled")

        route_card = self.make_card(content, 15)
        route_card.pack(fill="x", pady=(0, 14))
        tk.Label(route_card, text="3. Find the Shortest Route (Dijkstra)",
                 font=("Segoe UI", 14, "bold"), bg=WHITE, fg=PLUM).pack(anchor="w")
        route_row = tk.Frame(route_card, bg=WHITE)
        route_row.pack(fill="x", pady=(10, 8))
        route_start_var = tk.StringVar(value=location_names[0] if location_names else "")
        route_end_var = tk.StringVar(value=location_names[-1] if location_names else "")
        tk.Label(route_row, text="Start", font=FONT_BOLD, bg=WHITE, fg=PLUM).pack(side="left", padx=(0, 6))
        start_box = ttk.Combobox(route_row, textvariable=route_start_var,
                                 values=location_names, state="readonly", width=25)
        start_box.pack(side="left", padx=(0, 14))
        tk.Label(route_row, text="Destination", font=FONT_BOLD, bg=WHITE, fg=PLUM).pack(side="left", padx=(0, 6))
        end_box = ttk.Combobox(route_row, textvariable=route_end_var,
                               values=location_names, state="readonly", width=25)
        end_box.pack(side="left", padx=(0, 14))
        route_result = tk.Label(route_card, text="Choose a start and destination to calculate a route.",
                                font=FONT, bg=WHITE, fg=MUTED, justify="left", anchor="w",
                                wraplength=1000)
        route_result.pack(fill="x", pady=(4, 8))

        def calculate_route():
            current = self.load_campus_map()
            names = [str(x.get("name", "")).strip() for x in current["locations"]
                     if isinstance(x, dict) and str(x.get("name", "")).strip()]
            start, destination = route_start_var.get().strip(), route_end_var.get().strip()
            if not names or start not in names or destination not in names:
                messagebox.showwarning("Locations Required", "Add at least one location and choose valid start and destination locations.", parent=self.root)
                return
            path, total = self.dijkstra_shortest_path(names, current["connections"], start, destination)
            if path is None:
                route_result.configure(
                    text="No route exists between these locations yet. Add connections that link them together.",
                    fg=ROSE_DARK
                )
            else:
                route_result.configure(
                    text="Shortest route: " + "  →  ".join(path) +
                         f"\nTotal distance: {total:g} units\nAlgorithm: Dijkstra's shortest-path algorithm",
                    fg=GREEN
                )

        self.make_button(route_card, "Calculate Shortest Route", calculate_route).pack(anchor="w")
        self.make_button(content, "Back to Dashboard",
                         self.open_admin_dashboard if self.is_admin() else self.open_student_dashboard,
                         primary=False).pack(anchor="w", pady=(0, 5))

    # --------------------------------------------------------
    # ADMIN ITEM REPORT REVIEW
    # --------------------------------------------------------

    def open_admin_reports(self):
        if not self.is_admin():
            self.navigate(self.build_home, remember=False)
            return
        self.navigate(self.build_admin_reports)

    def build_admin_reports(self):
        self.create_header(
            self.screen_frame,
            "Item Report Management",
            "Approve or reject student-submitted lost and found reports."
        )

        main = self.page_content(18)
        filter_row = tk.Frame(main, bg=BG)
        filter_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            filter_row, text="Review status:",
            font=FONT_BOLD, bg=BG, fg=PLUM
        ).pack(side="left", padx=(0, 8))

        review_var = tk.StringVar(value="ALL")
        review_box = ttk.Combobox(
            filter_row, textvariable=review_var,
            values=["PENDING", "APPROVED", "REJECTED", "ALL"],
            state="readonly", width=14
        )
        review_box.pack(side="left")

        table_frame = tk.Frame(main, bg=BG)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id", "name", "status", "category",
            "location", "reporter", "review"
        )

        tree = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )
        tree.tag_configure("APPROVED", background=GREEN_LIGHT, foreground=GREEN)
        tree.tag_configure("REJECTED", background=RED_LIGHT, foreground=RED)
        tree.tag_configure("PENDING", background=AMBER_LIGHT, foreground=AMBER)

        headings = {
            "id": ("Item ID", 80),
            "name": ("Item Name", 150),
            "status": ("Lost/Found", 90),
            "category": ("Category", 115),
            "location": ("Location", 140),
            "reporter": ("Reported By", 160),
            "review": ("Review Status", 115)
        }

        for col, (heading, width) in headings.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width, minwidth=65, anchor="w")

        yscroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=yscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        count_label = tk.Label(
            main, text="", font=FONT, bg=BG, fg=MUTED
        )
        count_label.pack(anchor="w", pady=8)

        def refresh():
            tree.delete(*tree.get_children())
            items = load_records(ITEMS_FILE)
            selected_review = review_var.get()

            filtered = [
                item for item in items
                if selected_review == "ALL"
                or self.review_status(item) == selected_review
            ]

            filtered.sort(
                key=lambda item: item.get("created_at", ""),
                reverse=True
            )

            for item in filtered:
                tree.insert(
                    "", "end",
                    values=(
                        self.item_id(item),
                        self.item_name(item),
                        item.get("status", ""),
                        item.get("category", ""),
                        item.get("location", ""),
                        item.get("reporter_name", item.get("reported_by", "")),
                        self.review_status(item)
                    ),
                    tags=(self.review_status(item),)
                )

            count_label.config(
                text=f"{len(filtered)} report(s) shown  •  "
                     f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}"
            )

        def selected_item():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "Select a Report",
                    "Select a report from the table first.",
                    parent=self.root
                )
                return None

            selected_id = str(tree.item(selection[0], "values")[0]).strip()

            return next(
                (
                    item for item in load_records(ITEMS_FILE)
                    if self.item_id(item) == selected_id
                ),
                None
            )

        def view_report():
            item = selected_item()
            if item is not None:
                self.navigate(lambda: self.build_item_details(item))

        def review_report(new_status):
            item = selected_item()

            if item is None:
                messagebox.showerror(
                    "Report Not Found",
                    "The selected saved report could not be found.",
                    parent=self.root
                )
                return

            if not messagebox.askyesno(
                f"{new_status.title()} Report",
                f"{new_status.title()} report {self.item_id(item)}?",
                parent=self.root
            ):
                return

            items = load_records(ITEMS_FILE)
            selected_id = self.item_id(item)
            updated = False

            for saved_item in items:
                if self.item_id(saved_item) == selected_id:
                    saved_item["review_status"] = new_status
                    saved_item["reviewed_at"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    saved_item["reviewed_by"] = self.current_user.get("email")
                    updated = True
                    break

            if not updated:
                messagebox.showerror(
                    "Report Not Found",
                    "The report could not be updated.",
                    parent=self.root
                )
                return

            if save_records(ITEMS_FILE, items):
                messagebox.showinfo(
                    "Report Updated",
                    f"Report {selected_id} is now {new_status}.",
                    parent=self.root
                )
                refresh()

        buttons = tk.Frame(main, bg=BG)
        buttons.pack(fill="x", pady=(5, 0))

        self.make_button(
            buttons, "View Details", view_report, primary=False
        ).pack(side="left", padx=(0, 8))

        self.make_button(
            buttons, "Approve Report",
            lambda: review_report("APPROVED")
        ).pack(side="left", padx=8)

        self.make_button(
            buttons, "Reject Report",
            lambda: review_report("REJECTED")
        ).pack(side="left", padx=8)

        self.make_button(
            buttons, "Refresh", refresh, primary=False
        ).pack(side="left", padx=8)

        self.make_button(
            buttons, "Admin Dashboard", self.open_admin_dashboard,
            primary=False
        ).pack(side="right")

        review_box.bind(
            "<<ComboboxSelected>>", lambda event: refresh()
        )
        tree.bind("<Double-1>", lambda event: view_report())
        refresh()

    # --------------------------------------------------------
    # ADMIN CLAIM REVIEW
    # --------------------------------------------------------

    def open_admin_claims(self):
        if not self.is_admin():
            self.navigate(self.build_home, remember=False)
            return
        self.navigate(self.build_admin_claims)

    def build_admin_claims(self):
        self.create_header(
            self.screen_frame,
            "Ownership Claim Management",
            "Read each student's explanation before deciding a claim."
        )

        main = self.page_content(18)
        filter_row = tk.Frame(main, bg=BG)
        filter_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            filter_row, text="Claim status:",
            font=FONT_BOLD, bg=BG, fg=PLUM
        ).pack(side="left", padx=(0, 8))

        status_var = tk.StringVar(value="PENDING")
        status_box = ttk.Combobox(
            filter_row, textvariable=status_var,
            values=["PENDING", "APPROVED", "REJECTED", "ALL"],
            state="readonly", width=14
        )
        status_box.pack(side="left")

        table_frame = tk.Frame(main, bg=BG)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id", "item_id", "item_name",
            "claimant", "status", "created_at"
        )

        tree = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )
        tree.tag_configure("APPROVED", background=GREEN_LIGHT, foreground=GREEN)
        tree.tag_configure("REJECTED", background=RED_LIGHT, foreground=RED)
        tree.tag_configure("PENDING", background=AMBER_LIGHT, foreground=AMBER)

        headings = {
            "id": ("Claim ID", 85),
            "item_id": ("Item ID", 85),
            "item_name": ("Item Name", 150),
            "claimant": ("Claimant", 170),
            "status": ("Status", 100),
            "created_at": ("Submitted At", 165)
        }

        for col, (heading, width) in headings.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width, minwidth=65, anchor="w")

        yscroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=yscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        count_label = tk.Label(
            main, text="", font=FONT, bg=BG, fg=MUTED
        )
        count_label.pack(anchor="w", pady=8)

        def refresh():
            tree.delete(*tree.get_children())
            claims = load_records(CLAIMS_FILE)
            selected_status = status_var.get()

            filtered = [
                claim for claim in claims
                if selected_status == "ALL"
                or str(claim.get("status", "PENDING")).upper()
                == selected_status
            ]

            filtered.sort(
                key=lambda claim: claim.get("created_at", ""),
                reverse=True
            )

            for claim in filtered:
                tree.insert(
                    "", "end",
                    values=(
                        claim.get("id", ""),
                        claim.get("item_id", ""),
                        claim.get("item_name", ""),
                        claim.get("claimant_name", claim.get("claimant_email", "")),
                        claim.get("status", "PENDING"),
                        claim.get("created_at", "")
                    ),
                    tags=(str(claim.get("status", "PENDING")).upper(),)
                )

            count_label.config(
                text=f"{len(filtered)} claim(s) shown  •  "
                     f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}"
            )

        def selected_claim():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "Select a Claim",
                    "Select a claim from the table first.",
                    parent=self.root
                )
                return None

            claim_id = str(tree.item(selection[0], "values")[0]).strip()

            return next(
                (
                    claim for claim in load_records(CLAIMS_FILE)
                    if str(claim.get("id", "")).strip() == claim_id
                ),
                None
            )

        def view_details():
            claim = selected_claim()

            if claim is None:
                messagebox.showerror(
                    "Claim Not Found",
                    "The selected saved claim could not be found.",
                    parent=self.root
                )
                return

            self.navigate(lambda: self.build_admin_claim_details(claim))

        def decide_claim(new_status):
            claim = selected_claim()

            if claim is None:
                messagebox.showerror(
                    "Claim Not Found",
                    "The selected saved claim could not be found.",
                    parent=self.root
                )
                return

            claim_id = str(claim.get("id", ""))
            item_id = str(claim.get("item_id", "")).strip()

            if str(claim.get("status", "PENDING")).upper() != "PENDING":
                messagebox.showwarning(
                    "Claim Already Reviewed",
                    "Only pending claims can be reviewed.",
                    parent=self.root
                )
                return

            if not messagebox.askyesno(
                f"{new_status.title()} Claim",
                f"{new_status.title()} claim {claim_id}?",
                parent=self.root
            ):
                return

            claims = load_records(CLAIMS_FILE)
            items = load_records(ITEMS_FILE)

            matching_item = next(
                (
                    item for item in items
                    if self.item_id(item) == item_id
                ),
                None
            )

            if matching_item is None:
                messagebox.showerror(
                    "Item Not Found",
                    "The associated item record no longer exists.",
                    parent=self.root
                )
                return

            if new_status == "APPROVED":
                if self.review_status(matching_item) != "APPROVED":
                    messagebox.showerror(
                        "Report Not Approved",
                        "The associated item report must be approved first.",
                        parent=self.root
                    )
                    return

                if str(matching_item.get("status", "")).upper() != "FOUND":
                    messagebox.showerror(
                        "Item Unavailable",
                        "Only FOUND items can have an approved claim.",
                        parent=self.root
                    )
                    return

                other_approved = any(
                    str(other.get("item_id", "")).strip() == item_id
                    and str(other.get("id", "")) != claim_id
                    and str(other.get("status", "")).upper()
                    in ("APPROVED", "ACCEPTED")
                    for other in claims
                )

                if other_approved:
                    messagebox.showerror(
                        "Claim Already Approved",
                        "Another claim for this item has already been approved.",
                        parent=self.root
                    )
                    return

            for saved_claim in claims:
                if str(saved_claim.get("id", "")) == claim_id:
                    saved_claim["status"] = new_status
                    saved_claim["reviewed_at"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    saved_claim["reviewed_by"] = self.current_user.get("email")
                    break

            if new_status == "APPROVED":
                # Save item state and claim state together where possible.
                matching_item["status"] = "CLAIMED"
                matching_item["claimed_at"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                if not save_records(ITEMS_FILE, items):
                    return

                if not save_records(CLAIMS_FILE, claims):
                    messagebox.showwarning(
                        "Partial Update",
                        "The item was marked claimed, but the claim status "
                        "could not be saved. Check the JSON files.",
                        parent=self.root
                    )
                    return
            else:
                if not save_records(CLAIMS_FILE, claims):
                    return

            messagebox.showinfo(
                "Claim Updated",
                f"Claim {claim_id} is now {new_status}.",
                parent=self.root
            )
            refresh()

        controls = tk.Frame(main, bg=BG)
        controls.pack(fill="x", pady=(5, 0))

        self.make_button(
            controls, "View Explanation", view_details, primary=False
        ).pack(side="left", padx=(0, 8))

        self.make_button(
            controls, "Approve Claim",
            lambda: decide_claim("APPROVED")
        ).pack(side="left", padx=8)

        self.make_button(
            controls, "Reject Claim",
            lambda: decide_claim("REJECTED")
        ).pack(side="left", padx=8)

        self.make_button(
            controls, "Refresh", refresh, primary=False
        ).pack(side="left", padx=8)

        self.make_button(
            controls, "Admin Dashboard", self.open_admin_dashboard,
            primary=False
        ).pack(side="right")

        status_box.bind(
            "<<ComboboxSelected>>", lambda event: refresh()
        )
        tree.bind("<Double-1>", lambda event: view_details())
        refresh()

    def build_admin_claim_details(self, claim):
        self.create_header(
            self.screen_frame,
            "Claim Review Details",
            "Read the student's ownership explanation before deciding."
        )

        content = self.page_content(25)
        card = self.make_card(content, 20)
        card.pack(fill="x")

        details = [
            ("Claim ID", claim.get("id", "")),
            ("Item ID", claim.get("item_id", "")),
            ("Item Name", claim.get("item_name", "")),
            ("Claimant", claim.get("claimant_name", "")),
            ("Claimant Email", claim.get("claimant_email", "")),
            ("Status", claim.get("status", "PENDING")),
            ("Submitted At", claim.get("created_at", "")),
            ("Reviewed At", claim.get("reviewed_at", "Not reviewed yet"))
        ]

        for label, value in details:
            row = tk.Frame(card, bg=WHITE)
            row.pack(fill="x", pady=5)

            tk.Label(
                row, text=f"{label}:",
                font=FONT_BOLD, bg=WHITE, fg=PLUM,
                width=17, anchor="w"
            ).pack(side="left")

            tk.Label(
                row, text=str(value),
                font=FONT, bg=WHITE, fg=TEXT,
                wraplength=650, justify="left", anchor="w"
            ).pack(side="left", fill="x", expand=True)

        tk.Label(
            content, text="Ownership Explanation",
            font=FONT_BOLD, bg=BG, fg=PLUM
        ).pack(anchor="w", pady=(18, 5))

        explanation = tk.Text(
            content, height=7, font=FONT, wrap="word",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER
        )
        explanation.pack(fill="x")
        explanation.insert("1.0", claim.get("explanation", ""))
        explanation.configure(state="disabled")

        self.make_button(
            content, "Back to Claims",
            self.open_admin_claims, primary=False
        ).pack(fill="x", pady=(15, 8))

        self.make_button(
            content, "Admin Dashboard",
            self.open_admin_dashboard
        ).pack(fill="x")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    ensure_storage()

    root = tk.Tk()
    app = CampusLostFoundApp(root)

    root.mainloop()
