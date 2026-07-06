from src.analyzer.recommendation_engine import RecommendationEngine


class RecommendationService:
    def __init__(self):
        self.recommendation_engine = RecommendationEngine()

    def get_final_recommendations(self):
        recommendations = self.recommendation_engine.generate_final_recommendations()

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