import tkinter as tk

from src.gui.theme import AppTheme


class AppCard(tk.Frame):
    """Lotto Analyzer 화면에서 공통으로 사용하는 기본 카드."""

    def __init__(self, parent, title=None, **kwargs):
        super().__init__(
            parent,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            **kwargs
        )

        if title:
            tk.Label(
                self,
                text=title,
                font=AppTheme.FONT_CARD_TITLE,
                fg=AppTheme.TEXT_PRIMARY,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w"
            ).pack(
                fill="x",
                padx=AppTheme.CARD_PADDING,
                pady=(15, 8)
            )


class SummaryCard(tk.Frame):
    """통계 및 백테스트 요약값을 표시하는 공통 카드."""

    def __init__(
        self,
        parent,
        title,
        value="-",
        description="",
        accent_color=None,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            **kwargs
        )

        self.accent_color = accent_color or AppTheme.PRIMARY

        accent = tk.Frame(self, bg=self.accent_color, height=4)
        accent.pack(fill="x")

        content = tk.Frame(self, bg=AppTheme.CARD_BACKGROUND)
        content.pack(fill="both", expand=True, padx=16, pady=14)

        self.title_label = tk.Label(
            content,
            text=title,
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.title_label.pack(fill="x")

        self.value_label = tk.Label(
            content,
            text=str(value),
            font=(AppTheme.FONT_FAMILY, 18, "bold"),
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.value_label.pack(fill="x", pady=(8, 2))

        self.description_label = tk.Label(
            content,
            text=description,
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        )
        self.description_label.pack(fill="x")

    def set_value(self, value, description=None):
        self.value_label.config(text=str(value))
        if description is not None:
            self.description_label.config(text=description)
