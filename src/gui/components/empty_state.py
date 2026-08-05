import tkinter as tk

from src.gui.theme import AppTheme


class EmptyState(tk.Frame):
    """결과가 없거나 작업 중일 때 사용하는 공통 안내 화면."""

    def __init__(
        self,
        parent,
        message,
        description="",
        icon_text="6",
        **kwargs
    ):
        super().__init__(
            parent,
            bg=AppTheme.CARD_BACKGROUND,
            **kwargs
        )

        icon_canvas = tk.Canvas(
            self,
            width=64,
            height=64,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=0
        )
        icon_canvas.pack()

        icon_canvas.create_oval(
            7,
            7,
            57,
            57,
            fill=AppTheme.EMPTY_ICON_BACKGROUND,
            outline=""
        )
        icon_canvas.create_text(
            32,
            32,
            text=icon_text,
            font=(AppTheme.FONT_FAMILY, 18, "bold"),
            fill=AppTheme.PRIMARY
        )

        tk.Label(
            self,
            text=message,
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND
        ).pack(pady=(12, 4))

        if description:
            tk.Label(
                self,
                text=description,
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_SECONDARY,
                bg=AppTheme.CARD_BACKGROUND
            ).pack()
