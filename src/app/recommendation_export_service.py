from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas


class RecommendationExportService:
    """추천번호 결과를 PNG, PDF, TXT 형식으로 저장한다."""

    BALL_COLORS = {
        "yellow": "#F2B720",
        "blue": "#3B82C4",
        "red": "#E35757",
        "gray": "#718096",
        "green": "#3FA36C",
    }

    def export_png(self, file_path, recommendations, version="1.3.0"):
        self._validate_recommendations(recommendations)

        path = Path(file_path)
        width = 1200
        margin = 70
        header_height = 170
        card_height = 165
        footer_height = 90
        gap = 20
        height = (
            header_height
            + len(recommendations) * (card_height + gap)
            + footer_height
            + margin
        )

        image = Image.new("RGB", (width, height), "#F3F6FA")
        draw = ImageDraw.Draw(image)

        title_font = self._load_font(42, bold=True)
        subtitle_font = self._load_font(21)
        card_title_font = self._load_font(24, bold=True)
        ball_font = self._load_font(22, bold=True)
        body_font = self._load_font(18)
        small_font = self._load_font(15)

        draw.text((margin, 45), "Lotto Analyzer", font=title_font, fill="#182033")
        draw.text(
            (margin, 105),
            "과거 당첨 데이터 기반 통계 분석 후 추천번호 생성",
            font=subtitle_font,
            fill="#667085",
        )

        current_y = header_height

        for item in recommendations:
            left = margin
            top = current_y
            right = width - margin
            bottom = top + card_height

            draw.rounded_rectangle(
                (left, top, right, bottom),
                radius=18,
                fill="#FFFFFF",
                outline="#E4E9F0",
                width=2,
            )
            draw.rectangle((left, top, left + 7, bottom), fill="#2D6CDF")

            draw.text(
                (left + 30, top + 22),
                f"추천 조합 {item['index']:02d}",
                font=card_title_font,
                fill="#182033",
            )

            score_text = f"종합점수 {item['total_score']:.2f}"
            score_box = draw.textbbox((0, 0), score_text, font=body_font)
            score_width = score_box[2] - score_box[0]
            draw.text(
                (right - score_width - 28, top + 26),
                score_text,
                font=body_font,
                fill="#2D6CDF",
            )

            ball_y = top + 78
            ball_x = left + 32
            ball_size = 58
            ball_gap = 18

            for number in item["numbers"]:
                draw.ellipse(
                    (ball_x, ball_y, ball_x + ball_size, ball_y + ball_size),
                    fill=self._get_ball_color(number),
                )
                number_text = f"{number:02d}"
                number_box = draw.textbbox((0, 0), number_text, font=ball_font)
                number_width = number_box[2] - number_box[0]
                number_height = number_box[3] - number_box[1]
                draw.text(
                    (
                        ball_x + (ball_size - number_width) / 2,
                        ball_y + (ball_size - number_height) / 2 - 3,
                    ),
                    number_text,
                    font=ball_font,
                    fill="#FFFFFF",
                )
                ball_x += ball_size + ball_gap

            pattern = item["pattern"]
            metrics = [
                f"홀짝 {pattern['odd_even']['pattern']}",
                f"고저 {pattern['low_high']['pattern']}",
                f"번호합 {pattern['sum']['sum']}",
            ]

            metric_x = right - 345
            metric_y = top + 96
            for metric in metrics:
                draw.text(
                    (metric_x, metric_y),
                    metric,
                    font=body_font,
                    fill="#667085",
                )
                metric_y += 28

            current_y += card_height + gap

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text(
            (margin, current_y + 20),
            f"생성일시 {generated_at}",
            font=small_font,
            fill="#667085",
        )
        draw.text(
            (width - margin - 150, current_y + 20),
            f"Version {version}",
            font=small_font,
            fill="#667085",
        )

        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, "PNG")
        return str(path)

    def export_pdf(self, file_path, recommendations, version="1.3.0"):
        self._validate_recommendations(recommendations)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
        pdf = canvas.Canvas(str(path), pagesize=A4)
        page_width, page_height = A4

        pdf.setTitle("Lotto Analyzer 추천번호")
        pdf.setFont("HYSMyeongJo-Medium", 22)
        pdf.drawString(48, page_height - 55, "Lotto Analyzer")

        pdf.setFont("HYSMyeongJo-Medium", 11)
        pdf.setFillColorRGB(0.4, 0.44, 0.52)
        pdf.drawString(
            48,
            page_height - 78,
            "과거 당첨 데이터 기반 통계 분석 후 추천번호 생성",
        )

        y = page_height - 120

        for item in recommendations:
            if y < 150:
                pdf.showPage()
                y = page_height - 60

            pdf.setFillColorRGB(0.96, 0.97, 0.98)
            pdf.roundRect(
                45,
                y - 95,
                page_width - 90,
                105,
                10,
                fill=1,
                stroke=0,
            )

            pdf.setFillColorRGB(0.11, 0.13, 0.2)
            pdf.setFont("HYSMyeongJo-Medium", 14)
            pdf.drawString(62, y - 18, f"추천 조합 {item['index']:02d}")

            pdf.setFont("HYSMyeongJo-Medium", 10)
            pdf.setFillColorRGB(0.18, 0.42, 0.87)
            pdf.drawRightString(
                page_width - 62,
                y - 18,
                f"종합점수 {item['total_score']:.2f}",
            )

            number_x = 68
            number_y = y - 61

            for number in item["numbers"]:
                red, green, blue = self._hex_to_rgb(
                    self._get_ball_color(number)
                )
                pdf.setFillColorRGB(red, green, blue)
                pdf.circle(number_x, number_y, 16, fill=1, stroke=0)

                pdf.setFillColorRGB(1, 1, 1)
                pdf.setFont("HYSMyeongJo-Medium", 10)
                pdf.drawCentredString(
                    number_x,
                    number_y - 4,
                    f"{number:02d}",
                )
                number_x += 47

            pattern = item["pattern"]
            pdf.setFillColorRGB(0.4, 0.44, 0.52)
            pdf.setFont("HYSMyeongJo-Medium", 9)
            pdf.drawString(365, y - 48, f"홀짝 {pattern['odd_even']['pattern']}")
            pdf.drawString(365, y - 67, f"고저 {pattern['low_high']['pattern']}")
            pdf.drawString(365, y - 86, f"번호합 {pattern['sum']['sum']}")

            y -= 125

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.setFillColorRGB(0.4, 0.44, 0.52)
        pdf.setFont("HYSMyeongJo-Medium", 9)
        pdf.drawString(48, 42, f"생성일시 {generated_at}")
        pdf.drawRightString(page_width - 48, 42, f"Version {version}")
        pdf.save()

        return str(path)

    def export_txt(self, file_path, recommendations, version="1.3.0"):
        self._validate_recommendations(recommendations)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "Lotto Analyzer",
            "과거 당첨 데이터 기반 통계 분석 후 추천번호 생성",
            "=" * 60,
            "",
        ]

        for item in recommendations:
            pattern = item["pattern"]
            numbers = " ".join(f"{number:02d}" for number in item["numbers"])

            lines.extend([
                f"[추천 조합 {item['index']:02d}]",
                f"번호: {numbers}",
                f"종합점수: {item['total_score']:.2f}",
                f"홀짝: {pattern['odd_even']['pattern']}",
                f"고저: {pattern['low_high']['pattern']}",
                f"번호합: {pattern['sum']['sum']}",
                "-" * 60,
            ])

        lines.extend([
            "",
            f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Version: {version}",
            "※ 본 추천번호는 과거 데이터 기반 통계 분석 결과입니다.",
        ])

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _validate_recommendations(self, recommendations):
        if not recommendations:
            raise ValueError("내보낼 추천번호가 없습니다.")

    def _get_ball_color(self, number):
        if 1 <= number <= 10:
            return self.BALL_COLORS["yellow"]
        if 11 <= number <= 20:
            return self.BALL_COLORS["blue"]
        if 21 <= number <= 30:
            return self.BALL_COLORS["red"]
        if 31 <= number <= 40:
            return self.BALL_COLORS["gray"]
        return self.BALL_COLORS["green"]

    def _load_font(self, size, bold=False):
        candidates = []

        if bold:
            candidates.extend([
                Path("C:/Windows/Fonts/malgunbd.ttf"),
                Path("C:/Windows/Fonts/NanumGothicBold.ttf"),
            ])
        else:
            candidates.extend([
                Path("C:/Windows/Fonts/malgun.ttf"),
                Path("C:/Windows/Fonts/NanumGothic.ttf"),
            ])

        candidates.append(
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
            if bold
            else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        )

        for font_path in candidates:
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size)

        return ImageFont.load_default()

    def _hex_to_rgb(self, color):
        color = color.lstrip("#")
        return tuple(
            int(color[index:index + 2], 16) / 255
            for index in (0, 2, 4)
        )
