import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from src.app.recommendation_service import RecommendationService


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lotto Analyzer(1.0.3)")
        self.root.geometry("900x720")
        self.root.resizable(False, False)

        self.recommendation_service = RecommendationService()

        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_tabs()

    def create_header(self):
        header_frame = tk.Frame(self.root)
        header_frame.pack(fill="x", pady=(15, 5))

        title_label = tk.Label(
            header_frame,
            text="로또 분석기 (Lotto Analyzer)",
            font=("맑은 고딕", 24, "bold")
        )
        title_label.pack()

        description_label = tk.Label(
            header_frame,
            text="과거 당첨 데이터 기반 통계 분석 후 추천번호를 생성합니다.",
            font=("맑은 고딕", 11)
        )
        description_label.pack(pady=(3, 0))

        developer_label = tk.Label(
            header_frame,
            text="Developer : Y.YB",
            font=("맑은 고딕", 9),
            fg="gray"
        )
        developer_label.pack(pady=(2, 5))

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.recommend_tab = tk.Frame(self.notebook)
        self.analysis_tab = tk.Frame(self.notebook)
        self.backtest_tab = tk.Frame(self.notebook)
        self.draw_search_tab = tk.Frame(self.notebook)
        self.log_tab = tk.Frame(self.notebook)

        self.notebook.add(self.recommend_tab, text="추천번호")
        self.notebook.add(self.analysis_tab, text="분석")
        self.notebook.add(self.backtest_tab, text="백테스트")
        self.notebook.add(self.draw_search_tab, text="회차조회")
        self.notebook.add(self.log_tab, text="로그")

        self.create_recommend_tab()
        self.create_analysis_tab()
        self.create_backtest_tab()
        self.create_draw_search_tab()
        self.create_log_tab()

    def create_recommend_tab(self):
        button_frame = tk.Frame(self.recommend_tab)
        button_frame.pack(fill="x", pady=15)

        generate_button = tk.Button(
            button_frame,
            text="최종 추천번호 5세트 생성",
            font=("맑은 고딕", 13, "bold"),
            width=30,
            height=2,
            command=self.generate_recommendations
        )
        generate_button.pack()

        self.recommend_status_label = tk.Label(
            self.recommend_tab,
            text="상태 : 대기",
            font=("맑은 고딕", 10),
            anchor="w"
        )
        self.recommend_status_label.pack(fill="x", padx=10)

        self.recommend_result_text = scrolledtext.ScrolledText(
            self.recommend_tab,
            width=100,
            height=27,
            font=("Consolas", 11)
        )
        self.recommend_result_text.pack(padx=10, pady=10)

        self.recommend_result_text.insert(
            tk.END,
            "추천번호 생성 버튼을 눌러주세요.\n"
        )

    def create_analysis_tab(self):
        title_label = tk.Label(
            self.analysis_tab,
            text="분석 화면",
            font=("맑은 고딕", 16, "bold")
        )
        title_label.pack(pady=(30, 10))

        description_label = tk.Label(
            self.analysis_tab,
            text="번호 출현 빈도, HOT/COLD 번호, Pair, Triple, 패턴 분석 결과를 표시할 예정입니다.",
            font=("맑은 고딕", 11)
        )
        description_label.pack(pady=5)

        self.analysis_text = scrolledtext.ScrolledText(
            self.analysis_tab,
            width=100,
            height=27,
            font=("Consolas", 11)
        )
        self.analysis_text.pack(padx=10, pady=20)

        self.analysis_text.insert(
            tk.END,
            "분석 탭 준비 완료\n\n"
            "다음 단계에서 아래 기능을 연결합니다.\n"
            "- 전체 번호 출현 빈도\n"
            "- HOT 번호\n"
            "- COLD 번호\n"
            "- Pair TOP20\n"
            "- Triple TOP20\n"
            "- 패턴 분석\n"
            "- 장기 미출현 번호\n"
        )

    def create_backtest_tab(self):
        title_label = tk.Label(
            self.backtest_tab,
            text="백테스트 화면",
            font=("맑은 고딕", 16, "bold")
        )
        title_label.pack(pady=(30, 10))

        description_label = tk.Label(
            self.backtest_tab,
            text="최근 회차 기준 추천번호 성능을 검증하는 백테스트 결과를 표시할 예정입니다.",
            font=("맑은 고딕", 11)
        )
        description_label.pack(pady=5)

        self.backtest_text = scrolledtext.ScrolledText(
            self.backtest_tab,
            width=100,
            height=27,
            font=("Consolas", 11)
        )
        self.backtest_text.pack(padx=10, pady=20)

        self.backtest_text.insert(
            tk.END,
            "백테스트 탭 준비 완료\n\n"
            "다음 단계에서 아래 기능을 연결합니다.\n"
            "- 최근 10회 백테스트\n"
            "- 최근 30회 백테스트\n"
            "- 평균 일치 개수\n"
            "- 최고 일치 개수\n"
            "- 번호 적중률\n"
            "- 일치 개수 분포\n"
        )

    def create_draw_search_tab(self):
        title_label = tk.Label(
            self.draw_search_tab,
            text="회차조회 화면",
            font=("맑은 고딕", 16, "bold")
        )
        title_label.pack(pady=(30, 10))

        description_label = tk.Label(
            self.draw_search_tab,
            text="특정 회차의 당첨번호를 조회하는 기능을 추가할 예정입니다.",
            font=("맑은 고딕", 11)
        )
        description_label.pack(pady=5)

        search_frame = tk.Frame(self.draw_search_tab)
        search_frame.pack(pady=20)

        tk.Label(
            search_frame,
            text="회차 입력",
            font=("맑은 고딕", 11)
        ).pack(side="left", padx=5)

        self.draw_no_entry = tk.Entry(
            search_frame,
            width=15,
            font=("맑은 고딕", 11)
        )
        self.draw_no_entry.pack(side="left", padx=5)

        search_button = tk.Button(
            search_frame,
            text="조회",
            font=("맑은 고딕", 10),
            width=10,
            command=self.show_draw_search_ready_message
        )
        search_button.pack(side="left", padx=5)

        self.draw_search_text = scrolledtext.ScrolledText(
            self.draw_search_tab,
            width=100,
            height=23,
            font=("Consolas", 11)
        )
        self.draw_search_text.pack(padx=10, pady=10)

        self.draw_search_text.insert(
            tk.END,
            "회차조회 탭 준비 완료\n\n"
            "다음 단계에서 입력한 회차의 당첨번호 조회 기능을 연결합니다.\n"
        )

    def create_log_tab(self):
        title_label = tk.Label(
            self.log_tab,
            text="로그",
            font=("맑은 고딕", 16, "bold")
        )
        title_label.pack(pady=(20, 10))

        self.log_text = scrolledtext.ScrolledText(
            self.log_tab,
            width=100,
            height=30,
            font=("Consolas", 10)
        )
        self.log_text.pack(padx=10, pady=10)

        self.add_log("프로그램 시작")
        self.add_log("GUI 탭 화면 초기화 완료")

    def generate_recommendations(self):
        try:
            self.recommend_status_label.config(text="상태 : 추천번호 생성 중...")
            self.add_log("추천번호 생성 시작")

            self.root.update_idletasks()

            self.recommend_result_text.delete("1.0", tk.END)

            recommendations = self.recommendation_service.get_final_recommendations()

            self.recommend_result_text.insert(tk.END, "=" * 85 + "\n")
            self.recommend_result_text.insert(tk.END, "               최종 추천번호 5세트\n")
            self.recommend_result_text.insert(tk.END, "=" * 85 + "\n\n")

            for item in recommendations:
                pattern = item["pattern"]

                self.recommend_result_text.insert(
                    tk.END,
                    f"[{item['index']}세트]\n"
                )

                self.recommend_result_text.insert(
                    tk.END,
                    f"번호 : {item['numbers']}\n"
                )

                self.recommend_result_text.insert(
                    tk.END,
                    f"총점 : {item['total_score']}\n"
                )

                self.recommend_result_text.insert(
                    tk.END,
                    f"홀짝 : {pattern['odd_even']['pattern']}\n"
                )

                self.recommend_result_text.insert(
                    tk.END,
                    f"고저 : {pattern['low_high']['pattern']}\n"
                )

                self.recommend_result_text.insert(
                    tk.END,
                    f"번호합 : {pattern['sum']['sum']}\n"
                )

                self.recommend_result_text.insert(
                    tk.END,
                    "-" * 85 + "\n"
                )

            self.recommend_result_text.insert(
                tk.END,
                "\n※ 본 추천번호는 과거 데이터 기반 통계 분석 결과입니다.\n"
            )

            self.recommend_status_label.config(text="상태 : 추천번호 생성 완료")
            self.add_log("추천번호 생성 완료")

        except Exception as e:
            self.recommend_status_label.config(text="상태 : 오류 발생")
            self.add_log(f"추천번호 생성 오류: {e}")

            messagebox.showerror(
                "오류",
                f"추천번호 생성 중 오류가 발생했습니다.\n\n{e}"
            )

    def show_draw_search_ready_message(self):
        messagebox.showinfo(
            "안내",
            "회차조회 기능은 다음 단계에서 연결합니다."
        )
        self.add_log("회차조회 버튼 클릭")

    def add_log(self, message):
        if hasattr(self, "log_text"):
            self.log_text.insert(tk.END, f"- {message}\n")
            self.log_text.see(tk.END)

    def run(self):
        self.root.mainloop()