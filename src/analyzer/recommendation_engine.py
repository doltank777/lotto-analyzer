import random
from itertools import combinations

from src.analyzer.frequency_analyzer import FrequencyAnalyzer
from src.analyzer.trend_analyzer import TrendAnalyzer
from src.analyzer.pair_analyzer import PairAnalyzer
from src.analyzer.triple_analyzer import TripleAnalyzer
from src.analyzer.pattern_analyzer import PatternAnalyzer
from src.analyzer.missing_number_analyzer import MissingNumberAnalyzer
from src.config.recommendation_settings_manager import (
    RecommendationSettingsManager,
)


class RecommendationEngine:
    def __init__(self, max_draw_no=None, settings_manager=None):
        self.max_draw_no = max_draw_no
        self.settings_manager = (
            settings_manager
            if settings_manager is not None
            else RecommendationSettingsManager()
        )

        self.frequency_analyzer = FrequencyAnalyzer(max_draw_no=max_draw_no)
        self.trend_analyzer = TrendAnalyzer(max_draw_no=max_draw_no)
        self.pair_analyzer = PairAnalyzer(max_draw_no=max_draw_no)
        self.triple_analyzer = TripleAnalyzer(max_draw_no=max_draw_no)
        self.pattern_analyzer = PatternAnalyzer(max_draw_no=max_draw_no)
        self.missing_number_analyzer = MissingNumberAnalyzer(
            max_draw_no=max_draw_no
        )

    def calculate_number_scores(self):
        settings = self.settings_manager.get_settings()
        weights = settings["weights"]

        frequency_scores = self._get_frequency_scores()
        recent_30_scores = self._get_recent_scores(30)
        recent_100_scores = self._get_recent_scores(100)
        rising_scores = self._get_rising_scores()
        missing_scores = self._get_missing_scores()

        result = []

        for number in range(1, 46):
            total_score = (
                frequency_scores.get(number, 0) * weights["frequency"]
                + recent_30_scores.get(number, 0) * weights["recent_30"]
                + recent_100_scores.get(number, 0) * weights["recent_100"]
                + rising_scores.get(number, 0) * weights["rising"]
                + missing_scores.get(number, 0) * weights["missing"]
            )

            result.append({
                "number": number,
                "total_score": round(total_score, 4),
                "frequency_score": frequency_scores.get(number, 0),
                "recent_30_score": recent_30_scores.get(number, 0),
                "recent_100_score": recent_100_scores.get(number, 0),
                "rising_score": rising_scores.get(number, 0),
                "missing_score": missing_scores.get(number, 0)
            })

        return sorted(
            result,
            key=lambda item: item["total_score"],
            reverse=True,
        )

    def generate_final_recommendations(self):
        settings = self.settings_manager.get_settings()["final_settings"]

        return self.generate_recommendations(
            set_count=settings["set_count"],
            candidate_pool_size=settings["candidate_pool_size"],
            max_attempts=settings["max_attempts"],
            max_overlap_count=settings["max_overlap_count"],
        )

    def generate_recommendations(
        self,
        set_count=10,
        candidate_pool_size=30,
        max_attempts=5000,
        max_overlap_count=None
    ):
        number_scores = self.calculate_number_scores()
        candidate_numbers = [
            item["number"]
            for item in number_scores[:candidate_pool_size]
        ]

        recommendations = []
        used_sets = set()
        attempts = 0

        while len(recommendations) < set_count and attempts < max_attempts:
            attempts += 1

            numbers = sorted(random.sample(candidate_numbers, 6))
            numbers_key = tuple(numbers)

            if numbers_key in used_sets:
                continue

            if not self.is_valid_recommendation(numbers):
                continue

            if max_overlap_count is not None:
                if self.has_too_much_overlap(
                    numbers,
                    recommendations,
                    max_overlap_count,
                ):
                    continue

            score_result = self.calculate_combination_score(numbers)

            recommendations.append(score_result)
            used_sets.add(numbers_key)

        return sorted(
            recommendations,
            key=lambda item: item["total_score"],
            reverse=True,
        )

    def has_too_much_overlap(
        self,
        numbers,
        recommendations,
        max_overlap_count,
    ):
        current_set = set(numbers)

        for item in recommendations:
            existing_set = set(item["numbers"])
            overlap_count = len(current_set & existing_set)

            if overlap_count > max_overlap_count:
                return True

        return False

    def is_valid_recommendation(self, numbers):
        conditions = self.settings_manager.get_settings()["conditions"]
        pattern = self.pattern_analyzer.analyze_single_draw_pattern(numbers)

        odd_even_pattern = pattern["odd_even"]["pattern"]
        low_high_pattern = pattern["low_high"]["pattern"]
        total_sum = pattern["sum"]["sum"]
        unique_digit_count = pattern["last_digit"]["unique_digit_count"]
        consecutive_pair_count = pattern["consecutive"]["pair_count"]

        if (
            odd_even_pattern
            not in conditions["allowed_odd_even_patterns"]
        ):
            return False

        if (
            low_high_pattern
            not in conditions["allowed_low_high_patterns"]
        ):
            return False

        if not conditions["min_sum"] <= total_sum <= conditions["max_sum"]:
            return False

        if unique_digit_count < conditions["min_unique_digit_count"]:
            return False

        if (
            consecutive_pair_count
            > conditions["max_consecutive_pair_count"]
        ):
            return False

        return True

    def calculate_combination_score(self, numbers):
        numbers = sorted(numbers)

        number_score_map = {
            item["number"]: item["total_score"]
            for item in self.calculate_number_scores()
        }

        base_score = sum(
            number_score_map.get(number, 0)
            for number in numbers
        )
        pair_score = self._calculate_pair_score(numbers)
        triple_score = self._calculate_triple_score(numbers)
        pattern_score = self._calculate_pattern_score(numbers)

        total_score = (
            base_score
            + pair_score
            + triple_score
            + pattern_score
        )

        return {
            "numbers": numbers,
            "total_score": round(total_score, 4),
            "base_score": round(base_score, 4),
            "pair_score": round(pair_score, 4),
            "triple_score": round(triple_score, 4),
            "pattern_score": round(pattern_score, 4),
            "pattern": self.pattern_analyzer.analyze_single_draw_pattern(
                numbers
            )
        }

    def _get_frequency_scores(self):
        frequencies = self.frequency_analyzer.get_number_frequency()

        if not frequencies:
            return {number: 0 for number in range(1, 46)}

        max_count = max(item["count"] for item in frequencies)

        if max_count == 0:
            return {number: 0 for number in range(1, 46)}

        return {
            item["number"]: round(item["count"] / max_count, 4)
            for item in frequencies
        }

    def _get_recent_scores(self, recent_count):
        hot_numbers = self.trend_analyzer.get_hot_numbers(
            recent_count,
            45,
        )

        if not hot_numbers:
            return {number: 0 for number in range(1, 46)}

        max_count = max(item["count"] for item in hot_numbers)

        if max_count == 0:
            return {number: 0 for number in range(1, 46)}

        return {
            item["number"]: round(item["count"] / max_count, 4)
            for item in hot_numbers
        }

    def _get_rising_scores(self):
        rising_numbers = self.trend_analyzer.get_rising_numbers(45)

        if not rising_numbers:
            return {number: 0 for number in range(1, 46)}

        max_diff = max(item["diff"] for item in rising_numbers)

        if max_diff <= 0:
            return {number: 0 for number in range(1, 46)}

        scores = {}

        for item in rising_numbers:
            diff = item["diff"]
            scores[item["number"]] = round(
                max(diff, 0) / max_diff,
                4,
            )

        return scores

    def _get_missing_scores(self):
        missing_numbers = (
            self.missing_number_analyzer.analyze_missing_numbers()
        )

        if not missing_numbers:
            return {number: 0 for number in range(1, 46)}

        max_missing = max(
            item["missing_draws"]
            for item in missing_numbers
        )

        if max_missing == 0:
            return {number: 0 for number in range(1, 46)}

        return {
            item["number"]: round(
                item["missing_draws"] / max_missing,
                4,
            )
            for item in missing_numbers
        }

    def _calculate_pair_score(self, numbers):
        pair_weight = self.settings_manager.get_settings()[
            "combination_weights"
        ]["pair"]
        pair_data = self.pair_analyzer.analyze_pair_frequency()
        pair_score_map = {
            item["pair"]: item["count"]
            for item in pair_data
        }

        score = 0

        for pair in combinations(numbers, 2):
            score += pair_score_map.get(tuple(sorted(pair)), 0)

        return score * pair_weight

    def _calculate_triple_score(self, numbers):
        triple_weight = self.settings_manager.get_settings()[
            "combination_weights"
        ]["triple"]
        triple_data = self.triple_analyzer.analyze_triple_frequency()
        triple_score_map = {
            item["triple"]: item["count"]
            for item in triple_data
        }

        score = 0

        for triple in combinations(numbers, 3):
            score += triple_score_map.get(tuple(sorted(triple)), 0)

        return score * triple_weight

    def _calculate_pattern_score(self, numbers):
        pattern_weight = self.settings_manager.get_settings()[
            "combination_weights"
        ]["pattern"]
        conditions = self.settings_manager.get_settings()["conditions"]
        pattern = self.pattern_analyzer.analyze_single_draw_pattern(numbers)

        score = 0

        odd_even = pattern["odd_even"]["pattern"]
        low_high = pattern["low_high"]["pattern"]
        total_sum = pattern["sum"]["sum"]
        unique_digit_count = pattern["last_digit"]["unique_digit_count"]
        consecutive_pair_count = pattern["consecutive"]["pair_count"]

        if odd_even in conditions["allowed_odd_even_patterns"]:
            score += 1

        if low_high in conditions["allowed_low_high_patterns"]:
            score += 1

        if conditions["min_sum"] <= total_sum <= conditions["max_sum"]:
            score += 1

        if unique_digit_count >= conditions["min_unique_digit_count"]:
            score += 1

        if (
            consecutive_pair_count
            <= conditions["max_consecutive_pair_count"]
        ):
            score += 1

        return score * pattern_weight
