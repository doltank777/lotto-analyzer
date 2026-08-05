import tkinter as tk
import threading
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime

from src.app.recommendation_service import RecommendationService
from src.app.draw_search_service import DrawSearchService
from src.app.analysis_service import AnalysisService
from src.app.backtest_service import BacktestService
from src.gui.theme import AppTheme
from src.gui.components import (
    AppCard,
    EmptyState,
    LottoBall,
    MetricBadge,
    create_indeterminate_progress,
)


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{AppTheme.APP_NAME} ({AppTheme.VERSION})")
        self.root.geometry(f"{AppTheme.WINDOW_WIDTH}x{AppTheme.WINDOW_HEIGHT}")
        self.root.minsize(AppTheme.WINDOW_WIDTH, AppTheme.WINDOW_HEIGHT)
        self.root.configure(bg=AppTheme.APP_BACKGROUND)

        self.recommendation_service = RecommendationService()
        self.draw_search_service = DrawSearchService()
        self.analysis_service = AnalysisService()
        self.backtest_service = BacktestService()

        self.menu_buttons = {}
        self.views = {}
        self.current_view = None

        self.create_widgets()

    def create_widgets(self):
        self.create_styles()
        self.create_app_shell()
        self.create_sidebar()
        self.create_header()
        self.create_content_area()
        self.create_status_bar()
        self.create_views()
        self.show_view("recommend")

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Primary.TButton",
            font=AppTheme.FONT_BUTTON,
            padding=(18, 10),
            background=AppTheme.PRIMARY,
            foreground=AppTheme.TEXT_INVERSE,
            borderwidth=0,
            focusthickness=0
        )
        style.map(
            "Primary.TButton",
            background=[
                ("active", AppTheme.PRIMARY_HOVER),
                ("pressed", AppTheme.PRIMARY_PRESSED),
                ("disabled", "#B7C5DE")
            ],
            foreground=[("disabled", "#EEF2F7")]
        )

        style.configure(
            "Secondary.TButton",
            font=AppTheme.FONT_BUTTON,
            padding=(14, 8),
            background=AppTheme.CARD_BACKGROUND,
            foreground=AppTheme.TEXT_PRIMARY,
            bordercolor=AppTheme.BORDER,
            borderwidth=1,
            focusthickness=0
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#F7F9FC"), ("pressed", "#EEF2F7")]
        )

        style.configure(
            "Recommendation.Horizontal.TProgressbar",
            troughcolor=AppTheme.PROGRESS_TRACK,
            background=AppTheme.PRIMARY,
            bordercolor=AppTheme.PROGRESS_TRACK,
            lightcolor=AppTheme.PRIMARY,
            darkcolor=AppTheme.PRIMARY,
            thickness=5
        )

    def create_app_shell(self):
        self.app_shell = tk.Frame(self.root, bg=AppTheme.APP_BACKGROUND)
        self.app_shell.pack(fill="both", expand=True)

        self.app_shell.grid_rowconfigure(1, weight=1)
        self.app_shell.grid_columnconfigure(1, weight=1)

    def create_sidebar(self):
        self.sidebar = tk.Frame(
            self.app_shell,
            bg=AppTheme.SIDEBAR_BACKGROUND,
            width=AppTheme.SIDEBAR_WIDTH
        )
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand = tk.Frame(self.sidebar, bg=AppTheme.SIDEBAR_BACKGROUND)
        brand.pack(fill="x", padx=20, pady=(24, 28))

        tk.Label(
            brand,
            text="LA",
            font=(AppTheme.FONT_FAMILY, 16, "bold"),
            fg=AppTheme.TEXT_INVERSE,
            bg=AppTheme.PRIMARY,
            width=3,
            height=1
        ).pack(side="left")

        brand_text = tk.Frame(brand, bg=AppTheme.SIDEBAR_BACKGROUND)
        brand_text.pack(side="left", padx=(10, 0))

        tk.Label(
            brand_text,
            text="LOTTO",
            font=(AppTheme.FONT_FAMILY, 11, "bold"),
            fg=AppTheme.TEXT_INVERSE,
            bg=AppTheme.SIDEBAR_BACKGROUND,
            anchor="w"
        ).pack(anchor="w")

        tk.Label(
            brand_text,
            text="ANALYZER",
            font=(AppTheme.FONT_FAMILY, 8),
            fg="#AAB5C8",
            bg=AppTheme.SIDEBAR_BACKGROUND,
            anchor="w"
        ).pack(anchor="w")

        menu_items = [
            ("recommend", "추천번호"),
            ("analysis", "통계분석"),
            ("backtest", "백테스트"),
            ("draw_search", "회차조회"),
            ("log", "시스템로그"),
        ]

        for key, label in menu_items:
            button = tk.Button(
                self.sidebar,
                text=f"  {label}",
                font=AppTheme.FONT_MENU,
                fg="#C6CFDC",
                bg=AppTheme.SIDEBAR_BACKGROUND,
                activeforeground=AppTheme.TEXT_INVERSE,
                activebackground=AppTheme.SIDEBAR_HOVER,
                relief="flat",
                bd=0,
                anchor="w",
                padx=22,
                pady=13,
                cursor="hand2",
                command=lambda view_key=key: self.show_view(view_key)
            )
            button.pack(fill="x", padx=10, pady=2)
            button.bind("<Enter>", lambda event, b=button, k=key: self.on_menu_enter(b, k))
            button.bind("<Leave>", lambda event, b=button, k=key: self.on_menu_leave(b, k))
            self.menu_buttons[key] = button

        footer = tk.Frame(self.sidebar, bg=AppTheme.SIDEBAR_BACKGROUND)
        footer.pack(side="bottom", fill="x", padx=20, pady=20)

        tk.Label(
            footer,
            text=f"Version {AppTheme.VERSION}",
            font=AppTheme.FONT_SMALL,
            fg="#7F8CA3",
            bg=AppTheme.SIDEBAR_BACKGROUND,
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            footer,
            text="Developer  Y.YB",
            font=AppTheme.FONT_SMALL,
            fg="#7F8CA3",
            bg=AppTheme.SIDEBAR_BACKGROUND,
            anchor="w"
        ).pack(fill="x", pady=(3, 0))

    def create_header(self):
        self.header = tk.Frame(
            self.app_shell,
            bg=AppTheme.HEADER_BACKGROUND,
            height=78,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER
        )
        self.header.grid(row=0, column=1, sticky="ew")
        self.header.grid_propagate(False)

        title_area = tk.Frame(self.header, bg=AppTheme.HEADER_BACKGROUND)
        title_area.pack(side="left", fill="both", expand=True, padx=26, pady=15)

        self.header_title = tk.Label(
            title_area,
            text="추천번호",
            font=AppTheme.FONT_APP_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.HEADER_BACKGROUND,
            anchor="w"
        )
        self.header_title.pack(anchor="w")

        self.header_description = tk.Label(
            title_area,
            text="과거 당첨 데이터 기반 통계 분석 후 추천번호를 생성합니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.HEADER_BACKGROUND,
            anchor="w"
        )
        self.header_description.pack(anchor="w", pady=(4, 0))

        info_area = tk.Frame(self.header, bg=AppTheme.HEADER_BACKGROUND)
        info_area.pack(side="right", padx=26)

        tk.Label(
            info_area,
            text="DATA READY",
            font=(AppTheme.FONT_FAMILY, 8, "bold"),
            fg=AppTheme.SUCCESS,
            bg="#EAF8F2",
            padx=10,
            pady=5
        ).pack()

    def create_content_area(self):
        self.content_area = tk.Frame(self.app_shell, bg=AppTheme.CONTENT_BACKGROUND)
        self.content_area.grid(row=1, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.app_shell,
            text="●  Lotto Analyzer 준비 완료 | DB 연결 정상",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.HEADER_BACKGROUND,
            anchor="w",
            padx=20,
            pady=8,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER
        )
        self.status_bar.grid(row=2, column=1, sticky="ew")

    def create_views(self):
        self.create_recommend_view()
        self.create_analysis_view()
        self.create_backtest_view()
        self.create_draw_search_view()
        self.create_log_view()

    def create_view_frame(self, key):
        frame = tk.Frame(self.content_area, bg=AppTheme.CONTENT_BACKGROUND)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.views[key] = frame
        return frame

    def create_card(self, parent, title=None):
        return AppCard(parent, title=title)

    def create_page_intro(self, parent, title, description):
        area = tk.Frame(parent, bg=AppTheme.CONTENT_BACKGROUND)
        area.pack(fill="x", pady=(0, 14))

        tk.Label(
            area,
            text=title,
            font=AppTheme.FONT_PAGE_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            area,
            text=description,
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w"
        ).pack(fill="x", pady=(5, 0))

    def configure_text_widget(self, widget):
        widget.configure(**AppTheme.text_widget_options())

    def create_recommend_view(self):
        view = self.create_view_frame("recommend")
        body = tk.Frame(view, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self.create_page_intro(
            body,
            "최종 추천번호",
            "저장된 과거 당첨 데이터를 종합 분석하여 추천번호 5세트를 생성합니다."
        )

        action_card = self.create_card(body)
        action_card.pack(fill="x", pady=(0, 14))

        action_info = tk.Frame(action_card, bg=AppTheme.CARD_BACKGROUND)
        action_info.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            action_info,
            text="과거 데이터 기반 추천번호 생성",
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(anchor="w")

        self.recommend_status_label = tk.Label(
            action_info,
            text="대기 중 · 분석 준비 완료",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.recommend_status_label.pack(anchor="w", pady=(5, 0))

        self.generate_button = ttk.Button(
            action_card,
            text="추천번호 생성",
            style="Primary.TButton",
            command=self.generate_recommendations
        )
        self.generate_button.pack(side="right", padx=18, pady=15)

        self.recommend_progress = create_indeterminate_progress(
            body,
            style="Recommendation.Horizontal.TProgressbar"
        )

        result_card = self.create_card(body, "추천 조합")
        result_card.pack(fill="both", expand=True)

        result_body = tk.Frame(result_card, bg=AppTheme.CARD_BACKGROUND)
        result_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.recommend_canvas = tk.Canvas(
            result_body,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=0,
            borderwidth=0
        )
        self.recommend_scrollbar = ttk.Scrollbar(
            result_body,
            orient="vertical",
            command=self.recommend_canvas.yview
        )
        self.recommend_cards_frame = tk.Frame(
            self.recommend_canvas,
            bg=AppTheme.CARD_BACKGROUND
        )

        self.recommend_cards_window = self.recommend_canvas.create_window(
            (0, 0),
            window=self.recommend_cards_frame,
            anchor="nw"
        )
        self.recommend_canvas.configure(yscrollcommand=self.recommend_scrollbar.set)

        self.recommend_canvas.pack(side="left", fill="both", expand=True)
        self.recommend_scrollbar.pack(side="right", fill="y")

        self.recommend_cards_frame.bind(
            "<Configure>",
            lambda event: self.recommend_canvas.configure(
                scrollregion=self.recommend_canvas.bbox("all")
            )
        )
        self.recommend_canvas.bind("<Configure>", self._resize_recommend_cards_frame)
        self.recommend_canvas.bind_all("<MouseWheel>", self._on_recommend_mousewheel)

        self.show_recommend_empty_state()

    def _resize_recommend_cards_frame(self, event):
        self.recommend_canvas.itemconfigure(
            self.recommend_cards_window,
            width=event.width
        )

    def _on_recommend_mousewheel(self, event):
        if self.current_view == "recommend":
            self.recommend_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear_recommendation_cards(self):
        for widget in self.recommend_cards_frame.winfo_children():
            widget.destroy()

    def show_recommend_empty_state(self, message="추천번호 생성 버튼을 눌러주세요."):
        self.clear_recommendation_cards()

        empty_state = EmptyState(
            self.recommend_cards_frame,
            message=message,
            description=(
                "과거 당첨 데이터의 출현빈도, 추세, 조합 및 패턴을 "
                "종합 분석합니다."
            ),
            icon_text="6"
        )
        empty_state.pack(fill="both", expand=True, pady=105)

    def create_lotto_ball(self, parent, number):
        ball = LottoBall(parent, number)
        ball.pack(side="left", padx=(0, 10))

    def create_metric(self, parent, label, value):
        metric = MetricBadge(parent, label, value)
        metric.pack(side="left", padx=(0, 8), ipadx=10, ipady=5)

    def create_recommendation_card(self, item):
        card = tk.Frame(
            self.recommend_cards_frame,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER
        )
        card.pack(fill="x", pady=(0, 10))

        accent = tk.Frame(card, bg=AppTheme.PRIMARY, width=4)
        accent.pack(side="left", fill="y")
        accent.pack_propagate(False)

        content = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND)
        content.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        top_row = tk.Frame(content, bg=AppTheme.CARD_BACKGROUND)
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text=f"추천 조합 {item['index']:02d}",
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack(side="left")

        score_frame = tk.Frame(top_row, bg=AppTheme.SCORE_BACKGROUND)
        score_frame.pack(side="right")

        tk.Label(
            score_frame,
            text="종합점수",
            font=(AppTheme.FONT_FAMILY, 8),
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SCORE_BACKGROUND
        ).pack(side="left", padx=(9, 5), pady=4)

        tk.Label(
            score_frame,
            text=f"{item['total_score']:.2f}",
            font=(AppTheme.FONT_FAMILY, 10, "bold"),
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SCORE_BACKGROUND
        ).pack(side="left", padx=(0, 9), pady=4)

        detail_row = tk.Frame(content, bg=AppTheme.CARD_BACKGROUND)
        detail_row.pack(fill="x", pady=(10, 0))

        balls = tk.Frame(detail_row, bg=AppTheme.CARD_BACKGROUND)
        balls.pack(side="left")
        for number in item["numbers"]:
            self.create_lotto_ball(balls, number)

        pattern = item["pattern"]
        metrics = tk.Frame(detail_row, bg=AppTheme.CARD_BACKGROUND)
        metrics.pack(side="right", pady=7)

        self.create_metric(metrics, "홀짝", pattern["odd_even"]["pattern"])
        self.create_metric(metrics, "고저", pattern["low_high"]["pattern"])
        self.create_metric(metrics, "번호합", pattern["sum"]["sum"])

    def create_analysis_view(self):
        view = self.create_view_frame("analysis")
        body = tk.Frame(view, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self.create_page_intro(
            body,
            "통계분석",
            "출현빈도, 추세, 동시 출현 조합, 장기 미출현 및 패턴 통계를 조회합니다."
        )

        action_card = self.create_card(body)
        action_card.pack(fill="x", pady=(0, 14))
        tk.Label(
            action_card,
            text="저장된 전체 회차를 기준으로 최신 통계 요약을 계산합니다.",
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack(side="left", padx=18, pady=16)

        self.analysis_button = ttk.Button(
            action_card,
            text="통계분석 실행",
            style="Primary.TButton",
            command=self.run_analysis_summary
        )
        self.analysis_button.pack(side="right", padx=18, pady=15)

        result_card = self.create_card(body, "통계분석 결과")
        result_card.pack(fill="both", expand=True)

        self.analysis_text = scrolledtext.ScrolledText(result_card, height=24)
        self.analysis_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.configure_text_widget(self.analysis_text)
        self.analysis_text.insert(tk.END, "통계분석 실행 버튼을 눌러주세요.\n")

    def create_backtest_view(self):
        view = self.create_view_frame("backtest")
        body = tk.Frame(view, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self.create_page_intro(
            body,
            "백테스트",
            "각 대상 회차 이전 데이터만 사용하여 추천번호 생성 결과를 검증합니다."
        )

        action_card = self.create_card(body)
        action_card.pack(fill="x", pady=(0, 14))
        tk.Label(
            action_card,
            text="최근 10회 기준 최종 추천번호 백테스트를 실행합니다.",
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack(side="left", padx=18, pady=16)

        self.backtest_button = ttk.Button(
            action_card,
            text="백테스트 실행",
            style="Primary.TButton",
            command=self.run_backtest
        )
        self.backtest_button.pack(side="right", padx=18, pady=15)

        result_card = self.create_card(body, "백테스트 결과")
        result_card.pack(fill="both", expand=True)

        self.backtest_text = scrolledtext.ScrolledText(result_card, height=24)
        self.backtest_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.configure_text_widget(self.backtest_text)
        self.backtest_text.insert(
            tk.END,
            "최근 10회 기준 백테스트를 실행할 수 있습니다.\n\n"
            "출력 항목\n- 평균 일치 개수\n- 최고 일치 개수\n- 번호 적중률\n"
            "- 등수 및 일치 개수 분포\n- 점수 구간별 결과\n"
        )

    def create_draw_search_view(self):
        view = self.create_view_frame("draw_search")
        body = tk.Frame(view, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self.create_page_intro(
            body,
            "회차조회",
            "저장된 과거 당첨번호 데이터에서 특정 회차의 당첨번호를 조회합니다."
        )

        search_card = self.create_card(body, "회차 검색")
        search_card.pack(fill="x", pady=(0, 14))

        search_row = tk.Frame(search_card, bg=AppTheme.CARD_BACKGROUND)
        search_row.pack(fill="x", padx=18, pady=(0, 18))

        tk.Label(
            search_row,
            text="조회 회차",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack(side="left")

        self.draw_no_entry = tk.Entry(
            search_row,
            width=18,
            font=AppTheme.FONT_BODY,
            bg=AppTheme.INPUT_BACKGROUND,
            fg=AppTheme.TEXT_PRIMARY,
            insertbackground=AppTheme.TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            highlightcolor=AppTheme.PRIMARY
        )
        self.draw_no_entry.pack(side="left", padx=(12, 8), ipady=7)
        self.draw_no_entry.bind("<Return>", lambda event: self.search_draw_number())

        search_button = ttk.Button(
            search_row,
            text="조회",
            style="Primary.TButton",
            command=self.search_draw_number
        )
        search_button.pack(side="left")

        result_card = self.create_card(body, "당첨번호 조회 결과")
        result_card.pack(fill="both", expand=True)

        self.draw_search_text = scrolledtext.ScrolledText(result_card, height=23)
        self.draw_search_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.configure_text_widget(self.draw_search_text)
        self.draw_search_text.insert(tk.END, "조회할 회차를 입력해주세요.\n")

    def create_log_view(self):
        view = self.create_view_frame("log")
        body = tk.Frame(view, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self.create_page_intro(
            body,
            "시스템로그",
            "프로그램 실행 상태와 각 기능의 처리 내역을 시간순으로 확인합니다."
        )

        result_card = self.create_card(body, "실행 로그")
        result_card.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(result_card, height=28)
        self.log_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.configure_text_widget(self.log_text)

        self.add_log("프로그램 시작")
        self.add_log("모던 GUI 디자인 시스템 초기화 완료")
        self.add_log("화면 및 Service 연결 완료")

    def show_view(self, key):
        if key not in self.views:
            return

        self.current_view = key
        self.views[key].tkraise()

        page_info = {
            "recommend": ("추천번호", "과거 당첨 데이터 기반 통계 분석 후 추천번호를 생성합니다."),
            "analysis": ("통계분석", "과거 당첨 데이터의 주요 통계와 패턴을 확인합니다."),
            "backtest": ("백테스트", "추천번호 생성 결과를 과거 회차 기준으로 검증합니다."),
            "draw_search": ("회차조회", "특정 회차의 당첨번호와 보너스번호를 조회합니다."),
            "log": ("시스템로그", "프로그램 실행 상태와 처리 내역을 확인합니다."),
        }

        title, description = page_info[key]
        self.header_title.config(text=title)
        self.header_description.config(text=description)

        for menu_key, button in self.menu_buttons.items():
            if menu_key == key:
                button.config(bg=AppTheme.SIDEBAR_ACTIVE, fg=AppTheme.TEXT_INVERSE)
            else:
                button.config(bg=AppTheme.SIDEBAR_BACKGROUND, fg="#C6CFDC")

    def on_menu_enter(self, button, key):
        if self.current_view != key:
            button.config(bg=AppTheme.SIDEBAR_HOVER, fg=AppTheme.TEXT_INVERSE)

    def on_menu_leave(self, button, key):
        if self.current_view != key:
            button.config(bg=AppTheme.SIDEBAR_BACKGROUND, fg="#C6CFDC")

    def run_analysis_summary(self):
        self.analysis_button.config(state="disabled")
        self.set_status("통계분석 실행 중...")
        self.add_log("통계분석 실행 시작")
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, "통계분석을 실행하고 있습니다...\n")

        threading.Thread(
            target=self._run_analysis_summary_worker,
            daemon=True
        ).start()

    def _run_analysis_summary_worker(self):
        try:
            summary = self.analysis_service.get_analysis_summary()
            self.root.after(0, self._display_analysis_summary, summary)
        except Exception as e:
            self.root.after(0, self._handle_analysis_error, e)

    def _display_analysis_summary(self, summary):
        self.analysis_text.delete("1.0", tk.END)

        self.analysis_text.insert(tk.END, "=" * 90 + "\n")
        self.analysis_text.insert(tk.END, "                    통계분석 결과\n")
        self.analysis_text.insert(tk.END, "=" * 90 + "\n\n")

        self.analysis_text.insert(tk.END, "[전체 출현 빈도 TOP 10]\n")
        for item in summary["most_common_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - {item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[전체 저출현 번호 TOP 10]\n")
        for item in summary["least_common_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - {item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[최근 30회 HOT 번호 TOP 10]\n")
        for item in summary["hot_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - {item['count']}회\n"
            )

        self.analysis_text.insert(tk.END, "\n[최근 30회 COLD 번호 TOP 10]\n")
        for item in summary["cold_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - {item['count']}회\n"
            )

        self.analysis_text.insert(tk.END, "\n[상승 번호 TOP 10]\n")
        for item in summary["rising_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - 최근 {item['recent_count']}회 / "
                f"이전 {item['previous_count']}회 / 차이 {item['diff']}\n"
            )

        self.analysis_text.insert(tk.END, "\n[하락 번호 TOP 10]\n")
        for item in summary["falling_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - 최근 {item['recent_count']}회 / "
                f"이전 {item['previous_count']}회 / 차이 {item['diff']}\n"
            )

        self.analysis_text.insert(tk.END, "\n[동시 출현 번호쌍 TOP 20]\n")
        for item in summary["top_pairs"]:
            pair = item["pair"]
            self.analysis_text.insert(
                tk.END,
                f"{pair[0]:>2}번 + {pair[1]:>2}번 - "
                f"{item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[3개 번호 동시 출현 TOP 20]\n")
        for item in summary["top_triples"]:
            triple = item["triple"]
            self.analysis_text.insert(
                tk.END,
                f"{triple[0]:>2}번 + {triple[1]:>2}번 + {triple[2]:>2}번 - "
                f"{item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[장기 미출현 번호 TOP 10]\n")
        for item in summary["missing_numbers"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['number']:>2}번 - {item['missing_draws']}회 미출현 / "
                f"마지막 출현 {item['last_seen_draw_no']}회\n"
            )

        pattern_summary = summary["pattern_summary"]

        self.analysis_text.insert(tk.END, "\n[홀짝 패턴 분포]\n")
        for item in pattern_summary["odd_even"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['pattern']} - {item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[고저 패턴 분포]\n")
        for item in pattern_summary["low_high"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['pattern']} - {item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[번호합 구간 분포]\n")
        for item in pattern_summary["sum"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['pattern']} - {item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(tk.END, "\n[연속번호 개수 분포]\n")
        for item in pattern_summary["consecutive"]:
            self.analysis_text.insert(
                tk.END,
                f"{item['pattern']}쌍 - {item['count']}회 ({item['rate']}%)\n"
            )

        self.analysis_text.insert(
            tk.END,
            "\n※ 본 통계분석은 저장된 과거 당첨번호 데이터를 기준으로 계산됩니다.\n"
        )

        self.analysis_button.config(state="normal")
        self.set_status("통계분석 완료 | Lotto Analyzer 정상 동작 중")
        self.add_log("통계분석 완료")

    def _handle_analysis_error(self, error):
        self.analysis_button.config(state="normal")
        self.set_status("통계분석 오류 발생")
        self.add_log(f"통계분석 오류 [{type(error).__name__}]: {error}")
        messagebox.showerror(
            "오류",
            f"통계분석 중 오류가 발생했습니다.\n\n{error}"
        )

    def set_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def generate_recommendations(self):
        self.generate_button.config(state="disabled")
        self.recommend_status_label.config(
            text="분석 중 · 추천번호를 생성하고 있습니다.",
            fg=AppTheme.PRIMARY
        )
        self.set_status("추천번호 생성 중...")
        self.add_log("추천번호 생성 시작")

        self.show_recommend_empty_state("추천번호를 생성하고 있습니다.")
        self.recommend_progress.pack(fill="x", pady=(0, 10))
        self.recommend_progress.start(10)

        threading.Thread(
            target=self._generate_recommendations_worker,
            daemon=True
        ).start()

    def _generate_recommendations_worker(self):
        try:
            recommendations = self.recommendation_service.get_final_recommendations()
            self.root.after(0, self._display_recommendations, recommendations)
        except Exception as e:
            self.root.after(0, self._handle_recommendation_error, e)

    def _display_recommendations(self, recommendations):
        self.recommend_progress.stop()
        self.recommend_progress.pack_forget()
        self.clear_recommendation_cards()

        if not recommendations:
            self.show_recommend_empty_state("조건에 맞는 추천 조합을 생성하지 못했습니다.")
        else:
            for item in recommendations:
                self.create_recommendation_card(item)

            notice = tk.Label(
                self.recommend_cards_frame,
                text="※ 본 추천번호는 과거 데이터 기반 통계 분석 결과입니다.",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_SECONDARY,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w"
            )
            notice.pack(fill="x", pady=(2, 4))

        self.recommend_canvas.yview_moveto(0)
        self.generate_button.config(state="normal")
        self.recommend_status_label.config(
            text="완료 · 추천번호 생성이 완료되었습니다.",
            fg=AppTheme.SUCCESS
        )
        self.set_status("추천번호 생성 완료 | Lotto Analyzer 정상 동작 중")
        self.add_log("추천번호 생성 완료")

    def _handle_recommendation_error(self, error):
        self.recommend_progress.stop()
        self.recommend_progress.pack_forget()
        self.generate_button.config(state="normal")
        self.recommend_status_label.config(
            text="오류 · 추천번호 생성에 실패했습니다.",
            fg=AppTheme.ERROR
        )
        self.show_recommend_empty_state("추천번호 생성 중 오류가 발생했습니다.")
        self.set_status("추천번호 생성 오류 발생")
        self.add_log(f"추천번호 생성 오류 [{type(error).__name__}]: {error}")
        messagebox.showerror(
            "오류",
            f"추천번호 생성 중 오류가 발생했습니다.\n\n{error}"
        )

    def search_draw_number(self):
        try:
            draw_no_text = self.draw_no_entry.get().strip()

            if not draw_no_text:
                messagebox.showwarning("입력 오류", "조회할 회차를 입력해주세요.")
                return

            if not draw_no_text.isdigit():
                messagebox.showwarning("입력 오류", "회차는 숫자만 입력해주세요.")
                return

            draw_no = int(draw_no_text)

            self.set_status(f"{draw_no}회 당첨번호 조회 중...")
            self.add_log(f"{draw_no}회 당첨번호 조회 시작")

            result = self.draw_search_service.get_draw_by_no(draw_no)

            self.draw_search_text.delete("1.0", tk.END)

            if result is None:
                self.draw_search_text.insert(
                    tk.END,
                    f"{draw_no}회 당첨번호 데이터가 없습니다.\n"
                )
                self.set_status("회차조회 결과 없음")
                self.add_log(f"{draw_no}회 당첨번호 조회 결과 없음")
                return

            self.draw_search_text.insert(tk.END, "=" * 70 + "\n")
            self.draw_search_text.insert(tk.END, f"                      {result['draw_no']}회 당첨번호\n")
            self.draw_search_text.insert(tk.END, "=" * 70 + "\n\n")

            self.draw_search_text.insert(
                tk.END,
                f"당첨번호 : {result['numbers']}\n"
            )

            self.draw_search_text.insert(
                tk.END,
                f"보너스번호 : {result['bonus_number']}\n"
            )

            self.draw_search_text.insert(tk.END, "\n" + "-" * 70 + "\n")
            self.draw_search_text.insert(
                tk.END,
                "※ 저장된 과거 당첨번호 데이터를 기준으로 조회합니다.\n"
            )

            self.set_status(f"{draw_no}회 당첨번호 조회 완료")
            self.add_log(f"{draw_no}회 당첨번호 조회 완료")

        except Exception as e:
            self.set_status("회차조회 오류 발생")
            self.add_log(f"회차조회 오류: {e}")

            messagebox.showerror(
                "오류",
                f"회차조회 중 오류가 발생했습니다.\n\n{e}"
            )

    def add_log(self, message):
        if hasattr(self, "log_text"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text.insert(tk.END, f"[{now}] {message}\n")
            self.log_text.see(tk.END)

    def run(self):
        self.root.mainloop()

    def run_backtest(self):
        self.backtest_button.config(state="disabled")
        self.set_status("백테스트 실행 중...")
        self.add_log("백테스트 시작")

        self.backtest_text.delete("1.0", tk.END)
        self.backtest_text.insert(
            tk.END,
            "최근 10회 기준 최종 추천번호 백테스트를 실행하고 있습니다...\n"
        )

        threading.Thread(
            target=self._run_backtest_worker,
            daemon=True
        ).start()

    def _run_backtest_worker(self):
        try:
            data = self.backtest_service.run_backtest(10)
            self.root.after(0, self._display_backtest_result, data)
        except Exception as e:
            self.root.after(0, self._handle_backtest_error, e)

    def _display_backtest_result(self, data):
        summary = data["summary"]
        self.backtest_text.delete("1.0", tk.END)

        self.backtest_text.insert(tk.END, "=" * 90 + "\n")
        self.backtest_text.insert(tk.END, "                 백테스트 결과\n")
        self.backtest_text.insert(tk.END, "=" * 90 + "\n\n")

        self.backtest_text.insert(
            tk.END,
            f"테스트 회차 : {summary['test_count']}회\n"
        )
        self.backtest_text.insert(
            tk.END,
            f"추천번호 개수 : {summary['total_recommendation_count']}개\n"
        )
        self.backtest_text.insert(
            tk.END,
            f"평균 일치 개수 : {summary['average_match_count']}개\n"
        )
        self.backtest_text.insert(
            tk.END,
            f"전체 추천 최고 일치 개수 : {summary['max_match_count']}개\n"
        )
        self.backtest_text.insert(
            tk.END,
            f"회차별 최고 결과 평균 일치 : {summary['best_average_match_count']}개\n"
        )
        self.backtest_text.insert(
            tk.END,
            f"회차별 최고 결과 최대 일치 : {summary['best_max_match_count']}개\n"
        )
        self.backtest_text.insert(
            tk.END,
            f"번호 적중률 : {summary['number_hit_rate']}%\n\n"
        )

        self.backtest_text.insert(tk.END, "[등수 분포]\n")
        for rank, count in summary["rank_counts"].items():
            self.backtest_text.insert(tk.END, f"{rank} : {count}세트\n")

        self.backtest_text.insert(tk.END, "\n[일치 개수 분포]\n")
        for match, count in summary["match_count_distribution"].items():
            self.backtest_text.insert(
                tk.END,
                f"{match}개 일치 : {count}세트\n"
            )

        self.backtest_text.insert(tk.END, "\n[점수 구간별 결과]\n")
        for score, stat in summary["score_range_stats"].items():
            success_rate = 0
            if stat["count"] > 0:
                success_rate = round(
                    stat["three_or_more_count"] / stat["count"] * 100,
                    2
                )

            self.backtest_text.insert(tk.END, f"{score}점 구간\n")
            self.backtest_text.insert(
                tk.END,
                f"  추천 개수       : {stat['count']}개\n"
            )
            self.backtest_text.insert(
                tk.END,
                f"  평균 일치       : {stat['average_match_count']}개\n"
            )
            self.backtest_text.insert(
                tk.END,
                f"  최고 일치       : {stat['max_match_count']}개\n"
            )
            self.backtest_text.insert(
                tk.END,
                f"  3개 이상 일치   : {stat['three_or_more_count']}개\n"
            )
            self.backtest_text.insert(
                tk.END,
                f"  3개 이상 성공률 : {success_rate}%\n\n"
            )

        self.backtest_text.insert(
            tk.END,
            "※ 각 대상 회차 이전 데이터만 사용하여 최종 추천번호 5세트를 생성한 결과입니다.\n"
        )

        self.backtest_button.config(state="normal")
        self.set_status("백테스트 완료 | Lotto Analyzer 정상 동작 중")
        self.add_log("백테스트 완료")

    def _handle_backtest_error(self, error):
        self.backtest_button.config(state="normal")
        self.set_status("백테스트 오류 발생")
        self.add_log(f"백테스트 오류 [{type(error).__name__}]: {error}")
        messagebox.showerror(
            "오류",
            f"백테스트 중 오류가 발생했습니다.\n\n{error}"
        )
