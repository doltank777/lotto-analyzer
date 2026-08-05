class AppTheme:
    """Lotto Analyzer 모던 라이트 UI 디자인 시스템."""

    APP_NAME = "Lotto Analyzer"
    VERSION = "1.1.0"

    WINDOW_WIDTH = 1180
    WINDOW_HEIGHT = 800
    SIDEBAR_WIDTH = 210

    # Core colors
    APP_BACKGROUND = "#F3F6FA"
    SIDEBAR_BACKGROUND = "#172033"
    SIDEBAR_HOVER = "#222E45"
    SIDEBAR_ACTIVE = "#2D6CDF"
    HEADER_BACKGROUND = "#FFFFFF"
    CONTENT_BACKGROUND = "#F3F6FA"
    CARD_BACKGROUND = "#FFFFFF"
    INPUT_BACKGROUND = "#F8FAFC"

    PRIMARY = "#2D6CDF"
    PRIMARY_HOVER = "#245FC8"
    PRIMARY_PRESSED = "#1E52B1"
    SUCCESS = "#1F9D68"
    WARNING = "#D99019"
    ERROR = "#D94A4A"

    TEXT_PRIMARY = "#182033"
    TEXT_SECONDARY = "#667085"
    TEXT_MUTED = "#98A2B3"
    TEXT_INVERSE = "#FFFFFF"
    BORDER = "#E4E9F0"
    DIVIDER = "#EDF0F4"

    FONT_FAMILY = "맑은 고딕"
    MONO_FONT_FAMILY = "Consolas"

    FONT_APP_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_PAGE_TITLE = (FONT_FAMILY, 20, "bold")
    FONT_CARD_TITLE = (FONT_FAMILY, 12, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9)
    FONT_MENU = (FONT_FAMILY, 10, "bold")
    FONT_BUTTON = (FONT_FAMILY, 10, "bold")
    FONT_MONO = (MONO_FONT_FAMILY, 10)

    WINDOW_PADDING = 22
    CARD_PADDING = 18
    PAGE_GAP = 14

    @classmethod
    def text_widget_options(cls):
        return {
            "font": cls.FONT_MONO,
            "bg": cls.INPUT_BACKGROUND,
            "fg": cls.TEXT_PRIMARY,
            "insertbackground": cls.TEXT_PRIMARY,
            "selectbackground": cls.PRIMARY,
            "selectforeground": cls.TEXT_INVERSE,
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 1,
            "highlightbackground": cls.BORDER,
            "highlightcolor": cls.PRIMARY,
            "padx": 14,
            "pady": 12,
        }