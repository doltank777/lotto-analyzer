import tkinter as tk
import threading
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime

from src.app.recommendation_service import RecommendationService
from src.app.draw_search_service import DrawSearchService
from src.app.analysis_service import AnalysisService
from src.app.backtest_service import BacktestService
from src.gui.theme import AppTheme

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lotto Analyzer (1.1.0)")
        self.root.geometry(f"{AppTheme.WINDOW_WIDTH}x{AppTheme.WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.bg_color = AppTheme.BACKGROUND
        self.panel_color = AppTheme.PANEL
        self.status_color = AppTheme.SURFACE

        self.default_font = AppTheme.FONT_BODY
        self.title_font = AppTheme.FONT_TITLE
        self.subtitle_font = AppTheme.FONT_SUBTITLE
        self.button_font = AppTheme.FONT_BUTTON
        self.section_title_font = AppTheme.FONT_SECTION_TITLE
        self.text_font = AppTheme.FONT_MONO

        self.root.configure(bg=self.bg_color)

        self.recommendation_service = RecommendationService()
        self.draw_search_service = DrawSearchService()
        self.analysis_service = AnalysisService()
        self.backtest_service = BacktestService()

        self.create_widgets()        

    def create_widgets(self):
        self.create_styles()
        self.create_header()
        self.create_tabs()
        self.create_status_bar()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TNotebook",
            background=AppTheme.BACKGROUND,
            borderwidth=0,
            tabmargins=(0, 0, 0, 0)
        )

        style.configure(
            "TNotebook.Tab",
            font=AppTheme.FONT_BODY_BOLD,
            padding=AppTheme.TAB_PADDING,
            background=AppTheme.SURFACE,
            foreground=AppTheme.TEXT_SECONDARY,
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", AppTheme.PANEL),
                ("active", AppTheme.PANEL_ALT)
            ],
            foreground=[
                ("selected", AppTheme.TEXT_PRIMARY),
                ("active", AppTheme.TEXT_PRIMARY)
            ]
        )

        style.configure(
            "Primary.TButton",
            font=AppTheme.FONT_BUTTON,
            padding=AppTheme.BUTTON_PADDING,
            background=AppTheme.PRIMARY,
            foreground=AppTheme.TEXT_PRIMARY,
            borderwidth=0,
            focusthickness=0
        )
        style.map(
            "Primary.TButton",
            background=[
                ("active", AppTheme.PRIMARY_ACTIVE),
                ("pressed", AppTheme.PRIMARY_ACTIVE),
                ("disabled", AppTheme.BORDER)
            ],
            foreground=[
                ("disabled", AppTheme.TEXT_MUTED)
            ]
        )

        style.configure(
            "Secondary.TButton",
            font=AppTheme.FONT_BUTTON,
            padding=(14, 7),
            background=AppTheme.PANEL_ALT,
            foreground=AppTheme.TEXT_PRIMARY,
            borderwidth=0,
            focusthickness=0
        )
        style.map(
            "Secondary.TButton",
            background=[
                ("active", AppTheme.BORDER),
                ("pressed", AppTheme.BORDER)
            ]
        )

    def create_section_header(self, parent, title, description):
        header = tk.Frame(parent, bg=AppTheme.PANEL)
        header.pack(fill="x", padx=AppTheme.CONTENT_PADDING, pady=(18, 8))

        tk.Label(
            header,
            text=title,
            font=AppTheme.FONT_SECTION_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.PANEL,
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            header,
            text=description,
            font=AppTheme.FONT_SECTION_DESCRIPTION,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.PANEL,
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

    def apply_text_widget_theme(self, widget):
        widget.configure(**AppTheme.text_widget_options())

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=AppTheme.BACKGROUND)
        header_frame.pack(
            fill="x",
            padx=AppTheme.WINDOW_PADDING_X,
            pady=(AppTheme.HEADER_PADDING_Y, 8)
        )

        title_area = tk.Frame(header_frame, bg=AppTheme.BACKGROUND)
        title_area.pack(side="left", fill="x", expand=True)

        tk.Label(
            title_area,
            text="LOTTO ANALYZER",
            font=self.title_font,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.BACKGROUND,
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            title_area,
            text="과거 당첨 데이터 기반 통계 분석 후 추천번호를 생성합니다.",
            font=self.subtitle_font,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.BACKGROUND,
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

        info_area = tk.Frame(header_frame, bg=AppTheme.BACKGROUND)
        info_area.pack(side="right", anchor="e")

        tk.Label(
            info_area,
            text="VERSION 1.1.0",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.BACKGROUND
        ).pack(anchor="e")

        tk.Label(
            info_area,
            text="Developer  Y.YB",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.BACKGROUND
        ).pack(anchor="e", pady=(4, 0))

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=AppTheme.WINDOW_PADDING_X, pady=(6, 12))

        self.recommend_tab = tk.Frame(self.notebook, bg=self.panel_color)
        self.analysis_tab = tk.Frame(self.notebook, bg=self.panel_color)
        self.backtest_tab = tk.Frame(self.notebook, bg=self.panel_color)
        self.draw_search_tab = tk.Frame(self.notebook, bg=self.panel_color)
        self.log_tab = tk.Frame(self.notebook, bg=self.panel_color)

        self.notebook.add(self.recommend_tab, text="추천번호")
        self.notebook.add(self.analysis_tab, text="통계분석")
        self.notebook.add(self.backtest_tab, text="백테스트")
        self.notebook.add(self.draw_search_tab, text="회차조회")
        self.notebook.add(self.log_tab, text="시스템로그")

        self.create_recommend_tab()
        self.create_analysis_tab()
        self.create_backtest_tab()
        self.create_draw_search_tab()
        self.create_log_tab()

    def create_recommend_tab(self):
        button_frame = tk.Frame(self.recommend_tab, bg=self.panel_color)
        button_frame.pack(fill="x", pady=(18, 10))

        self.generate_button = ttk.Button(
            button_frame,
            text="최종 추천번호 5세트 생성",
            style="Primary.TButton",
            command=self.generate_recommendations
        )
        self.generate_button.pack()

        self.recommend_status_label = tk.Label(
            self.recommend_tab,
            text="상태 : 대기",
            font=self.default_font,
            fg=AppTheme.TEXT_SECONDARY,
            bg=self.panel_color,
            anchor="w"
        )
        self.recommend_status_label.pack(fill="x", padx=15)

        self.recommend_result_text = scrolledtext.ScrolledText(
            self.recommend_tab,
            width=105,
            height=28,
            font=self.text_font,
            relief="solid",
            borderwidth=1
        )
        self.recommend_result_text.pack(padx=15, pady=10)
        self.apply_text_widget_theme(self.recommend_result_text)

        self.recommend_result_text.insert(
            tk.END,
            "추천번호 생성 버튼을 눌러주세요.\n"
        )
        
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

    def create_analysis_tab(self):
        title_label = tk.Label(
            self.analysis_tab,
            text="통계분석",
            font=self.section_title_font,
            fg=AppTheme.TEXT_PRIMARY,
            bg=self.panel_color
        )
        title_label.pack(pady=(20, 8))

        description_label = tk.Label(
            self.analysis_tab,
            text="과거 당첨 데이터를 기준으로 주요 통계분석 결과를 조회합니다.",
            font=self.default_font,
            fg=AppTheme.TEXT_SECONDARY,
            bg=self.panel_color
        )
        description_label.pack(pady=5)

        button_frame = tk.Frame(self.analysis_tab, bg=self.panel_color)
        button_frame.pack(pady=10)

        self.analysis_button = ttk.Button(
            button_frame,
            text="통계분석 실행",
            style="Primary.TButton",
            command=self.run_analysis_summary
        )
        self.analysis_button.pack()

        self.analysis_text = scrolledtext.ScrolledText(
            self.analysis_tab,
            width=105,
            height=25,
            font=self.text_font,
            relief="solid",
            borderwidth=1
        )
        self.analysis_text.pack(padx=15, pady=10)
        self.apply_text_widget_theme(self.analysis_text)

        self.analysis_text.insert(
            tk.END,
            "통계분석 실행 버튼을 눌러주세요.\n"
        )

    def create_backtest_tab(self):
        title_label = tk.Label(
            self.backtest_tab,
            text="백테스트",
            font=self.section_title_font,
            fg=AppTheme.TEXT_PRIMARY,
            bg=self.panel_color
        )
        title_label.pack(pady=(25, 10))

        description_label = tk.Label(
            self.backtest_tab,
            text="최근 회차 기준 추천번호 성능을 검증하는 백테스트 결과를 표시할 예정입니다.",
            font=self.default_font,
            fg=AppTheme.TEXT_SECONDARY,
            bg=self.panel_color
        )
        description_label.pack(pady=5)

        button_frame = tk.Frame(
            self.backtest_tab,
            bg=self.panel_color
        )
        button_frame.pack(pady=10)

        self.backtest_button = ttk.Button(
            button_frame,
            text="최근 10회 백테스트 실행",
            style="Primary.TButton",
            command=self.run_backtest
        )
        self.backtest_button.pack()

        self.backtest_text = scrolledtext.ScrolledText(
            self.backtest_tab,
            width=105,
            height=25,
            font=self.text_font,
            relief="solid",
            borderwidth=1
        )
        self.backtest_text.pack(padx=15, pady=10)
        self.apply_text_widget_theme(self.backtest_text)

        self.backtest_text.insert(
            tk.END,
            "최근 10회 기준 최종 추천번호 백테스트를 실행할 수 있습니다.\n\n"
            "출력 항목\n"
            "- 평균 일치 개수\n"
            "- 최고 일치 개수\n"
            "- 번호 적중률\n"
            "- 등수 및 일치 개수 분포\n"
            "- 점수 구간별 결과\n"
        )

    def create_draw_search_tab(self):
        title_label = tk.Label(
            self.draw_search_tab,
            text="회차조회",
            font=self.section_title_font,
            fg=AppTheme.TEXT_PRIMARY,
            bg=self.panel_color
        )
        title_label.pack(pady=(25, 10))

        description_label = tk.Label(
            self.draw_search_tab,
            text="특정 회차의 당첨번호를 조회하는 기능을 추가할 예정입니다.",
            font=self.default_font,
            fg=AppTheme.TEXT_SECONDARY,
            bg=self.panel_color
        )
        description_label.pack(pady=5)

        search_frame = tk.Frame(self.draw_search_tab, bg=self.panel_color)
        search_frame.pack(pady=20)

        tk.Label(
            search_frame,
            text="회차 입력",
            font=self.default_font,
            fg=AppTheme.TEXT_SECONDARY,
            bg=self.panel_color
        ).pack(side="left", padx=5)

        self.draw_no_entry = tk.Entry(
            search_frame,
            width=15,
            font=self.default_font,
            bg=AppTheme.INPUT_BACKGROUND,
            fg=AppTheme.TEXT_PRIMARY,
            insertbackground=AppTheme.TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            highlightcolor=AppTheme.PRIMARY
        )
        self.draw_no_entry.pack(side="left", padx=5)

        search_button = ttk.Button(
            search_frame,
            text="조회",
            style="Secondary.TButton",
            command=self.search_draw_number
        )
        search_button.pack(side="left", padx=5)

        self.draw_search_text = scrolledtext.ScrolledText(
            self.draw_search_tab,
            width=105,
            height=24,
            font=self.text_font,
            relief="solid",
            borderwidth=1
        )
        self.draw_search_text.pack(padx=15, pady=10)
        self.apply_text_widget_theme(self.draw_search_text)

        self.draw_search_text.insert(
            tk.END,
            "회차조회 탭 준비 완료\n\n"            
        )

    def create_log_tab(self):
        title_label = tk.Label(
            self.log_tab,
            text="시스템로그",
            font=self.section_title_font,
            fg=AppTheme.TEXT_PRIMARY,
            bg=self.panel_color
        )
        title_label.pack(pady=(20, 10))

        self.log_text = scrolledtext.ScrolledText(
            self.log_tab,
            width=105,
            height=31,
            font=AppTheme.FONT_MONO,
            relief="solid",
            borderwidth=1
        )
        self.log_text.pack(padx=15, pady=10)
        self.apply_text_widget_theme(self.log_text)

        self.add_log("프로그램 시작")
        self.add_log("GUI 스타일 초기화 완료")
        self.add_log("탭 화면 초기화 완료")

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="Lotto Analyzer 준비 완료 | DB 연결 정상 | Developer : Y.YB",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=self.status_color,
            anchor="w",
            padx=AppTheme.WINDOW_PADDING_X,
            pady=7
        )
        self.status_bar.pack(fill="x", side="bottom")

    def set_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def generate_recommendations(self):
        self.generate_button.config(state="disabled")
        self.recommend_status_label.config(text="상태 : 추천번호 생성 중...")
        self.set_status("추천번호 생성 중...")
        self.add_log("추천번호 생성 시작")

        self.recommend_result_text.delete("1.0", tk.END)
        self.recommend_result_text.insert(tk.END, "추천번호를 생성하고 있습니다...\n")

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
        self.recommend_result_text.delete("1.0", tk.END)

        self.recommend_result_text.insert(tk.END, "=" * 90 + "\n")
        self.recommend_result_text.insert(tk.END, "                    최종 추천번호 5세트\n")
        self.recommend_result_text.insert(tk.END, "=" * 90 + "\n\n")

        for item in recommendations:
            pattern = item["pattern"]

            self.recommend_result_text.insert(tk.END, f"[{item['index']}세트]\n")
            self.recommend_result_text.insert(tk.END, f"번호   : {item['numbers']}\n")
            self.recommend_result_text.insert(tk.END, f"총점   : {item['total_score']}\n")
            self.recommend_result_text.insert(
                tk.END,
                f"홀짝   : {pattern['odd_even']['pattern']}\n"
            )
            self.recommend_result_text.insert(
                tk.END,
                f"고저   : {pattern['low_high']['pattern']}\n"
            )
            self.recommend_result_text.insert(
                tk.END,
                f"번호합 : {pattern['sum']['sum']}\n"
            )
            self.recommend_result_text.insert(tk.END, "-" * 90 + "\n")

        self.recommend_result_text.insert(
            tk.END,
            "\n※ 본 추천번호는 과거 데이터 기반 통계 분석 결과입니다.\n"
        )

        self.generate_button.config(state="normal")
        self.recommend_status_label.config(text="상태 : 추천번호 생성 완료")
        self.set_status("추천번호 생성 완료 | Lotto Analyzer 정상 동작 중")
        self.add_log("추천번호 생성 완료")

    def _handle_recommendation_error(self, error):
        self.generate_button.config(state="normal")
        self.recommend_status_label.config(text="상태 : 오류 발생")
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