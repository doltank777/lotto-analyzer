import tkinter as tk
from tkinter import messagebox, scrolledtext

from src.app.recommendation_service import RecommendationService


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lotto Analyzer")
        self.root.geometry("820x700")
        self.root.resizable(False, False)

        self.recommendation_service = RecommendationService()

        self.create_widgets()

    def create_widgets(self):

        title_label = tk.Label(
            self.root,
            text="로또 분석기 (Lotto Analyzer)",
            font=("맑은 고딕", 24, "bold")
        )
        title_label.pack(pady=(20, 5))

        description_label = tk.Label(
            self.root,
            text="과거 당첨 데이터 기반 통계 분석 후 추천번호를 생성합니다.",
            font=("맑은 고딕", 11)
        )
        description_label.pack()

        developer_label = tk.Label(
            self.root,
            text="Developer : Y.YB",
            font=("맑은 고딕", 9),
            fg="gray"
        )
        developer_label.pack(pady=(2, 15))

        generate_button = tk.Button(
            self.root,
            text="최종 추천번호 5세트 생성",
            font=("맑은 고딕", 13, "bold"),
            width=30,
            height=2,
            command=self.generate_recommendations
        )
        generate_button.pack(pady=10)

        self.status_label = tk.Label(
            self.root,
            text="상태 : 대기",
            font=("맑은 고딕", 10),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=15)

        self.result_text = scrolledtext.ScrolledText(
            self.root,
            width=95,
            height=26,
            font=("Consolas", 11)
        )

        self.result_text.pack(padx=15, pady=10)

        self.result_text.insert(
            tk.END,
            "프로그램이 준비되었습니다.\n"
            "버튼을 눌러 추천번호를 생성하세요.\n"
        )

    def generate_recommendations(self):

        try:

            self.status_label.config(text="상태 : 추천번호 생성 중...")

            self.root.update_idletasks()

            self.result_text.delete("1.0", tk.END)

            recommendations = self.recommendation_service.get_final_recommendations()

            self.result_text.insert(tk.END, "=" * 85 + "\n")
            self.result_text.insert(tk.END, "               최종 추천번호 5세트\n")
            self.result_text.insert(tk.END, "=" * 85 + "\n\n")

            for item in recommendations:

                pattern = item["pattern"]

                self.result_text.insert(
                    tk.END,
                    f"[{item['index']}세트]\n"
                )

                self.result_text.insert(
                    tk.END,
                    f"번호 : {item['numbers']}\n"
                )

                self.result_text.insert(
                    tk.END,
                    f"총점 : {item['total_score']}\n"
                )

                self.result_text.insert(
                    tk.END,
                    f"홀짝 : {pattern['odd_even']['pattern']}\n"
                )

                self.result_text.insert(
                    tk.END,
                    f"고저 : {pattern['low_high']['pattern']}\n"
                )

                self.result_text.insert(
                    tk.END,
                    f"번호합 : {pattern['sum']['sum']}\n"
                )

                self.result_text.insert(
                    tk.END,
                    "-" * 85 + "\n"
                )

            self.result_text.insert(
                tk.END,
                "\n※ 본 추천번호는 과거 데이터 기반 통계 분석 결과입니다.\n"
            )

            self.status_label.config(text="상태 : 추천번호 생성 완료")

        except Exception as e:

            self.status_label.config(text="상태 : 오류 발생")

            messagebox.showerror(
                "오류",
                f"추천번호 생성 중 오류가 발생했습니다.\n\n{e}"
            )

    def run(self):
        self.root.mainloop()