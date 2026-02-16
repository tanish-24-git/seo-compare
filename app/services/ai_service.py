import json
from groq import AsyncGroq

from core.config import settings
from typing import Dict, Any, List

class AIService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        self.model = "llama-3.3-70b-versatile"


    async def analyze_seo_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extracts SEO signals from HTML content using Groq AI.
        """
        if not self.client:
            return {}

        prompt = f"""
        Analyze the following HTML content for SEO signals and return a JSON object.
        URL: {url}
        
        Focus on:
        1. Content Quality (readability, keyword density, depth)
        2. EEAT Signals (author bio, expert quotes, citations)
        3. YMYL Trust (disclaimers, registrations, contact info)
        4. India Specific Context (references to Indian laws, currency, local contact)
        5. Brand/UX (visual clarity, primary CTA)

        HTML Snapshot (truncated):
        {html_content[:15000]}
        
        Return ONLY valid JSON in this format:
        {{
            "content_quality": {{
                "readability_score": float,
                "keyword_optimization": float,
                "depth_analysis": "string"
            }},
            "eeat": {{
                "author_identified": bool,
                "expert_citations": bool,
                "transparency_score": float
            }},
            "ymyl": {{
                "trust_indicators": ["list"],
                "disclaimer_present": bool,
                "license_info": "string"
            }},
            "india_specific": {{
                "localized_content": bool,
                "indian_legal_compliance": bool
            }},
            "brand_ux": {{
                "primary_cta_clarity": float,
                "professional_design_score": float
            }}
        }}
        """

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SEO auditor specializing in enterprise and YMYL (Your Money Your Life) websites. You always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Error calling Groq API for extraction: {e}")
            return {}

    async def compare_seo_data(self, baseline_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> str:
        """
        Generates a comparative analysis summary between baseline and competitor using AI.
        """
        if not self.client:
            return "AI Analysis not available (Missing API Key)."

        prompt = f"""
        Compare the following SEO data of a baseline website (Bajaj Life) and a competitor.
        
        Baseline Data (Bajaj Life):
        {json.dumps(baseline_data, indent=2, default=str)}
        
        Competitor Data:
        {json.dumps(competitor_data, indent=2, default=str)}

        
        Provide a deep, enterprise-grade SEO gap analysis report in Markdown format.
        
        Structure your response exactly as follows:
        
        ### 🏆 Executive Summary
        [Provide a high-level verdict. Who is winning? What is the score difference? 2-3 sentences.]
        
        ### 📊 Critical Parameter Analysis
        *   **Content Depth**: Compare word count average and thin content ratio.
        *   **YMYL Signals**: Specifically analyze Trust and IRDAI compliance.
        *   **Authority Gap**: Compare Domain Authority and Backlink profile strength.
        
        ### ⚡ Technical Performance Drift
        *   **Load Time**: Detailed comparison of page load times (in seconds).
        *   **Core Web Vitals**: Compare LCP and CLS scores if available.
        *   **Mobile Experience**: Is there a significant gap in mobile optimization?

        ### 🔍 Keyword & Intent Gaps
        Based on the content analysis, identify what *kinds* of keywords the competitor might be targeting that Bajaj is missing (e.g., "Term Plan for NRI", "Tax Saving 80C"). Infer this from the 'intent' and 'content' sections.

        ### ✅ Actionable Recommendations
        1. [Specific action 1]
        2. [Specific action 2]
        3. [Specific action 3]
        
        Make the tone professional, data-driven, and extremely specific. Do not use generic advice. Use the provided JSON data for every claim.
        
        """

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior SEO consultant providing a competitive gap analysis for an insurance enterprise."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API for comparison: {e}")
            return "Error generating AI comparison."

