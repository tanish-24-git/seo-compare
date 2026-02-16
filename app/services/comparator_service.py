from typing import Any, Dict
from models.seo import FullSEOResult, ComparisonResult
from services.ai_service import AIService


class ComparatorService:
    def __init__(self):
        self.ai_service = AIService()
        self.weights = {
            "content": 0.35,
            "technical": 0.25,
            "ymyl": 0.10,
            "eeat": 0.10,
            "mobile": 0.10,
            "performance": 0.10
        }

    async def compare(self, baseline: FullSEOResult, competitor: FullSEOResult) -> ComparisonResult:
        gaps = []
        scores = {}
        
        # Helper to compare parameters
        def check_gap(section: str, param: str, b_val: Any, c_val: Any):
            status = "equal"
            if isinstance(b_val, (int, float)) and isinstance(c_val, (int, float)):
                if c_val > b_val: status = "leading"
                elif c_val < b_val: status = "lagging"
            elif isinstance(b_val, bool) and isinstance(c_val, bool):
                if c_val and not b_val: status = "leading"
                elif b_val and not c_val: status = "lagging"
            
            return {
                "section": section,
                "parameter": param,
                "baseline_value": b_val,
                "competitor_value": c_val,
                "status": status
            }

        # Domain Authority Section
        gaps.append(check_gap("Domain Authority", "HTTPS", baseline.domain_authority.https_status, competitor.domain_authority.https_status))
        
        # Technical
        gaps.append(check_gap("Technical", "Load Time", baseline.technical.page_load_time, competitor.technical.page_load_time)) # Lower is better? Logic would need adjustment for time
        
        # YMYL
        gaps.append(check_gap("YMYL", "IRDAI Registration", baseline.ymyl.irdai_registration, competitor.ymyl.irdai_registration))
        
        # Calculate scores per section
        # (Simplified scoring for demonstration)
        sections = ["content", "technical", "ymyl", "eeat", "mobile"]
        for section in sections:
            # logic to aggregate gap statuses into a 0-100 score
            leading_count = len([g for g in gaps if g["status"] == "leading" and g["section"].lower().startswith(section[0:3])])
            total_count = len([g for g in gaps if g["section"].lower().startswith(section[0:3])]) or 1
            scores[section] = (leading_count / total_count) * 100

        overall_grade = sum([scores.get(s, 0) * self.weights.get(s, 0) for s in sections])

        # AI Comparison Summary
        ai_summary = await self.ai_service.compare_seo_data(
            baseline.model_dump(), 
            competitor.model_dump()
        )

        return ComparisonResult(
            baseline_url=baseline.url,
            competitor_url=competitor.url,
            gaps=gaps,
            scores=scores,
            overall_grade=overall_grade,
            summary=f"Competitor is {round(overall_grade, 2)}% relative to Bajaj Life baseline.",
            ai_analysis=ai_summary
        )
