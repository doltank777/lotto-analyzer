from src.analyzer.frequency_analyzer import FrequencyAnalyzer
from src.analyzer.trend_analyzer import TrendAnalyzer
from src.analyzer.pair_analyzer import PairAnalyzer
from src.analyzer.triple_analyzer import TripleAnalyzer
from src.analyzer.pattern_analyzer import PatternAnalyzer
from src.analyzer.missing_number_analyzer import MissingNumberAnalyzer


class AnalysisService:
    def __init__(self):
        self.frequency_analyzer = FrequencyAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.pair_analyzer = PairAnalyzer()
        self.triple_analyzer = TripleAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.missing_number_analyzer = MissingNumberAnalyzer()

    def get_analysis_summary(self):
        return {
            "most_common_numbers": self.frequency_analyzer.get_most_common_numbers(10),
            "least_common_numbers": self.frequency_analyzer.get_least_common_numbers(10),
            "hot_numbers": self.trend_analyzer.get_hot_numbers(30, 10),
            "cold_numbers": self.trend_analyzer.get_cold_numbers(30, 10),
            "rising_numbers": self.trend_analyzer.get_rising_numbers(10),
            "falling_numbers": self.trend_analyzer.get_falling_numbers(10),
            "top_pairs": self.pair_analyzer.get_top_pairs(20),
            "top_triples": self.triple_analyzer.get_top_triples(20),
            "missing_numbers": self.missing_number_analyzer.get_top_missing_numbers(10),
            "pattern_summary": self.pattern_analyzer.analyze_all_patterns()
        }