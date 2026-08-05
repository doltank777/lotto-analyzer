import tkinter as tk

from src.gui.theme import AppTheme


class MetricBadge(tk.Frame):
    """라벨과 값을 한 줄로 표시하는 작은 지표 배지."""

    def __init__(self, parent, label, value, **kwargs):
        super().__init__(
            parent,
            bg=AppTheme.METRIC_BACKGROUND,
            **kwargs
        )

        tk.Label(
            self,
            text=label,
            font=(AppTheme.FONT_FAMILY, 8),
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.METRIC_BACKGROUND
        ).pack(side="left")

        self.value_label = tk.Label(
            self,
            text=str(value),
            font=(AppTheme.FONT_FAMILY, 9, "bold"),
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.METRIC_BACKGROUND
        )
        self.value_label.pack(side="left", padx=(7, 0))

    def set_value(self, value):
        self.value_label.config(text=str(value))
