import tkinter as tk
from tkinter import messagebox

from src.app.recommendation_service import RecommendationService


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("로또 분석기")
        self.root.geometry("720x520")
        self.root.resizable(False, False)

        self.recommendation_service = RecommendationService()

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="로또 분석기",
            font=("맑은 고딕", 22, "bold")
        )
        title_label.pack(pady=20)

        description_label = tk.Label(
            self.root,
            text="과거 당첨 데이터 기반 통계 분석 후 추천번호를 생성합니다.",
            font=("맑은 고딕", 11)
        )
        description_label.pack(pady=5)

        generate_button = tk.Button(
            self.root,
            text="최종 추천번호 5세트 생성",
            font=("맑은 고딕", 13, "bold"),
            width=28,
            height=2,
            command=self.generate_recommendations
        )
        generate_button.pack(pady=20)

        self.result_text = tk.Text(
            self.root,
            width=78,
            height=18,
            font=("맑은 고딕", 11)
        )
        self.result_text.pack(pady=10)

    def generate_recommendations(self):
        try:
            self.result_text.delete("1.0", tk.END)

            recommendations = self.recommendation_service.get_final_recommendations()

            self.result_text.insert(tk.END, "최종 추천번호 5세트\n")
            self.result_text.insert(tk.END, "-" * 60 + "\n\n")

            for item in recommendations:
                pattern = item["pattern"]

                self.result_text.insert(
                    tk.END,
                    f"{item['index']}. {item['numbers']} | "
                    f"총점 {item['total_score']} | "
                    f"홀짝 {pattern['odd_even']['pattern']} | "
                    f"고저 {pattern['low_high']['pattern']} | "
                    f"합계 {pattern['sum']['sum']}\n"
                )

            self.result_text.insert(
                tk.END,
                "\n※ 본 추천번호는 과거 데이터 기반 통계 분석 결과입니다.\n"
            )

        except Exception as e:
            messagebox.showerror("오류", f"추천번호 생성 중 오류가 발생했습니다.\n\n{e}")

    def run(self):
        self.root.mainloop()