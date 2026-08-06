import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.gui.theme import AppTheme


class ChartCard(tk.Frame):
    """Tkinter 화면에 Matplotlib 차트를 표시하는 공통 카드."""

    def __init__(
        self,
        parent,
        title,
        description="",
        figure_height=3.2,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            **kwargs
        )

        self.title = title
        self.description = description
        self.figure_height = figure_height
        self.canvas = None
        self.figure = None
        self.axes = None

        self._build_header()
        self._build_chart_area()

    def _build_header(self):
        header = tk.Frame(self, bg=AppTheme.CARD_BACKGROUND)
        header.pack(fill="x", padx=16, pady=(14, 10))

        tk.Label(
            header,
            text=self.title,
            font=AppTheme.FONT_CARD_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w"
        ).pack(fill="x")

        if self.description:
            tk.Label(
                header,
                text=self.description,
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_SECONDARY,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w"
            ).pack(fill="x", pady=(4, 0))

        tk.Frame(
            self,
            bg=AppTheme.DIVIDER,
            height=1
        ).pack(fill="x")

    def _build_chart_area(self):
        self.chart_container = tk.Frame(
            self,
            bg=AppTheme.CARD_BACKGROUND
        )
        self.chart_container.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        self._create_figure()

    def _create_figure(self):
        self.figure = Figure(
            figsize=(6.4, self.figure_height),
            dpi=100,
            facecolor=AppTheme.CARD_BACKGROUND
        )
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.chart_container
        )
        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        self._apply_axes_style()

    def _apply_axes_style(self):
        self.axes.set_facecolor(AppTheme.CARD_BACKGROUND)

        self.axes.tick_params(
            axis="x",
            colors=AppTheme.TEXT_SECONDARY,
            labelsize=9
        )
        self.axes.tick_params(
            axis="y",
            colors=AppTheme.TEXT_SECONDARY,
            labelsize=9
        )

        for spine in self.axes.spines.values():
            spine.set_color(AppTheme.BORDER)

        self.axes.grid(
            axis="y",
            color=AppTheme.DIVIDER,
            linewidth=0.8,
            alpha=0.9
        )
        self.axes.set_axisbelow(True)

    def clear(self):
        self.axes.clear()
        self._apply_axes_style()

    def draw_bar_chart(
        self,
        labels,
        values,
        value_format="{:.0f}",
        y_label="",
        rotate_labels=0,
        color=None
    ):
        self.clear()

        if not labels or not values:
            self.show_empty_state()
            return

        bar_color = color or AppTheme.PRIMARY
        bars = self.axes.bar(
            labels,
            values,
            color=bar_color
        )

        if y_label:
            self.axes.set_ylabel(
                y_label,
                color=AppTheme.TEXT_SECONDARY,
                fontsize=9
            )

        if rotate_labels:
            self.axes.tick_params(
                axis="x",
                labelrotation=rotate_labels
            )

        self._add_bar_value_labels(
            bars,
            value_format=value_format
        )
        self._finish_draw()

    def draw_horizontal_bar_chart(
        self,
        labels,
        values,
        value_format="{:.0f}",
        x_label="",
        color=None
    ):
        self.clear()

        if not labels or not values:
            self.show_empty_state()
            return

        bar_color = color or AppTheme.PRIMARY
        bars = self.axes.barh(
            labels,
            values,
            color=bar_color
        )

        if x_label:
            self.axes.set_xlabel(
                x_label,
                color=AppTheme.TEXT_SECONDARY,
                fontsize=9
            )

        self.axes.invert_yaxis()
        self._add_horizontal_bar_value_labels(
            bars,
            value_format=value_format
        )
        self._finish_draw()

    def draw_line_chart(
        self,
        labels,
        values,
        y_label="",
        marker="o",
        color=None
    ):
        self.clear()

        if not labels or not values:
            self.show_empty_state()
            return

        line_color = color or AppTheme.PRIMARY
        self.axes.plot(
            labels,
            values,
            color=line_color,
            marker=marker,
            linewidth=2,
            markersize=5
        )

        if y_label:
            self.axes.set_ylabel(
                y_label,
                color=AppTheme.TEXT_SECONDARY,
                fontsize=9
            )

        self._finish_draw()

    def draw_pie_chart(
        self,
        labels,
        values,
        colors=None,
        autopct="%1.1f%%"
    ):
        self.axes.clear()
        self.axes.set_facecolor(AppTheme.CARD_BACKGROUND)

        if not labels or not values or sum(values) <= 0:
            self.show_empty_state()
            return

        pie_colors = colors or [
            AppTheme.PRIMARY,
            AppTheme.SUCCESS,
            AppTheme.WARNING,
            AppTheme.ERROR,
            AppTheme.TEXT_MUTED,
        ]

        wedges, texts, autotexts = self.axes.pie(
            values,
            labels=labels,
            colors=pie_colors[:len(values)],
            autopct=autopct,
            startangle=90,
            wedgeprops={
                "linewidth": 1,
                "edgecolor": AppTheme.CARD_BACKGROUND,
            }
        )

        for text in texts:
            text.set_color(AppTheme.TEXT_PRIMARY)
            text.set_fontsize(9)

        for text in autotexts:
            text.set_color(AppTheme.TEXT_INVERSE)
            text.set_fontsize(8)
            text.set_fontweight("bold")

        self.axes.axis("equal")
        self._finish_draw()

    def show_empty_state(
        self,
        message="표시할 차트 데이터가 없습니다."
    ):
        self.axes.clear()
        self.axes.set_facecolor(AppTheme.CARD_BACKGROUND)
        self.axes.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            color=AppTheme.TEXT_SECONDARY,
            fontsize=10,
            transform=self.axes.transAxes
        )
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        for spine in self.axes.spines.values():
            spine.set_visible(False)

        self._finish_draw()

    def _add_bar_value_labels(
        self,
        bars,
        value_format
    ):
        for bar in bars:
            height = bar.get_height()
            self.axes.annotate(
                value_format.format(height),
                xy=(
                    bar.get_x() + bar.get_width() / 2,
                    height
                ),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=AppTheme.TEXT_PRIMARY,
                fontsize=8
            )

    def _add_horizontal_bar_value_labels(
        self,
        bars,
        value_format
    ):
        for bar in bars:
            width = bar.get_width()
            self.axes.annotate(
                value_format.format(width),
                xy=(
                    width,
                    bar.get_y() + bar.get_height() / 2
                ),
                xytext=(4, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                color=AppTheme.TEXT_PRIMARY,
                fontsize=8
            )

    def _finish_draw(self):
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def destroy(self):
        if self.figure is not None:
            self.figure.clear()

        super().destroy()
