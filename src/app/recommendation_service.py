from src.analyzer.recommendation_engine import RecommendationEngine
from src.config.recommendation_settings_manager import (
    RecommendationSettingsManager,
)


class RecommendationService:
    def __init__(self):
        self.settings_manager = RecommendationSettingsManager()
        self.recommendation_engine = RecommendationEngine(
            settings_manager=self.settings_manager
        )

    def get_final_recommendations(self):
        recommendations = (
            self.recommendation_engine.generate_final_recommendations()
        )

        return [
            {
                "index": index,
                "numbers": item["numbers"],
                "total_score": item["total_score"],
                "base_score": item["base_score"],
                "pair_score": item["pair_score"],
                "triple_score": item["triple_score"],
                "pattern_score": item["pattern_score"],
                "pattern": item["pattern"]
            }
            for index, item in enumerate(recommendations, start=1)
        ]

    def get_recommendation_settings(self):
        return self.settings_manager.get_settings()

    def save_recommendation_settings(self, settings):
        return self.settings_manager.save_settings(settings)

    def restore_default_recommendation_settings(self):
        return self.settings_manager.restore_defaults()
