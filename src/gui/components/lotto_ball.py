import tkinter as tk

from src.gui.theme import AppTheme


class LottoBall(tk.Canvas):
    """번호 구간별 색상을 적용한 로또 번호공 컴포넌트."""

    def __init__(
        self,
        parent,
        number,
        size=52,
        background=None,
        show_shadow=True,
        **kwargs
    ):
        self.number = int(number)
        self.size = size
        self.background = background or AppTheme.CARD_BACKGROUND

        super().__init__(
            parent,
            width=size,
            height=size,
            bg=self.background,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )

        self._draw_ball(show_shadow)

    def _draw_ball(self, show_shadow):
        color = AppTheme.get_lotto_ball_color(self.number)
        padding = max(2, int(self.size * 0.04))
        shadow_offset = max(2, int(self.size * 0.04))

        if show_shadow:
            self.create_oval(
                padding + shadow_offset,
                padding + shadow_offset,
                self.size - padding,
                self.size - padding,
                fill=AppTheme.BALL_SHADOW,
                outline=""
            )

        self.create_oval(
            padding,
            padding,
            self.size - padding - shadow_offset,
            self.size - padding - shadow_offset,
            fill=color,
            outline=""
        )

        highlight_left = int(self.size * 0.18)
        highlight_top = int(self.size * 0.13)
        highlight_right = int(self.size * 0.45)
        highlight_bottom = int(self.size * 0.31)

        self.create_oval(
            highlight_left,
            highlight_top,
            highlight_right,
            highlight_bottom,
            fill=AppTheme.BALL_HIGHLIGHT,
            outline=""
        )

        center = (self.size - shadow_offset) / 2
        self.create_text(
            center,
            center,
            text=f"{self.number:02d}",
            font=(
                AppTheme.FONT_FAMILY,
                max(9, int(self.size * 0.21)),
                "bold"
            ),
            fill=AppTheme.TEXT_INVERSE
        )
