import tkinter as tk
from tkinter import ttk

from src.gui.theme import AppTheme
from src.gui.components import AppCard


class RecommendationSettingsView(tk.Frame):
    """추천번호 생성 설정을 표시하는 독립 View."""

    WEIGHT_FIELDS = [
        ("frequency", "전체 빈도", 0.0, 1.0, 0.01),
        ("recent_30", "최근 30회", 0.0, 1.0, 0.01),
        ("recent_100", "최근 100회", 0.0, 1.0, 0.01),
        ("rising", "상승 점수", 0.0, 1.0, 0.01),
        ("missing", "장기 미출현", 0.0, 1.0, 0.01),
    ]
    COMBINATION_FIELDS = [
        ("pair", "Pair", 0.0, 0.1, 0.001),
        ("triple", "Triple", 0.0, 0.1, 0.001),
        ("pattern", "Pattern", 0.0, 5.0, 0.1),
    ]
    INTEGER_FIELDS = [
        ("set_count", "추천 세트 수"),
        ("candidate_pool_size", "Candidate Pool"),
        ("max_attempts", "최대 생성 시도"),
        ("max_overlap_count", "세트 간 최대 중복"),
        ("min_sum", "번호합 최소"),
        ("max_sum", "번호합 최대"),
        ("min_unique_digit_count", "최소 끝수 종류"),
        ("max_consecutive_pair_count", "연속번호 최대"),
    ]
    PATTERN_OPTIONS = ["6:0", "5:1", "4:2", "3:3", "2:4", "1:5", "0:6"]

    def __init__(self, parent, recommendation_service):
        super().__init__(parent, bg=AppTheme.CONTENT_BACKGROUND)
        self.recommendation_service = recommendation_service
        self.weight_vars = {}; self.weight_value_labels = {}
        self.combination_vars = {}; self.combination_value_labels = {}
        self.integer_vars = {}; self.odd_even_vars = {}; self.low_high_vars = {}
        self._build_ui(); self.load_current_settings()

    def _build_ui(self):
        body = tk.Frame(self, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)
        self._create_page_intro(body, "추천 설정", "추천번호 생성에 사용하는 가중치와 조건을 관리합니다.")

        action_card = AppCard(body); action_card.pack(fill="x", pady=(0, 12))
        action_info = tk.Frame(action_card, bg=AppTheme.CARD_BACKGROUND)
        action_info.pack(side="left", fill="both", expand=True, padx=18, pady=14)
        tk.Label(action_info, text="과거 데이터 기반 추천 전략 설정", font=AppTheme.FONT_CARD_TITLE,
                 fg=AppTheme.TEXT_PRIMARY, bg=AppTheme.CARD_BACKGROUND, anchor="w").pack(anchor="w")
        self.status_label = tk.Label(action_info, text="현재 설정을 불러왔습니다.", font=AppTheme.FONT_SMALL,
                                     fg=AppTheme.TEXT_SECONDARY, bg=AppTheme.CARD_BACKGROUND, anchor="w")
        self.status_label.pack(anchor="w", pady=(5, 0))

        button_area = tk.Frame(action_card, bg=AppTheme.CARD_BACKGROUND)
        button_area.pack(side="right", padx=18, pady=14)
        self.restore_button = ttk.Button(button_area, text="기본값", style="Secondary.TButton", state="disabled")
        self.restore_button.pack(side="left", padx=(0, 8))
        self.cancel_button = ttk.Button(button_area, text="취소", style="Secondary.TButton", state="disabled")
        self.cancel_button.pack(side="left", padx=(0, 8))
        self.save_button = ttk.Button(button_area, text="저장", style="Primary.TButton", state="disabled")
        self.save_button.pack(side="left")

        content_card = AppCard(body, title="추천 설정"); content_card.pack(fill="both", expand=True)
        content_body = tk.Frame(content_card, bg=AppTheme.CARD_BACKGROUND)
        content_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.canvas = tk.Canvas(content_body, bg=AppTheme.CARD_BACKGROUND, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(content_body, orient="vertical", command=self.canvas.yview)
        self.settings_frame = tk.Frame(self.canvas, bg=AppTheme.CARD_BACKGROUND)
        self.settings_window = self.canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True); self.scrollbar.pack(side="right", fill="y")
        self.settings_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._resize_settings_frame)

        self._create_weight_section(); self._create_combination_section(); self._create_condition_section(); self._create_pattern_section()
        tk.Label(self.settings_frame,
                 text="※ STEP16-1B-1에서는 화면과 현재 설정 표시만 제공하며, 저장 기능은 다음 단계에서 연결됩니다.",
                 font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_SECONDARY, bg=AppTheme.CARD_BACKGROUND,
                 anchor="w").pack(fill="x", pady=(0, 4))

    def _create_page_intro(self, parent, title, description):
        area = tk.Frame(parent, bg=AppTheme.CONTENT_BACKGROUND); area.pack(fill="x", pady=(0, 14))
        tk.Label(area, text=title, font=AppTheme.FONT_PAGE_TITLE, fg=AppTheme.TEXT_PRIMARY,
                 bg=AppTheme.CONTENT_BACKGROUND, anchor="w").pack(fill="x")
        tk.Label(area, text=description, font=AppTheme.FONT_BODY, fg=AppTheme.TEXT_SECONDARY,
                 bg=AppTheme.CONTENT_BACKGROUND, anchor="w").pack(fill="x", pady=(5, 0))

    def _create_section_card(self, title, description):
        card = tk.Frame(self.settings_frame, bg=AppTheme.CARD_BACKGROUND, highlightthickness=1,
                        highlightbackground=AppTheme.BORDER); card.pack(fill="x", pady=(0, 12))
        header = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND); header.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(header, text=title, font=AppTheme.FONT_CARD_TITLE, fg=AppTheme.TEXT_PRIMARY,
                 bg=AppTheme.CARD_BACKGROUND, anchor="w").pack(fill="x")
        tk.Label(header, text=description, font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_SECONDARY,
                 bg=AppTheme.CARD_BACKGROUND, anchor="w").pack(fill="x", pady=(4, 0))
        tk.Frame(card, bg=AppTheme.DIVIDER, height=1).pack(fill="x")
        content = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND); content.pack(fill="x", padx=16, pady=14)
        return content

    def _create_weight_section(self):
        content = self._create_section_card("기본 가중치", "번호별 기본 점수 계산에 반영되는 분석 항목별 가중치입니다.")
        for row, (key, label, minimum, maximum, resolution) in enumerate(self.WEIGHT_FIELDS):
            variable = tk.DoubleVar(value=0.0); self.weight_vars[key] = variable
            self._create_slider_row(content, row, label, variable, minimum, maximum, resolution,
                                    self.weight_value_labels, key)

    def _create_combination_section(self):
        content = self._create_section_card("조합 가중치", "추천 조합의 Pair, Triple, Pattern 점수 반영 비율입니다.")
        for row, (key, label, minimum, maximum, resolution) in enumerate(self.COMBINATION_FIELDS):
            variable = tk.DoubleVar(value=0.0); self.combination_vars[key] = variable
            self._create_slider_row(content, row, label, variable, minimum, maximum, resolution,
                                    self.combination_value_labels, key)

    def _create_slider_row(self, parent, row, label, variable, minimum, maximum, resolution, value_labels, key):
        parent.grid_columnconfigure(1, weight=1)
        tk.Label(parent, text=label, font=AppTheme.FONT_BODY_BOLD, fg=AppTheme.TEXT_PRIMARY,
                 bg=AppTheme.CARD_BACKGROUND, width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=7)
        scale = tk.Scale(parent, from_=minimum, to=maximum, resolution=resolution, orient="horizontal",
                         variable=variable, showvalue=False, bg=AppTheme.CARD_BACKGROUND, fg=AppTheme.TEXT_PRIMARY,
                         troughcolor=AppTheme.PROGRESS_TRACK, activebackground=AppTheme.PRIMARY,
                         highlightthickness=0, bd=0, sliderlength=18, length=420)
        scale.grid(row=row, column=1, sticky="ew", padx=(10, 12), pady=4)
        value_label = tk.Label(parent, text="0", font=AppTheme.FONT_BODY_BOLD, fg=AppTheme.PRIMARY,
                               bg=AppTheme.CARD_BACKGROUND, width=8, anchor="e")
        value_label.grid(row=row, column=2, sticky="e"); value_labels[key] = value_label
        variable.trace_add("write", lambda *_args, var=variable, target=value_label:
                           target.config(text=self._format_float(var.get())))

    def _create_condition_section(self):
        content = self._create_section_card("추천 조건", "추천 세트 생성 범위와 조합 필터 조건입니다.")
        for column in range(4): content.grid_columnconfigure(column, weight=1 if column in (1, 3) else 0)
        for index, (key, label) in enumerate(self.INTEGER_FIELDS):
            row = index // 2; group_column = (index % 2) * 2
            tk.Label(content, text=label, font=AppTheme.FONT_BODY_BOLD, fg=AppTheme.TEXT_PRIMARY,
                     bg=AppTheme.CARD_BACKGROUND, anchor="w").grid(row=row, column=group_column, sticky="w",
                                                                    padx=(0 if group_column == 0 else 20, 10), pady=8)
            variable = tk.StringVar(); self.integer_vars[key] = variable
            entry = tk.Entry(content, textvariable=variable, font=AppTheme.FONT_BODY, bg=AppTheme.INPUT_BACKGROUND,
                             fg=AppTheme.TEXT_PRIMARY, insertbackground=AppTheme.TEXT_PRIMARY, relief="flat",
                             justify="right", highlightthickness=1, highlightbackground=AppTheme.BORDER,
                             highlightcolor=AppTheme.PRIMARY)
            entry.grid(row=row, column=group_column + 1, sticky="ew", padx=(0, 6), pady=8, ipady=7)

    def _create_pattern_section(self):
        content = self._create_section_card("허용 패턴", "추천번호 생성 시 허용할 홀짝 및 고저 패턴을 선택합니다.")
        content.grid_columnconfigure(0, weight=1); content.grid_columnconfigure(1, weight=1)
        self._create_pattern_group(content, "홀짝 패턴", self.odd_even_vars).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._create_pattern_group(content, "고저 패턴", self.low_high_vars).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    def _create_pattern_group(self, parent, title, variable_map):
        frame = tk.Frame(parent, bg=AppTheme.INPUT_BACKGROUND, highlightthickness=1, highlightbackground=AppTheme.BORDER)
        tk.Label(frame, text=title, font=AppTheme.FONT_BODY_BOLD, fg=AppTheme.TEXT_PRIMARY,
                 bg=AppTheme.INPUT_BACKGROUND, anchor="w").pack(fill="x", padx=14, pady=(12, 8))
        options = tk.Frame(frame, bg=AppTheme.INPUT_BACKGROUND); options.pack(fill="x", padx=10, pady=(0, 12))
        for index, pattern in enumerate(self.PATTERN_OPTIONS):
            variable = tk.BooleanVar(value=False); variable_map[pattern] = variable
            tk.Checkbutton(options, text=pattern, variable=variable, font=AppTheme.FONT_BODY,
                           fg=AppTheme.TEXT_PRIMARY, bg=AppTheme.INPUT_BACKGROUND,
                           activeforeground=AppTheme.TEXT_PRIMARY, activebackground=AppTheme.INPUT_BACKGROUND,
                           selectcolor=AppTheme.CARD_BACKGROUND, highlightthickness=0, bd=0).grid(
                               row=index // 4, column=index % 4, sticky="w", padx=6, pady=4)
        return frame

    def _resize_settings_frame(self, event):
        self.canvas.itemconfigure(self.settings_window, width=event.width)

    def handle_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_current_settings(self):
        try:
            settings = self.recommendation_service.get_recommendation_settings()
            self.set_settings(settings)
            self.status_label.config(text="현재 저장된 추천 설정을 불러왔습니다.", fg=AppTheme.SUCCESS)
        except Exception as error:
            self.status_label.config(text=f"설정을 불러오지 못했습니다: {error}", fg=AppTheme.ERROR)

    def set_settings(self, settings):
        for key, value in settings["weights"].items():
            if key in self.weight_vars: self.weight_vars[key].set(value)
        for key, value in settings["combination_weights"].items():
            if key in self.combination_vars: self.combination_vars[key].set(value)
        final_settings = settings["final_settings"]; conditions = settings["conditions"]
        integer_values = {
            "set_count": final_settings["set_count"], "candidate_pool_size": final_settings["candidate_pool_size"],
            "max_attempts": final_settings["max_attempts"], "max_overlap_count": final_settings["max_overlap_count"],
            "min_sum": conditions["min_sum"], "max_sum": conditions["max_sum"],
            "min_unique_digit_count": conditions["min_unique_digit_count"],
            "max_consecutive_pair_count": conditions["max_consecutive_pair_count"],
        }
        for key, value in integer_values.items(): self.integer_vars[key].set(str(value))
        allowed_odd_even = set(conditions["allowed_odd_even_patterns"])
        allowed_low_high = set(conditions["allowed_low_high_patterns"])
        for pattern, variable in self.odd_even_vars.items(): variable.set(pattern in allowed_odd_even)
        for pattern, variable in self.low_high_vars.items(): variable.set(pattern in allowed_low_high)
        self.canvas.update_idletasks(); self.canvas.yview_moveto(0)

    def _format_float(self, value):
        return f"{value:.3f}" if abs(value) < 0.1 else f"{value:.2f}"
