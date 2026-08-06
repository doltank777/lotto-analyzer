import copy
import tkinter as tk
from tkinter import messagebox, ttk

from src.gui.theme import AppTheme
from src.gui.components import AppCard


class RecommendationSettingsView(tk.Frame):
    """추천번호 생성 설정을 조회하고 저장하는 독립 View."""

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

    PATTERN_OPTIONS = [
        "6:0",
        "5:1",
        "4:2",
        "3:3",
        "2:4",
        "1:5",
        "0:6",
    ]

    INTEGER_FIELD_LABELS = dict(INTEGER_FIELDS)

    def __init__(
        self,
        parent,
        recommendation_service,
        on_log=None,
        on_status=None,
    ):
        super().__init__(parent, bg=AppTheme.CONTENT_BACKGROUND)

        self.recommendation_service = recommendation_service
        self.on_log = on_log
        self.on_status = on_status

        self.weight_vars = {}
        self.weight_value_labels = {}
        self.combination_vars = {}
        self.combination_value_labels = {}
        self.integer_vars = {}
        self.odd_even_vars = {}
        self.low_high_vars = {}

        self.saved_settings = None
        self.is_loading = False
        self.is_dirty = False

        self._build_ui()
        self._bind_change_tracking()
        self.load_current_settings()

    def _build_ui(self):
        body = tk.Frame(self, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self._create_page_intro(
            body,
            "추천 설정",
            "추천번호 생성에 사용하는 가중치와 조건을 관리합니다.",
        )

        action_card = AppCard(body)
        action_card.pack(fill="x", pady=(0, 12))

        action_info = tk.Frame(
            action_card,
            bg=AppTheme.CARD_BACKGROUND,
        )
        action_info.pack(
            side="left",
            fill="both",
            expand=True,
            padx=18,
            pady=14,
        )

        tk.Label(
            action_info,
            text="과거 데이터 기반 추천 전략 설정",
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(anchor="w")

        self.status_label = tk.Label(
            action_info,
            text="현재 설정을 불러오고 있습니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        )
        self.status_label.pack(anchor="w", pady=(5, 0))

        button_area = tk.Frame(
            action_card,
            bg=AppTheme.CARD_BACKGROUND,
        )
        button_area.pack(side="right", padx=18, pady=14)

        self.restore_button = ttk.Button(
            button_area,
            text="기본값",
            style="Secondary.TButton",
            command=self.restore_defaults,
        )
        self.restore_button.pack(side="left", padx=(0, 8))

        self.cancel_button = ttk.Button(
            button_area,
            text="취소",
            style="Secondary.TButton",
            command=self.cancel_changes,
        )
        self.cancel_button.pack(side="left", padx=(0, 8))

        self.save_button = ttk.Button(
            button_area,
            text="저장",
            style="Primary.TButton",
            command=self.save_settings,
        )
        self.save_button.pack(side="left")

        content_card = AppCard(body, title="추천 설정")
        content_card.pack(fill="both", expand=True)

        content_body = tk.Frame(
            content_card,
            bg=AppTheme.CARD_BACKGROUND,
        )
        content_body.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18),
        )

        self.canvas = tk.Canvas(
            content_body,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=0,
            borderwidth=0,
        )
        self.scrollbar = ttk.Scrollbar(
            content_body,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.settings_frame = tk.Frame(
            self.canvas,
            bg=AppTheme.CARD_BACKGROUND,
        )

        self.settings_window = self.canvas.create_window(
            (0, 0),
            window=self.settings_frame,
            anchor="nw",
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.settings_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas.bind(
            "<Configure>",
            self._resize_settings_frame,
        )

        self._create_weight_section()
        self._create_combination_section()
        self._create_condition_section()
        self._create_pattern_section()

        tk.Label(
            self.settings_frame,
            text=(
                "※ 저장한 설정은 다음 추천번호 생성부터 즉시 반영됩니다. "
                "recommendation_config.py의 기본값은 변경되지 않습니다."
            ),
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

    def _create_page_intro(self, parent, title, description):
        area = tk.Frame(parent, bg=AppTheme.CONTENT_BACKGROUND)
        area.pack(fill="x", pady=(0, 14))

        tk.Label(
            area,
            text=title,
            font=AppTheme.FONT_PAGE_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            area,
            text=description,
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w",
        ).pack(fill="x", pady=(5, 0))

    def _create_section_card(self, title, description):
        card = tk.Frame(
            self.settings_frame,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
        )
        card.pack(fill="x", pady=(0, 12))

        header = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND)
        header.pack(fill="x", padx=16, pady=(14, 10))

        tk.Label(
            header,
            text=title,
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            header,
            text=description,
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        tk.Frame(
            card,
            bg=AppTheme.DIVIDER,
            height=1,
        ).pack(fill="x")

        content = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND)
        content.pack(fill="x", padx=16, pady=14)

        return content

    def _create_weight_section(self):
        content = self._create_section_card(
            "기본 가중치",
            "번호별 기본 점수 계산에 반영되는 분석 항목별 가중치입니다.",
        )

        for row, (
            key,
            label,
            minimum,
            maximum,
            resolution,
        ) in enumerate(self.WEIGHT_FIELDS):
            variable = tk.DoubleVar(value=0.0)
            self.weight_vars[key] = variable

            self._create_slider_row(
                content,
                row,
                label,
                variable,
                minimum,
                maximum,
                resolution,
                self.weight_value_labels,
                key,
            )

    def _create_combination_section(self):
        content = self._create_section_card(
            "조합 가중치",
            "추천 조합의 Pair, Triple, Pattern 점수 반영 비율입니다.",
        )

        for row, (
            key,
            label,
            minimum,
            maximum,
            resolution,
        ) in enumerate(self.COMBINATION_FIELDS):
            variable = tk.DoubleVar(value=0.0)
            self.combination_vars[key] = variable

            self._create_slider_row(
                content,
                row,
                label,
                variable,
                minimum,
                maximum,
                resolution,
                self.combination_value_labels,
                key,
            )

    def _create_slider_row(
        self,
        parent,
        row,
        label,
        variable,
        minimum,
        maximum,
        resolution,
        value_labels,
        key,
    ):
        parent.grid_columnconfigure(1, weight=1)

        tk.Label(
            parent,
            text=label,
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            width=18,
            anchor="w",
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=7,
        )

        scale = tk.Scale(
            parent,
            from_=minimum,
            to=maximum,
            resolution=resolution,
            orient="horizontal",
            variable=variable,
            showvalue=False,
            bg=AppTheme.CARD_BACKGROUND,
            fg=AppTheme.TEXT_PRIMARY,
            troughcolor=AppTheme.PROGRESS_TRACK,
            activebackground=AppTheme.PRIMARY,
            highlightthickness=0,
            bd=0,
            sliderlength=18,
            length=420,
        )
        scale.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(10, 12),
            pady=4,
        )

        value_label = tk.Label(
            parent,
            text="0",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            width=8,
            anchor="e",
        )
        value_label.grid(
            row=row,
            column=2,
            sticky="e",
        )
        value_labels[key] = value_label

        variable.trace_add(
            "write",
            lambda *_args, var=variable, target=value_label: (
                target.config(text=self._format_float(var.get()))
            ),
        )

    def _create_condition_section(self):
        content = self._create_section_card(
            "추천 조건",
            "추천 세트 생성 범위와 조합 필터 조건입니다.",
        )

        for column in range(4):
            content.grid_columnconfigure(
                column,
                weight=1 if column in (1, 3) else 0,
            )

        for index, (key, label) in enumerate(self.INTEGER_FIELDS):
            row = index // 2
            group_column = (index % 2) * 2

            tk.Label(
                content,
                text=label,
                font=AppTheme.FONT_BODY_BOLD,
                fg=AppTheme.TEXT_PRIMARY,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w",
            ).grid(
                row=row,
                column=group_column,
                sticky="w",
                padx=(0 if group_column == 0 else 20, 10),
                pady=8,
            )

            variable = tk.StringVar()
            self.integer_vars[key] = variable

            entry = tk.Entry(
                content,
                textvariable=variable,
                font=AppTheme.FONT_BODY,
                bg=AppTheme.INPUT_BACKGROUND,
                fg=AppTheme.TEXT_PRIMARY,
                insertbackground=AppTheme.TEXT_PRIMARY,
                relief="flat",
                justify="right",
                highlightthickness=1,
                highlightbackground=AppTheme.BORDER,
                highlightcolor=AppTheme.PRIMARY,
            )
            entry.grid(
                row=row,
                column=group_column + 1,
                sticky="ew",
                padx=(0, 6),
                pady=8,
                ipady=7,
            )

    def _create_pattern_section(self):
        content = self._create_section_card(
            "허용 패턴",
            "추천번호 생성 시 허용할 홀짝 및 고저 패턴을 선택합니다.",
        )

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        odd_even_frame = self._create_pattern_group(
            content,
            "홀짝 패턴",
            self.odd_even_vars,
        )
        odd_even_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        low_high_frame = self._create_pattern_group(
            content,
            "고저 패턴",
            self.low_high_vars,
        )
        low_high_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )

    def _create_pattern_group(self, parent, title, variable_map):
        frame = tk.Frame(
            parent,
            bg=AppTheme.INPUT_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
        )

        tk.Label(
            frame,
            text=title,
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.INPUT_BACKGROUND,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 8))

        options = tk.Frame(
            frame,
            bg=AppTheme.INPUT_BACKGROUND,
        )
        options.pack(fill="x", padx=10, pady=(0, 12))

        for index, pattern in enumerate(self.PATTERN_OPTIONS):
            variable = tk.BooleanVar(value=False)
            variable_map[pattern] = variable

            checkbox = tk.Checkbutton(
                options,
                text=pattern,
                variable=variable,
                font=AppTheme.FONT_BODY,
                fg=AppTheme.TEXT_PRIMARY,
                bg=AppTheme.INPUT_BACKGROUND,
                activeforeground=AppTheme.TEXT_PRIMARY,
                activebackground=AppTheme.INPUT_BACKGROUND,
                selectcolor=AppTheme.CARD_BACKGROUND,
                highlightthickness=0,
                bd=0,
            )
            checkbox.grid(
                row=index // 4,
                column=index % 4,
                sticky="w",
                padx=6,
                pady=4,
            )

        return frame

    def _bind_change_tracking(self):
        all_variables = [
            *self.weight_vars.values(),
            *self.combination_vars.values(),
            *self.integer_vars.values(),
            *self.odd_even_vars.values(),
            *self.low_high_vars.values(),
        ]

        for variable in all_variables:
            variable.trace_add(
                "write",
                self._handle_setting_changed,
            )

    def _handle_setting_changed(self, *_args):
        if self.is_loading:
            return

        self.is_dirty = True
        self.status_label.config(
            text="변경된 설정이 저장되지 않았습니다.",
            fg=AppTheme.WARNING,
        )

    def _resize_settings_frame(self, event):
        self.canvas.itemconfigure(
            self.settings_window,
            width=event.width,
        )

    def handle_mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units",
        )

    def load_current_settings(self):
        try:
            settings = (
                self.recommendation_service
                .get_recommendation_settings()
            )
            self.saved_settings = copy.deepcopy(settings)
            self.set_settings(settings)
            self.is_dirty = False

            self.status_label.config(
                text="현재 저장된 추천 설정을 불러왔습니다.",
                fg=AppTheme.SUCCESS,
            )
        except Exception as error:
            self.status_label.config(
                text=f"설정을 불러오지 못했습니다: {error}",
                fg=AppTheme.ERROR,
            )
            self._write_log(
                f"추천 설정 불러오기 오류 [{type(error).__name__}]: "
                f"{error}",
                "ERROR",
            )

    def set_settings(self, settings):
        self.is_loading = True

        try:
            for key, value in settings["weights"].items():
                if key in self.weight_vars:
                    self.weight_vars[key].set(value)

            for key, value in settings[
                "combination_weights"
            ].items():
                if key in self.combination_vars:
                    self.combination_vars[key].set(value)

            final_settings = settings["final_settings"]
            conditions = settings["conditions"]

            integer_values = {
                "set_count": final_settings["set_count"],
                "candidate_pool_size": final_settings[
                    "candidate_pool_size"
                ],
                "max_attempts": final_settings["max_attempts"],
                "max_overlap_count": final_settings[
                    "max_overlap_count"
                ],
                "min_sum": conditions["min_sum"],
                "max_sum": conditions["max_sum"],
                "min_unique_digit_count": conditions[
                    "min_unique_digit_count"
                ],
                "max_consecutive_pair_count": conditions[
                    "max_consecutive_pair_count"
                ],
            }

            for key, value in integer_values.items():
                self.integer_vars[key].set(str(value))

            allowed_odd_even = set(
                conditions["allowed_odd_even_patterns"]
            )
            allowed_low_high = set(
                conditions["allowed_low_high_patterns"]
            )

            for pattern, variable in self.odd_even_vars.items():
                variable.set(pattern in allowed_odd_even)

            for pattern, variable in self.low_high_vars.items():
                variable.set(pattern in allowed_low_high)
        finally:
            self.is_loading = False

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)

    def collect_settings(self):
        integer_values = {}

        for key, variable in self.integer_vars.items():
            raw_value = variable.get().strip()
            label = self.INTEGER_FIELD_LABELS[key]

            if not raw_value:
                raise ValueError(f"{label} 값을 입력해주세요.")

            try:
                integer_values[key] = int(raw_value)
            except ValueError as error:
                raise ValueError(
                    f"{label} 값은 정수로 입력해주세요."
                ) from error

        allowed_odd_even = [
            pattern
            for pattern, variable in self.odd_even_vars.items()
            if variable.get()
        ]
        allowed_low_high = [
            pattern
            for pattern, variable in self.low_high_vars.items()
            if variable.get()
        ]

        if not allowed_odd_even:
            raise ValueError(
                "홀짝 허용 패턴을 하나 이상 선택해주세요."
            )

        if not allowed_low_high:
            raise ValueError(
                "고저 허용 패턴을 하나 이상 선택해주세요."
            )

        return {
            "weights": {
                key: round(variable.get(), 4)
                for key, variable in self.weight_vars.items()
            },
            "combination_weights": {
                key: round(variable.get(), 4)
                for key, variable in self.combination_vars.items()
            },
            "final_settings": {
                "set_count": integer_values["set_count"],
                "candidate_pool_size": integer_values[
                    "candidate_pool_size"
                ],
                "max_attempts": integer_values["max_attempts"],
                "max_overlap_count": integer_values[
                    "max_overlap_count"
                ],
            },
            "conditions": {
                "allowed_odd_even_patterns": allowed_odd_even,
                "allowed_low_high_patterns": allowed_low_high,
                "min_sum": integer_values["min_sum"],
                "max_sum": integer_values["max_sum"],
                "min_unique_digit_count": integer_values[
                    "min_unique_digit_count"
                ],
                "max_consecutive_pair_count": integer_values[
                    "max_consecutive_pair_count"
                ],
            },
        }

    def save_settings(self):
        try:
            settings = self.collect_settings()
            saved_settings = (
                self.recommendation_service
                .save_recommendation_settings(settings)
            )

            self.saved_settings = copy.deepcopy(saved_settings)
            self.set_settings(saved_settings)
            self.is_dirty = False

            self.status_label.config(
                text=(
                    "저장 완료 · 다음 추천번호 생성부터 "
                    "새 설정이 반영됩니다."
                ),
                fg=AppTheme.SUCCESS,
            )
            self._write_status("추천 설정 저장 완료")
            self._write_log("추천 설정 저장 완료", "SUCCESS")

            messagebox.showinfo(
                "추천 설정",
                "추천 설정을 저장했습니다.\n\n"
                "다음 추천번호 생성부터 새 설정이 반영됩니다.",
            )
        except ValueError as error:
            self.status_label.config(
                text=f"입력 오류 · {error}",
                fg=AppTheme.ERROR,
            )
            messagebox.showwarning(
                "입력 오류",
                str(error),
            )
        except Exception as error:
            self.status_label.config(
                text="오류 · 추천 설정 저장에 실패했습니다.",
                fg=AppTheme.ERROR,
            )
            self._write_status("추천 설정 저장 오류")
            self._write_log(
                f"추천 설정 저장 오류 [{type(error).__name__}]: "
                f"{error}",
                "ERROR",
            )
            messagebox.showerror(
                "오류",
                f"추천 설정 저장 중 오류가 발생했습니다.\n\n"
                f"{error}",
            )

    def cancel_changes(self):
        if self.saved_settings is None:
            self.load_current_settings()
            return

        if self.is_dirty:
            confirmed = messagebox.askyesno(
                "변경 취소",
                "저장하지 않은 변경 내용을 취소하시겠습니까?",
            )

            if not confirmed:
                return

        self.set_settings(copy.deepcopy(self.saved_settings))
        self.is_dirty = False

        self.status_label.config(
            text="변경 내용을 취소하고 저장된 설정으로 되돌렸습니다.",
            fg=AppTheme.TEXT_SECONDARY,
        )
        self._write_status("추천 설정 변경 취소")
        self._write_log("추천 설정 변경 취소", "INFO")

    def restore_defaults(self):
        confirmed = messagebox.askyesno(
            "기본값 복원",
            "추천 설정을 기본값으로 복원하시겠습니까?\n\n"
            "복원 즉시 JSON 설정 파일에 저장됩니다.",
        )

        if not confirmed:
            return

        try:
            restored_settings = (
                self.recommendation_service
                .restore_default_recommendation_settings()
            )

            self.saved_settings = copy.deepcopy(restored_settings)
            self.set_settings(restored_settings)
            self.is_dirty = False

            self.status_label.config(
                text="기본값 복원 완료 · 설정이 저장되었습니다.",
                fg=AppTheme.SUCCESS,
            )
            self._write_status("추천 설정 기본값 복원 완료")
            self._write_log(
                "추천 설정 기본값 복원 완료",
                "SUCCESS",
            )

            messagebox.showinfo(
                "기본값 복원",
                "추천 설정을 기본값으로 복원했습니다.",
            )
        except Exception as error:
            self.status_label.config(
                text="오류 · 기본값 복원에 실패했습니다.",
                fg=AppTheme.ERROR,
            )
            self._write_status("추천 설정 기본값 복원 오류")
            self._write_log(
                f"추천 설정 기본값 복원 오류 "
                f"[{type(error).__name__}]: {error}",
                "ERROR",
            )
            messagebox.showerror(
                "오류",
                f"기본값 복원 중 오류가 발생했습니다.\n\n"
                f"{error}",
            )

    def _write_log(self, message, level="INFO"):
        if callable(self.on_log):
            self.on_log(message, level)

    def _write_status(self, message):
        if callable(self.on_status):
            self.on_status(message)

    def _format_float(self, value):
        if abs(value) < 0.1:
            return f"{value:.3f}"

        return f"{value:.2f}"
