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
    SummaryCard,
    SectionCard,
    SummaryList,
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
        self.bind_global_mousewheel()
        self.show_view("recommend")

    def bind_global_mousewheel(self):
        """현재 선택된 화면의 스크롤 Canvas에 마우스 휠을 연결합니다."""
        self.root.bind_all("<MouseWheel>", self._on_global_mousewheel)

    def _on_global_mousewheel(self, event):
        scroll_units = int(-1 * (event.delta / 120))

        canvas_by_view = {
            "recommend": getattr(self, "recommend_canvas", None),
            "analysis": getattr(self, "analysis_canvas", None),
            "backtest": getattr(self, "backtest_canvas", None),
            "draw_search": getattr(self, "draw_search_canvas", None),
        }

        canvas = canvas_by_view.get(self.current_view)

        if canvas is None:
            return

        canvas.yview_scroll(scroll_units, "units")

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

        self.show_recommend_empty_state()

    def _resize_recommend_cards_frame(self, event):
        self.recommend_canvas.itemconfigure(
            self.recommend_cards_window,
            width=event.width
        )

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
        action_card.pack(fill="x", pady=(0, 10))

        action_info = tk.Frame(action_card, bg=AppTheme.CARD_BACKGROUND)
        action_info.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            action_info,
            text="과거 당첨 데이터 통계 대시보드",
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(anchor="w")

        self.analysis_status_label = tk.Label(
            action_info,
            text="대기 중 · 분석 준비 완료",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.analysis_status_label.pack(anchor="w", pady=(5, 0))

        self.analysis_button = ttk.Button(
            action_card,
            text="통계분석 실행",
            style="Primary.TButton",
            command=self.run_analysis_summary
        )
        self.analysis_button.pack(side="right", padx=18, pady=15)

        self.analysis_progress = create_indeterminate_progress(
            body,
            style="Recommendation.Horizontal.TProgressbar"
        )

        result_card = self.create_card(body, "통계분석 대시보드")
        result_card.pack(fill="both", expand=True)

        result_body = tk.Frame(result_card, bg=AppTheme.CARD_BACKGROUND)
        result_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.analysis_canvas = tk.Canvas(
            result_body,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=0,
            borderwidth=0
        )
        self.analysis_scrollbar = ttk.Scrollbar(
            result_body,
            orient="vertical",
            command=self.analysis_canvas.yview
        )
        self.analysis_dashboard_frame = tk.Frame(
            self.analysis_canvas,
            bg=AppTheme.CARD_BACKGROUND
        )

        self.analysis_dashboard_window = self.analysis_canvas.create_window(
            (0, 0),
            window=self.analysis_dashboard_frame,
            anchor="nw"
        )
        self.analysis_canvas.configure(
            yscrollcommand=self.analysis_scrollbar.set
        )

        self.analysis_canvas.pack(side="left", fill="both", expand=True)
        self.analysis_scrollbar.pack(side="right", fill="y")

        self.analysis_dashboard_frame.bind(
            "<Configure>",
            lambda event: self.analysis_canvas.configure(
                scrollregion=self.analysis_canvas.bbox("all")
            )
        )
        self.analysis_canvas.bind(
            "<Configure>",
            self._resize_analysis_dashboard_frame
        )

        self.show_analysis_empty_state()

    def _resize_analysis_dashboard_frame(self, event):
        self.analysis_canvas.itemconfigure(
            self.analysis_dashboard_window,
            width=event.width
        )

    def clear_analysis_dashboard(self):
        for widget in self.analysis_dashboard_frame.winfo_children():
            widget.destroy()

    def show_analysis_empty_state(
        self,
        message="통계분석 실행 버튼을 눌러주세요."
    ):
        self.clear_analysis_dashboard()

        empty_state = EmptyState(
            self.analysis_dashboard_frame,
            message=message,
            description=(
                "저장된 과거 당첨번호 데이터를 기준으로 주요 지표와 "
                "패턴을 계산합니다."
            ),
            icon_text="A"
        )
        empty_state.pack(fill="both", expand=True, pady=105)

    def create_dashboard_summary_card(
        self,
        parent,
        column,
        title,
        value,
        description,
        accent_color
    ):
        card = SummaryCard(
            parent,
            title=title,
            value=value,
            description=description,
            accent_color=accent_color
        )
        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0 if column == 0 else 5, 0 if column == 3 else 5)
        )
        return card

    def create_analysis_dashboard(self, summary):
        self.clear_analysis_dashboard()

        most_common = (
            summary["most_common_numbers"][0]
            if summary["most_common_numbers"]
            else None
        )
        hot = summary["hot_numbers"][0] if summary["hot_numbers"] else None
        rising = (
            summary["rising_numbers"][0]
            if summary["rising_numbers"]
            else None
        )
        missing = (
            summary["missing_numbers"][0]
            if summary["missing_numbers"]
            else None
        )

        kpi_row = tk.Frame(
            self.analysis_dashboard_frame,
            bg=AppTheme.CARD_BACKGROUND
        )
        kpi_row.pack(fill="x", pady=(0, 12))

        for column in range(4):
            kpi_row.grid_columnconfigure(column, weight=1, uniform="analysis_kpi")

        self.create_dashboard_summary_card(
            kpi_row,
            0,
            "최다 출현 번호",
            f"{most_common['number']}번" if most_common else "-",
            (
                f"{most_common['count']}회 · {most_common['rate']}%"
                if most_common
                else "데이터 없음"
            ),
            AppTheme.PRIMARY
        )
        self.create_dashboard_summary_card(
            kpi_row,
            1,
            "최근 30회 HOT",
            f"{hot['number']}번" if hot else "-",
            f"{hot['count']}회 출현" if hot else "데이터 없음",
            AppTheme.ERROR
        )
        self.create_dashboard_summary_card(
            kpi_row,
            2,
            "상승 번호",
            f"{rising['number']}번" if rising else "-",
            (
                f"최근 {rising['recent_count']}회 · 차이 {rising['diff']:+d}"
                if rising
                else "데이터 없음"
            ),
            AppTheme.SUCCESS
        )
        self.create_dashboard_summary_card(
            kpi_row,
            3,
            "장기 미출현",
            f"{missing['number']}번" if missing else "-",
            (
                f"{missing['missing_draws']}회 미출현"
                if missing
                else "데이터 없음"
            ),
            AppTheme.WARNING
        )

        sections = tk.Frame(
            self.analysis_dashboard_frame,
            bg=AppTheme.CARD_BACKGROUND
        )
        sections.pack(fill="both", expand=True)
        sections.grid_columnconfigure(0, weight=1, uniform="analysis_section")
        sections.grid_columnconfigure(1, weight=1, uniform="analysis_section")

        frequency_card = SectionCard(
            sections,
            "출현빈도",
            "전체 회차 기준 고출현 번호와 저출현 번호"
        )
        frequency_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(0, 12)
        )
        frequency_card.content.grid_columnconfigure(0, weight=1)
        frequency_card.content.grid_columnconfigure(1, weight=1)

        common_rows = [
            {
                "primary": f"{item['number']}번",
                "secondary": f"{item['count']}회",
                "detail": f"{item['rate']}%"
            }
            for item in summary["most_common_numbers"]
        ]
        least_rows = [
            {
                "primary": f"{item['number']}번",
                "secondary": f"{item['count']}회",
                "detail": f"{item['rate']}%"
            }
            for item in summary["least_common_numbers"]
        ]

        SummaryList(
            frequency_card.content,
            "전체 출현 TOP 10",
            common_rows
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        SummaryList(
            frequency_card.content,
            "전체 저출현 TOP 10",
            least_rows
        ).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        trend_card = SectionCard(
            sections,
            "최근 추세",
            "최근 30회 HOT/COLD와 상승·하락 및 장기 미출현 번호"
        )
        trend_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(0, 12)
        )
        for column in range(2):
            trend_card.content.grid_columnconfigure(column, weight=1)

        hot_rows = [
            {
                "primary": f"{item['number']}번",
                "secondary": f"{item['count']}회"
            }
            for item in summary["hot_numbers"]
        ]
        cold_rows = [
            {
                "primary": f"{item['number']}번",
                "secondary": f"{item['count']}회"
            }
            for item in summary["cold_numbers"]
        ]
        rising_rows = [
            {
                "primary": f"{item['number']}번",
                "secondary": f"{item['diff']:+d}",
                "detail": (
                    f"최근 {item['recent_count']} / 이전 "
                    f"{item['previous_count']}"
                )
            }
            for item in summary["rising_numbers"]
        ]
        missing_rows = [
            {
                "primary": f"{item['number']}번",
                "secondary": f"{item['missing_draws']}회",
                "detail": f"마지막 {item['last_seen_draw_no']}회"
            }
            for item in summary["missing_numbers"]
        ]

        SummaryList(
            trend_card.content,
            "최근 HOT",
            hot_rows
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 12))
        SummaryList(
            trend_card.content,
            "최근 COLD",
            cold_rows
        ).grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 12))
        SummaryList(
            trend_card.content,
            "상승 번호",
            rising_rows
        ).grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        SummaryList(
            trend_card.content,
            "장기 미출현",
            missing_rows
        ).grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        combination_card = SectionCard(
            sections,
            "조합 분석",
            "과거 당첨번호에서 자주 함께 출현한 Pair와 Triple"
        )
        combination_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(0, 12)
        )
        combination_card.content.grid_columnconfigure(0, weight=1)
        combination_card.content.grid_columnconfigure(1, weight=1)

        pair_rows = [
            {
                "primary": f"{item['pair'][0]} + {item['pair'][1]}",
                "secondary": f"{item['count']}회",
                "detail": f"{item['rate']}%"
            }
            for item in summary["top_pairs"]
        ]
        triple_rows = [
            {
                "primary": (
                    f"{item['triple'][0]} + {item['triple'][1]} + "
                    f"{item['triple'][2]}"
                ),
                "secondary": f"{item['count']}회",
                "detail": f"{item['rate']}%"
            }
            for item in summary["top_triples"]
        ]

        SummaryList(
            combination_card.content,
            "Pair TOP 20",
            pair_rows
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        SummaryList(
            combination_card.content,
            "Triple TOP 20",
            triple_rows
        ).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        pattern_card = SectionCard(
            sections,
            "패턴 분석",
            "홀짝·고저·번호합·연속번호 패턴 분포"
        )
        pattern_card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(0, 12)
        )
        for column in range(2):
            pattern_card.content.grid_columnconfigure(column, weight=1)

        pattern_summary = summary["pattern_summary"]

        def pattern_rows(items, suffix=""):
            return [
                {
                    "primary": f"{item['pattern']}{suffix}",
                    "secondary": f"{item['count']}회",
                    "detail": f"{item['rate']}%"
                }
                for item in items
            ]

        SummaryList(
            pattern_card.content,
            "홀짝 패턴",
            pattern_rows(pattern_summary["odd_even"])
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 12))
        SummaryList(
            pattern_card.content,
            "고저 패턴",
            pattern_rows(pattern_summary["low_high"])
        ).grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 12))
        SummaryList(
            pattern_card.content,
            "번호합 구간",
            pattern_rows(pattern_summary["sum"])
        ).grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        SummaryList(
            pattern_card.content,
            "연속번호 개수",
            pattern_rows(pattern_summary["consecutive"], "쌍")
        ).grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            self.analysis_dashboard_frame,
            text="※ 본 통계분석은 저장된 과거 당첨번호 데이터를 기준으로 계산됩니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.analysis_canvas.update_idletasks()
        self.analysis_canvas.yview_moveto(0)

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
        action_card.pack(fill="x", pady=(0, 10))

        action_info = tk.Frame(action_card, bg=AppTheme.CARD_BACKGROUND)
        action_info.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            action_info,
            text="최근 10회 추천번호 성능 리포트",
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(anchor="w")

        self.backtest_status_label = tk.Label(
            action_info,
            text="대기 중 · 백테스트 준비 완료",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.backtest_status_label.pack(anchor="w", pady=(5, 0))

        self.backtest_button = ttk.Button(
            action_card,
            text="백테스트 실행",
            style="Primary.TButton",
            command=self.run_backtest
        )
        self.backtest_button.pack(side="right", padx=18, pady=15)

        self.backtest_progress = create_indeterminate_progress(
            body,
            style="Recommendation.Horizontal.TProgressbar"
        )

        result_card = self.create_card(body, "백테스트 대시보드")
        result_card.pack(fill="both", expand=True)

        result_body = tk.Frame(result_card, bg=AppTheme.CARD_BACKGROUND)
        result_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.backtest_canvas = tk.Canvas(
            result_body,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=0,
            borderwidth=0
        )
        self.backtest_scrollbar = ttk.Scrollbar(
            result_body,
            orient="vertical",
            command=self.backtest_canvas.yview
        )
        self.backtest_dashboard_frame = tk.Frame(
            self.backtest_canvas,
            bg=AppTheme.CARD_BACKGROUND
        )

        self.backtest_dashboard_window = self.backtest_canvas.create_window(
            (0, 0),
            window=self.backtest_dashboard_frame,
            anchor="nw"
        )
        self.backtest_canvas.configure(
            yscrollcommand=self.backtest_scrollbar.set
        )

        self.backtest_canvas.pack(side="left", fill="both", expand=True)
        self.backtest_scrollbar.pack(side="right", fill="y")

        self.backtest_dashboard_frame.bind(
            "<Configure>",
            lambda event: self.backtest_canvas.configure(
                scrollregion=self.backtest_canvas.bbox("all")
            )
        )
        self.backtest_canvas.bind(
            "<Configure>",
            self._resize_backtest_dashboard_frame
        )

        self.show_backtest_empty_state()

    def _resize_backtest_dashboard_frame(self, event):
        self.backtest_canvas.itemconfigure(
            self.backtest_dashboard_window,
            width=event.width
        )

    def clear_backtest_dashboard(self):
        for widget in self.backtest_dashboard_frame.winfo_children():
            widget.destroy()

    def show_backtest_empty_state(
        self,
        message="백테스트 실행 버튼을 눌러주세요."
    ):
        self.clear_backtest_dashboard()

        empty_state = EmptyState(
            self.backtest_dashboard_frame,
            message=message,
            description=(
                "최근 10회 기준 추천번호 생성 결과의 평균 적중, 최고 적중, "
                "적중률과 분포를 계산합니다."
            ),
            icon_text="B"
        )
        empty_state.pack(fill="both", expand=True, pady=105)

    def create_backtest_dashboard(self, data):
        self.clear_backtest_dashboard()

        summary = data["summary"]

        kpi_row = tk.Frame(
            self.backtest_dashboard_frame,
            bg=AppTheme.CARD_BACKGROUND
        )
        kpi_row.pack(fill="x", pady=(0, 12))

        for column in range(4):
            kpi_row.grid_columnconfigure(
                column,
                weight=1,
                uniform="backtest_kpi"
            )

        cards = [
            (
                "평균 일치",
                f"{summary['average_match_count']}개",
                "전체 추천번호 기준",
                AppTheme.PRIMARY
            ),
            (
                "최고 일치",
                f"{summary['max_match_count']}개",
                f"회차별 최고 {summary['best_max_match_count']}개",
                AppTheme.SUCCESS
            ),
            (
                "번호 적중률",
                f"{summary['number_hit_rate']}%",
                "전체 추천번호 기준",
                AppTheme.WARNING
            ),
            (
                "테스트 회차",
                f"{summary['test_count']}회",
                f"추천번호 {summary['total_recommendation_count']}개",
                AppTheme.ERROR
            ),
        ]

        for column, (title, value, description, color) in enumerate(cards):
            card = SummaryCard(
                kpi_row,
                title=title,
                value=value,
                description=description,
                accent_color=color
            )
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 5, 0 if column == 3 else 5)
            )

        sections = tk.Frame(
            self.backtest_dashboard_frame,
            bg=AppTheme.CARD_BACKGROUND
        )
        sections.pack(fill="both", expand=True)
        sections.grid_columnconfigure(0, weight=1, uniform="backtest_section")
        sections.grid_columnconfigure(1, weight=1, uniform="backtest_section")

        rank_rows = [
            {
                "primary": str(rank),
                "secondary": f"{count}세트"
            }
            for rank, count in summary["rank_counts"].items()
        ]

        match_rows = [
            {
                "primary": f"{match}개 일치",
                "secondary": f"{count}세트"
            }
            for match, count in summary["match_count_distribution"].items()
        ]

        rank_card = SectionCard(
            sections,
            "등수 분포",
            "전체 추천번호의 등수별 발생 횟수"
        )
        rank_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(0, 12)
        )
        SummaryList(
            rank_card.content,
            "등수별 결과",
            rank_rows
        ).pack(fill="both", expand=True)

        match_card = SectionCard(
            sections,
            "일치 개수 분포",
            "추천번호와 실제 당첨번호의 일치 개수별 분포"
        )
        match_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(0, 12)
        )
        SummaryList(
            match_card.content,
            "일치 결과",
            match_rows
        ).pack(fill="both", expand=True)

        score_card = SectionCard(
            sections,
            "점수 구간별 결과",
            "추천 점수 구간별 평균·최고 일치 및 3개 이상 성공률"
        )
        score_card.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(0, 12)
        )

        score_rows = []
        for score, stat in summary["score_range_stats"].items():
            success_rate = 0
            if stat["count"] > 0:
                success_rate = round(
                    stat["three_or_more_count"] / stat["count"] * 100,
                    2
                )

            score_rows.append(
                {
                    "primary": f"{score}점 구간",
                    "secondary": f"{success_rate}%",
                    "detail": (
                        f"{stat['count']}개 · 평균 "
                        f"{stat['average_match_count']}개 · 최고 "
                        f"{stat['max_match_count']}개"
                    )
                }
            )

        SummaryList(
            score_card.content,
            "3개 이상 일치 성공률",
            score_rows
        ).pack(fill="both", expand=True)

        best_card = SectionCard(
            sections,
            "회차별 최고 결과",
            "각 대상 회차에서 가장 높은 적중 결과를 기준으로 계산"
        )
        best_card.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(0, 12)
        )

        best_rows = [
            {
                "primary": "회차별 최고 결과 평균 일치",
                "secondary": f"{summary['best_average_match_count']}개"
            },
            {
                "primary": "회차별 최고 결과 최대 일치",
                "secondary": f"{summary['best_max_match_count']}개"
            },
            {
                "primary": "전체 추천 최고 일치",
                "secondary": f"{summary['max_match_count']}개"
            },
        ]

        SummaryList(
            best_card.content,
            "핵심 결과",
            best_rows
        ).pack(fill="both", expand=True)

        tk.Label(
            self.backtest_dashboard_frame,
            text=(
                "※ 각 대상 회차 이전 데이터만 사용하여 최종 추천번호 "
                "5세트를 생성한 결과입니다."
            ),
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.backtest_canvas.update_idletasks()
        self.backtest_canvas.yview_moveto(0)

    def create_draw_search_view(self):
        view = self.create_view_frame("draw_search")
        body = tk.Frame(view, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self.create_page_intro(
            body,
            "회차조회",
            "저장된 과거 당첨번호 데이터에서 특정 회차의 당첨번호를 조회합니다."
        )

        search_card = self.create_card(body)
        search_card.pack(fill="x", pady=(0, 14))

        search_info = tk.Frame(search_card, bg=AppTheme.CARD_BACKGROUND)
        search_info.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            search_info,
            text="당첨번호 회차 검색",
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(anchor="w")

        self.draw_search_status_label = tk.Label(
            search_info,
            text="조회할 회차를 입력해주세요.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.draw_search_status_label.pack(anchor="w", pady=(5, 0))

        search_controls = tk.Frame(
            search_card,
            bg=AppTheme.CARD_BACKGROUND
        )
        search_controls.pack(side="right", padx=18, pady=14)

        self.draw_no_entry = tk.Entry(
            search_controls,
            width=14,
            font=AppTheme.FONT_BODY,
            bg=AppTheme.INPUT_BACKGROUND,
            fg=AppTheme.TEXT_PRIMARY,
            insertbackground=AppTheme.TEXT_PRIMARY,
            relief="flat",
            justify="center",
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            highlightcolor=AppTheme.PRIMARY
        )
        self.draw_no_entry.pack(side="left", padx=(0, 8), ipady=8)
        self.draw_no_entry.bind(
            "<Return>",
            lambda event: self.search_draw_number()
        )

        self.draw_search_button = ttk.Button(
            search_controls,
            text="조회",
            style="Primary.TButton",
            command=self.search_draw_number
        )
        self.draw_search_button.pack(side="left")

        result_card = self.create_card(body, "당첨번호 조회 결과")
        result_card.pack(fill="both", expand=True)

        result_body = tk.Frame(
            result_card,
            bg=AppTheme.CARD_BACKGROUND
        )
        result_body.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        self.draw_search_canvas = tk.Canvas(
            result_body,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=0,
            borderwidth=0
        )
        self.draw_search_scrollbar = ttk.Scrollbar(
            result_body,
            orient="vertical",
            command=self.draw_search_canvas.yview
        )
        self.draw_result_container = tk.Frame(
            self.draw_search_canvas,
            bg=AppTheme.CARD_BACKGROUND
        )

        self.draw_search_window = self.draw_search_canvas.create_window(
            (0, 0),
            window=self.draw_result_container,
            anchor="nw"
        )
        self.draw_search_canvas.configure(
            yscrollcommand=self.draw_search_scrollbar.set
        )

        self.draw_search_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )
        self.draw_search_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.draw_result_container.bind(
            "<Configure>",
            lambda event: self.draw_search_canvas.configure(
                scrollregion=self.draw_search_canvas.bbox("all")
            )
        )
        self.draw_search_canvas.bind(
            "<Configure>",
            self._resize_draw_search_result
        )

        self.show_draw_search_empty_state()

    def _resize_draw_search_result(self, event):
        self.draw_search_canvas.itemconfigure(
            self.draw_search_window,
            width=event.width
        )

    def clear_draw_search_result(self):
        for widget in self.draw_result_container.winfo_children():
            widget.destroy()

    def show_draw_search_empty_state(
        self,
        message="조회할 회차를 입력해주세요."
    ):
        self.clear_draw_search_result()

        empty_state = EmptyState(
            self.draw_result_container,
            message=message,
            description=(
                "저장된 과거 당첨번호 데이터에서 회차별 당첨번호와 "
                "보너스번호를 확인합니다."
            ),
            icon_text="D"
        )
        empty_state.pack(fill="both", expand=True, pady=105)

        self.draw_search_canvas.update_idletasks()
        self.draw_search_canvas.yview_moveto(0)

    def create_draw_result_card(self, result):
        self.clear_draw_search_result()

        draw_no = result["draw_no"]
        numbers = result["numbers"]
        bonus_number = result["bonus_number"]

        header = tk.Frame(
            self.draw_result_container,
            bg=AppTheme.CARD_BACKGROUND
        )
        header.pack(fill="x", pady=(20, 8))

        tk.Label(
            header,
            text=f"제 {draw_no}회",
            font=(AppTheme.FONT_FAMILY, 24, "bold"),
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack()

        tk.Label(
            header,
            text="로또 당첨번호",
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack(pady=(5, 0))

        number_card = tk.Frame(
            self.draw_result_container,
            bg=AppTheme.INPUT_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER
        )
        number_card.pack(fill="x", padx=30, pady=(18, 14))

        number_content = tk.Frame(
            number_card,
            bg=AppTheme.INPUT_BACKGROUND
        )
        number_content.pack(pady=28)

        winning_area = tk.Frame(
            number_content,
            bg=AppTheme.INPUT_BACKGROUND
        )
        winning_area.pack(side="left")

        tk.Label(
            winning_area,
            text="당첨번호",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.INPUT_BACKGROUND
        ).pack(pady=(0, 12))

        winning_balls = tk.Frame(
            winning_area,
            bg=AppTheme.INPUT_BACKGROUND
        )
        winning_balls.pack()

        for number in numbers:
            ball = LottoBall(
                winning_balls,
                number,
                size=64,
                background=AppTheme.INPUT_BACKGROUND
            )
            ball.pack(side="left", padx=6)

        plus_area = tk.Frame(
            number_content,
            bg=AppTheme.INPUT_BACKGROUND
        )
        plus_area.pack(side="left", padx=24)

        tk.Label(
            plus_area,
            text="+",
            font=(AppTheme.FONT_FAMILY, 24, "bold"),
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.INPUT_BACKGROUND
        ).pack(pady=(36, 0))

        bonus_area = tk.Frame(
            number_content,
            bg=AppTheme.INPUT_BACKGROUND
        )
        bonus_area.pack(side="left")

        tk.Label(
            bonus_area,
            text="보너스",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.INPUT_BACKGROUND
        ).pack(pady=(0, 12))

        bonus_ball = LottoBall(
            bonus_area,
            bonus_number,
            size=64,
            background=AppTheme.INPUT_BACKGROUND
        )
        bonus_ball.pack()

        metrics_row = tk.Frame(
            self.draw_result_container,
            bg=AppTheme.CARD_BACKGROUND
        )
        metrics_row.pack(fill="x", padx=30, pady=(0, 14))

        for column in range(3):
            metrics_row.grid_columnconfigure(
                column,
                weight=1,
                uniform="draw_metric"
            )

        odd_count = sum(1 for number in numbers if number % 2 == 1)
        even_count = len(numbers) - odd_count
        low_count = sum(1 for number in numbers if number <= 22)
        high_count = len(numbers) - low_count
        total_sum = sum(numbers)

        metric_values = [
            ("번호합", str(total_sum), AppTheme.PRIMARY),
            ("홀짝 비율", f"{odd_count}:{even_count}", AppTheme.SUCCESS),
            ("고저 비율", f"{low_count}:{high_count}", AppTheme.WARNING),
        ]

        for column, (title, value, color) in enumerate(metric_values):
            metric_card = SummaryCard(
                metrics_row,
                title=title,
                value=value,
                description="당첨번호 6개 기준",
                accent_color=color
            )
            metric_card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 5, 0 if column == 2 else 5)
            )

        tk.Label(
            self.draw_result_container,
            text="※ 저장된 과거 당첨번호 데이터를 기준으로 조회한 결과입니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(fill="x", padx=30, pady=(4, 12))

        self.draw_search_canvas.update_idletasks()
        self.draw_search_canvas.yview_moveto(0)

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
        self.analysis_status_label.config(
            text="분석 중 · 통계 데이터를 계산하고 있습니다.",
            fg=AppTheme.PRIMARY
        )
        self.set_status("통계분석 실행 중...")
        self.add_log("통계분석 실행 시작")

        self.show_analysis_empty_state("통계분석을 실행하고 있습니다.")
        self.analysis_progress.pack(fill="x", pady=(0, 10))
        self.analysis_progress.start(10)

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
        self.analysis_progress.stop()
        self.analysis_progress.pack_forget()
        self.create_analysis_dashboard(summary)

        self.analysis_button.config(state="normal")
        self.analysis_status_label.config(
            text="완료 · 통계분석 대시보드가 갱신되었습니다.",
            fg=AppTheme.SUCCESS
        )
        self.set_status("통계분석 완료 | Lotto Analyzer 정상 동작 중")
        self.add_log("통계분석 완료")

    def _handle_analysis_error(self, error):
        self.analysis_progress.stop()
        self.analysis_progress.pack_forget()
        self.analysis_button.config(state="normal")
        self.analysis_status_label.config(
            text="오류 · 통계분석에 실패했습니다.",
            fg=AppTheme.ERROR
        )
        self.show_analysis_empty_state("통계분석 중 오류가 발생했습니다.")
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
                messagebox.showwarning(
                    "입력 오류",
                    "조회할 회차를 입력해주세요."
                )
                return

            if not draw_no_text.isdigit():
                messagebox.showwarning(
                    "입력 오류",
                    "회차는 숫자만 입력해주세요."
                )
                return

            draw_no = int(draw_no_text)

            self.draw_search_button.config(state="disabled")
            self.draw_search_status_label.config(
                text=f"{draw_no}회 당첨번호를 조회하고 있습니다.",
                fg=AppTheme.PRIMARY
            )
            self.set_status(f"{draw_no}회 당첨번호 조회 중...")
            self.add_log(f"{draw_no}회 당첨번호 조회 시작")

            result = self.draw_search_service.get_draw_by_no(draw_no)

            if result is None:
                self.show_draw_search_empty_state(
                    f"{draw_no}회 당첨번호 데이터가 없습니다."
                )
                self.draw_search_status_label.config(
                    text="조회 결과 없음 · 다른 회차를 입력해주세요.",
                    fg=AppTheme.WARNING
                )
                self.set_status("회차조회 결과 없음")
                self.add_log(f"{draw_no}회 당첨번호 조회 결과 없음")
                return

            self.create_draw_result_card(result)

            self.draw_search_status_label.config(
                text=f"완료 · {draw_no}회 당첨번호 조회 완료",
                fg=AppTheme.SUCCESS
            )
            self.set_status(f"{draw_no}회 당첨번호 조회 완료")
            self.add_log(f"{draw_no}회 당첨번호 조회 완료")

        except Exception as e:
            self.show_draw_search_empty_state(
                "회차조회 중 오류가 발생했습니다."
            )
            self.draw_search_status_label.config(
                text="오류 · 회차조회에 실패했습니다.",
                fg=AppTheme.ERROR
            )
            self.set_status("회차조회 오류 발생")
            self.add_log(
                f"회차조회 오류 [{type(e).__name__}]: {e}"
            )

            messagebox.showerror(
                "오류",
                f"회차조회 중 오류가 발생했습니다.\n\n{e}"
            )

        finally:
            self.draw_search_button.config(state="normal")

    def add_log(self, message):
        if hasattr(self, "log_text"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text.insert(tk.END, f"[{now}] {message}\n")
            self.log_text.see(tk.END)

    def run(self):
        self.root.mainloop()

    def run_backtest(self):
        self.backtest_button.config(state="disabled")
        self.backtest_status_label.config(
            text="분석 중 · 백테스트를 실행하고 있습니다.",
            fg=AppTheme.PRIMARY
        )
        self.set_status("백테스트 실행 중...")
        self.add_log("백테스트 시작")

        self.show_backtest_empty_state("백테스트를 실행하고 있습니다.")
        self.backtest_progress.pack(fill="x", pady=(0, 10))
        self.backtest_progress.start(10)

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
        self.backtest_progress.stop()
        self.backtest_progress.pack_forget()
        self.create_backtest_dashboard(data)

        self.backtest_button.config(state="normal")
        self.backtest_status_label.config(
            text="완료 · 백테스트 대시보드가 갱신되었습니다.",
            fg=AppTheme.SUCCESS
        )
        self.set_status("백테스트 완료 | Lotto Analyzer 정상 동작 중")
        self.add_log("백테스트 완료")

    def _handle_backtest_error(self, error):
        self.backtest_progress.stop()
        self.backtest_progress.pack_forget()
        self.backtest_button.config(state="normal")
        self.backtest_status_label.config(
            text="오류 · 백테스트에 실패했습니다.",
            fg=AppTheme.ERROR
        )
        self.show_backtest_empty_state("백테스트 중 오류가 발생했습니다.")
        self.set_status("백테스트 오류 발생")
        self.add_log(f"백테스트 오류 [{type(error).__name__}]: {error}")
        messagebox.showerror(
            "오류",
            f"백테스트 중 오류가 발생했습니다.\n\n{error}"
        )
