from src.analyzer.backtest_engine import BacktestEngine


class BacktestService:

    def __init__(self):
        self.engine = BacktestEngine()

    def run_backtest(self, test_count=10):
        results = self.engine.run_recent_final_recommendation_backtests(
            test_count=test_count
        )

        summary = self.engine.summarize_backtest_results(results)

        return {
            "results": results,
            "summary": summary
        }