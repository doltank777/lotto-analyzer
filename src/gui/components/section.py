import tkinter as tk

from src.gui.theme import AppTheme


class SectionCard(tk.Frame):
    """대시보드의 분석 영역을 구분하는 공통 섹션 카드."""

    def __init__(self, parent, title, description="", **kwargs):
        super().__init__(
            parent,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            **kwargs
        )

        header = tk.Frame(self, bg=AppTheme.CARD_BACKGROUND)
        header.pack(fill="x", padx=16, pady=(14, 10))

        tk.Label(
            header,
            text=title,
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(fill="x")

        if description:
            tk.Label(
                header,
                text=description,
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_SECONDARY,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w"
            ).pack(fill="x", pady=(4, 0))

        divider = tk.Frame(self, bg=AppTheme.DIVIDER, height=1)
        divider.pack(fill="x")

        self.content = tk.Frame(self, bg=AppTheme.CARD_BACKGROUND)
        self.content.pack(fill="both", expand=True, padx=16, pady=14)


class SummaryList(tk.Frame):
    """분석 결과 목록을 제목과 함께 표시하는 공통 컴포넌트."""

    def __init__(
        self,
        parent,
        title,
        rows=None,
        empty_message="표시할 데이터가 없습니다.",
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.CARD_BACKGROUND, **kwargs)

        self.empty_message = empty_message

        tk.Label(
            self,
            text=title,
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(fill="x", pady=(0, 8))

        self.rows_frame = tk.Frame(self, bg=AppTheme.CARD_BACKGROUND)
        self.rows_frame.pack(fill="both", expand=True)

        self.set_rows(rows or [])

    def clear(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

    def set_rows(self, rows):
        self.clear()

        if not rows:
            tk.Label(
                self.rows_frame,
                text=self.empty_message,
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w"
            ).pack(fill="x", pady=6)
            return

        for index, row in enumerate(rows, start=1):
            primary = row.get("primary", "")
            secondary = row.get("secondary", "")
            detail = row.get("detail", "")

            item = tk.Frame(
                self.rows_frame,
                bg=(
                    AppTheme.INPUT_BACKGROUND
                    if index % 2 == 1
                    else AppTheme.CARD_BACKGROUND
                )
            )
            item.pack(fill="x", pady=1)

            rank_label = tk.Label(
                item,
                text=f"{index:02d}",
                font=(AppTheme.FONT_FAMILY, 8, "bold"),
                fg=AppTheme.TEXT_MUTED,
                bg=item["bg"],
                width=3,
                anchor="w"
            )
            rank_label.pack(side="left", padx=(8, 4), pady=6)

            tk.Label(
                item,
                text=str(primary),
                font=AppTheme.FONT_BODY_BOLD,
                fg=AppTheme.TEXT_PRIMARY,
                bg=item["bg"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True, pady=6)

            if detail:
                tk.Label(
                    item,
                    text=str(detail),
                    font=AppTheme.FONT_SMALL,
                    fg=AppTheme.TEXT_SECONDARY,
                    bg=item["bg"],
                    anchor="e"
                ).pack(side="right", padx=(8, 4), pady=6)

            if secondary:
                tk.Label(
                    item,
                    text=str(secondary),
                    font=AppTheme.FONT_BODY_BOLD,
                    fg=AppTheme.PRIMARY,
                    bg=item["bg"],
                    anchor="e"
                ).pack(side="right", padx=(4, 8), pady=6)
