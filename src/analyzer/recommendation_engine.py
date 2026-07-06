import random
from itertools import combinations

from src.analyzer.frequency_analyzer import FrequencyAnalyzer
from src.analyzer.trend_analyzer import TrendAnalyzer
from src.analyzer.pair_analyzer import PairAnalyzer
from src.analyzer.triple_analyzer import TripleAnalyzer
from src.analyzer.pattern_analyzer import PatternAnalyzer
from src.analyzer.missing_number_analyzer import MissingNumberAnalyzer


class RecommendationEngine:
    def __init__(self):
        self.frequency_analyzer = FrequencyAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.pair_analyzer = PairAnalyzer()
        self.triple_analyzer = TripleAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.missing_number_analyzer = MissingNumberAnalyzer()

    def calculate_number_scores(self):
        frequency_scores = self._get_frequency_scores()
        recent_30_scores = self._get_recent_scores(30)
        recent_100_scores = self._get_recent_scores(100)
        rising_scores = self._get_rising_scores()
        missing_scores = self._get_missing_scores()

        result = []

        for number in range(1, 46):
            total_score = (
                frequency_scores.get(number, 0) * 0.25 +
                recent_30_scores.get(number, 0) * 0.20 +
                recent_100_scores.get(number, 0) * 0.20 +
                rising_scores.get(number, 0) * 0.15 +
                missing_scores.get(number, 0) * 0.20
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

        return sorted(result, key=lambda x: x["total_score"], reverse=True)

    def generate_recommendations(self, set_count=10, candidate_pool_size=30, max_attempts=5000):
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

            score_result = self.calculate_combination_score(numbers)

            recommendations.append(score_result)
            used_sets.add(numbers_key)

        return sorted(
            recommendations,
            key=lambda x: x["total_score"],
            reverse=True
        )

    def is_valid_recommendation(self, numbers):
        pattern = self.pattern_analyzer.analyze_single_draw_pattern(numbers)

        odd_even_pattern = pattern["odd_even"]["pattern"]
        low_high_pattern = pattern["low_high"]["pattern"]
        total_sum = pattern["sum"]["sum"]
        unique_digit_count = pattern["last_digit"]["unique_digit_count"]
        consecutive_pair_count = pattern["consecutive"]["pair_count"]

        if odd_even_pattern not in ["3:3", "4:2", "2:4"]:
            return False

        if low_high_pattern not in ["3:3", "4:2", "2:4"]:
            return False

        if not 100 <= total_sum <= 170:
            return False

        if unique_digit_count < 5:
            return False

        if consecutive_pair_count > 1:
            return False

        return True

    def calculate_combination_score(self, numbers):
        numbers = sorted(numbers)

        number_score_map = {
            item["number"]: item["total_score"]
            for item in self.calculate_number_scores()
        }

        base_score = sum(number_score_map.get(number, 0) for number in numbers)
        pair_score = self._calculate_pair_score(numbers)
        triple_score = self._calculate_triple_score(numbers)
        pattern_score = self._calculate_pattern_score(numbers)

        total_score = base_score + pair_score + triple_score + pattern_score

        return {
            "numbers": numbers,
            "total_score": round(total_score, 4),
            "base_score": round(base_score, 4),
            "pair_score": round(pair_score, 4),
            "triple_score": round(triple_score, 4),
            "pattern_score": round(pattern_score, 4),
            "pattern": self.pattern_analyzer.analyze_single_draw_pattern(numbers)
        }

    def _get_frequency_scores(self):
        frequencies = self.frequency_analyzer.get_number_frequency()
        max_count = max(item["count"] for item in frequencies)

        return {
            item["number"]: round(item["count"] / max_count, 4)
            for item in frequencies
        }

    def _get_recent_scores(self, recent_count):
        hot_numbers = self.trend_analyzer.get_hot_numbers(recent_count, 45)
        max_count = max(item["count"] for item in hot_numbers)

        if max_count == 0:
            return {number: 0 for number in range(1, 46)}

        return {
            item["number"]: round(item["count"] / max_count, 4)
            for item in hot_numbers
        }

    def _get_rising_scores(self):
        rising_numbers = self.trend_analyzer.get_rising_numbers(45)
        max_diff = max(item["diff"] for item in rising_numbers)

        if max_diff <= 0:
            return {number: 0 for number in range(1, 46)}

        scores = {}

        for item in rising_numbers:
            diff = item["diff"]
            scores[item["number"]] = round(max(diff, 0) / max_diff, 4)

        return scores

    def _get_missing_scores(self):
        missing_numbers = self.missing_number_analyzer.analyze_missing_numbers()
        max_missing = max(item["missing_draws"] for item in missing_numbers)

        if max_missing == 0:
            return {number: 0 for number in range(1, 46)}

        return {
            item["number"]: round(item["missing_draws"] / max_missing, 4)
            for item in missing_numbers
        }

    def _calculate_pair_score(self, numbers):
        pair_data = self.pair_analyzer.analyze_pair_frequency()
        pair_score_map = {
            item["pair"]: item["count"]
            for item in pair_data
        }

        score = 0

        for pair in combinations(numbers, 2):
            score += pair_score_map.get(tuple(sorted(pair)), 0)

        return score * 0.01

    def _calculate_triple_score(self, numbers):
        triple_data = self.triple_analyzer.analyze_triple_frequency()
        triple_score_map = {
            item["triple"]: item["count"]
            for item in triple_data
        }

        score = 0

        for triple in combinations(numbers, 3):
            score += triple_score_map.get(tuple(sorted(triple)), 0)

        return score * 0.005

    def _calculate_pattern_score(self, numbers):
        pattern = self.pattern_analyzer.analyze_single_draw_pattern(numbers)

        score = 0

        odd_even = pattern["odd_even"]["pattern"]
        low_high = pattern["low_high"]["pattern"]
        total_sum = pattern["sum"]["sum"]
        unique_digit_count = pattern["last_digit"]["unique_digit_count"]
        consecutive_pair_count = pattern["consecutive"]["pair_count"]

        if odd_even in ["3:3", "4:2", "2:4"]:
            score += 1

        if low_high in ["3:3", "4:2", "2:4"]:
            score += 1

        if 100 <= total_sum <= 170:
            score += 1

        if unique_digit_count >= 5:
            score += 1

        if consecutive_pair_count <= 1:
            score += 1

        return score