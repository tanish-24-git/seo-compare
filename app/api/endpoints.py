from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Dict, Any
import os
import json
import re
from core.config import settings
from services.extractor_service import ExtractorService
from services.comparator_service import ComparatorService
from models.seo import FullSEOResult, ComparisonResult

router = APIRouter()
extractor_service = ExtractorService()
comparator_service = ComparatorService()

@router.get("/baseline")
async def get_baseline():
    """
    Returns the stored baseline SEO data for Bajaj Life.
    """
    try:
        baseline = extractor_service.get_baseline_data()
        return baseline.model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/extract/baseline")
async def extract_baseline(url: str = "https://www.bajajlifeinsurance.com/"):
    """
    Directly extracts baseline SEO data for Bajaj Life.
    """
    try:
        from services.crawler_service import CrawlerService
        crawler = CrawlerService()
        pages = await crawler.crawl(url)
        data = await extractor_service.extract_full_site_data(url, pages)
        save_path = await extractor_service.save_baseline(data)
        return {"status": "success", "message": "Baseline extraction completed.", "path": save_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

@router.post("/extract/competitor")
async def extract_competitor(url: str):
    """
    Directly extracts competitor SEO data.
    """
    try:
        from services.crawler_service import CrawlerService
        crawler = CrawlerService()
        pages = await crawler.crawl(url)
        data = await extractor_service.extract_full_site_data(url, pages)
        save_path = await extractor_service.save_competitor(data)
        return {"status": "success", "message": f"Extraction for {url} completed.", "path": save_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")


@router.get("/compare")
async def compare_sites(competitor_url: str = Query(...)):
    """
    Compares Bajaj Life (baseline) with a competitor.
    Returns detailed audit breakdown and scores for visualization.
    """
    try:
        baseline = extractor_service.get_baseline_data()
        
        # Check if competitor data exists
        domain = re.sub(r'\W+', '_', competitor_url.replace("https://", "").replace("http://", "").rstrip("/"))
        comp_path = os.path.join(settings.COMPETITOR_DIR, f"{domain}_seo.json")
        
        if os.path.exists(comp_path):
            with open(comp_path, "r") as f:
                competitor = FullSEOResult.model_validate_json(f.read())
        else:
            # Extract on the fly
            from services.crawler_service import CrawlerService
            crawler = CrawlerService()
            pages = await crawler.crawl(competitor_url)
            competitor = await extractor_service.extract_full_site_data(competitor_url, pages)
            await extractor_service.save_competitor(competitor)

        # Build detailed comparison
        b = baseline.model_dump(mode='json')
        c = competitor.model_dump(mode='json')

        
        # Categorical scores for Radar Chart
        def get_cat_scores(data):
            def safe_get(d, keys, default=0):
                for k in keys:
                    d = d.get(k, {}) if isinstance(d, dict) else {}
                return d if isinstance(d, (int, float, bool)) else default

            # Strict scoring: normalized to 0-100 with None safety
            plt = safe_get(data, ["technical", "page_load_time"], 3.0)
            rds = safe_get(data, ["content", "readability_score"], 0.7)
            mss = safe_get(data, ["mobile", "mobile_speed_score"], 70)
            da = safe_get(data, ["domain_authority", "domain_authority"], 50)
            
            tech_score = max(0, 100 - (float(plt) * 20))
            content_score = float(rds) * 100
            
            # Trust score calculation with safe boolean checks
            is_irdai = safe_get(data, ["ymyl", "irdai_registration"], False)
            is_claim = safe_get(data, ["ymyl", "claim_settlement_ratio"], False)
            trust_score = 100 if is_irdai and is_claim else 60
            
            mobile_score = float(mss)
            auth_score = float(da)
            
            return {
                "Technical": round(tech_score, 1),
                "Content": round(content_score, 1),
                "Trust (YMYL)": round(float(trust_score), 1),
                "Mobile": round(mobile_score, 1),
                "Authority": round(auth_score, 1)
            }

        categories = get_cat_scores(b)
        comp_categories = get_cat_scores(c)

        # Detailed parameters for table with strict logic
        details = []
        params_to_compare = [
            # 1. Domain
            ("Domain Authority", float(b["domain_authority"].get("domain_authority") or 0), float(c["domain_authority"].get("domain_authority") or 0), "/100"),
            ("Backlinks", int(b["domain_authority"].get("total_backlinks") or 0), int(c["domain_authority"].get("total_backlinks") or 0), ""),
            ("Referring Domains", int(b["domain_authority"].get("referring_domains") or 0), int(c["domain_authority"].get("referring_domains") or 0), ""),
            ("Organic Keywords", int(b["domain_authority"].get("organic_keywords") or 0), int(c["domain_authority"].get("organic_keywords") or 0), ""),
            ("HTTPS Secured", bool(b["domain_authority"].get("https_status")), bool(c["domain_authority"].get("https_status")), "bool"),

            # 2. Crawlability
            ("Robots.txt", bool(b["crawlability"].get("robots_txt_exists")), bool(c["crawlability"].get("robots_txt_exists")), "bool"),
            ("XML Sitemap", bool(b["crawlability"].get("xml_sitemap_exists")), bool(c["crawlability"].get("xml_sitemap_exists")), "bool"),
            ("Orphan Pages", int(b["crawlability"].get("orphan_pages") or 0), int(c["crawlability"].get("orphan_pages") or 0), ""),
            ("Crawl Depth", int(b["crawlability"].get("crawl_depth") or 0), int(c["crawlability"].get("crawl_depth") or 0), ""),
            
            # 3. Content 
            ("Avg Word Count", int(b["content"].get("avg_word_count") or 0), int(c["content"].get("avg_word_count") or 0), " words"),
            ("Thin Content Ratio", float(b["content"].get("thin_content_ratio") or 0), float(c["content"].get("thin_content_ratio") or 0), "%"),
            ("Readability Score", float(b["content"].get("readability_score") or 0), float(c["content"].get("readability_score") or 0), "/1.0"),
            ("FAQ Presence", bool(b["content"].get("faq_presence")), bool(c["content"].get("faq_presence")), "bool"),

            # 4. YMYL & Trust (Critical)
            ("IRDAI Reg. Display", bool(b["ymyl"].get("irdai_registration")), bool(c["ymyl"].get("irdai_registration")), "bool"),
            ("Claim Settlement Ratio", bool(b["ymyl"].get("claim_settlement_ratio")), bool(c["ymyl"].get("claim_settlement_ratio")), "bool"),
            ("Risk Disclaimer", bool(b["ymyl"].get("risk_disclaimer")), bool(c["ymyl"].get("risk_disclaimer")), "bool"),
            ("Privacy Policy", bool(b["ymyl"].get("privacy_policy_quality")), bool(c["ymyl"].get("privacy_policy_quality")), "bool"),
            ("Contact/Grievance", bool(b["ymyl"].get("contact_grievance_info")), bool(c["ymyl"].get("contact_grievance_info")), "bool"),

            # 5. Technical
            ("Page Load Time", float(b["technical"].get("page_load_time") or 0), float(c["technical"].get("page_load_time") or 0), "s"),
            ("TTFB", float(b["technical"].get("ttfb") or 0), float(c["technical"].get("ttfb") or 0), "ms"),
            ("LCP Score", float(b["technical"].get("lcp_score") or 0), float(c["technical"].get("lcp_score") or 0), "s"),
            ("CLS Score", float(b["technical"].get("cls_score") or 0), float(c["technical"].get("cls_score") or 0), ""),
            ("JS Bundle Size", float(b["technical"].get("js_bundle_weight") or 0), float(c["technical"].get("js_bundle_weight") or 0), "KB"),
            
            # 6. Mobile
            ("Mobile Responsiveness", bool(b["mobile"].get("mobile_responsive")), bool(c["mobile"].get("mobile_responsive")), "bool"),
            ("Mobile Speed Score", float(b["mobile"].get("mobile_speed_score") or 0), float(c["mobile"].get("mobile_speed_score") or 0), "/100"),
            ("Tap Target Spacing", bool(b["mobile"].get("tap_element_spacing")), bool(c["mobile"].get("tap_element_spacing")), "bool"),

            # 7. India Specific
            ("INR Currency Use", bool(b["india_specific"].get("inr_currency_use")), bool(c["india_specific"].get("inr_currency_use")), "bool"),
            ("Tax Keywords (80C)", bool(b["india_specific"].get("india_tax_keywords")), bool(c["india_specific"].get("india_tax_keywords")), "bool"),
            ("Hreflang en-IN", bool(b["india_specific"].get("hreflang_en_in")), bool(c["india_specific"].get("hreflang_en_in")), "bool"),
            
            # 8. Schema
            ("Organization Schema", bool(b["schema_data"].get("organization_schema")), bool(c["schema_data"].get("organization_schema")), "bool"),
            ("Product/Plan Schema", bool(b["schema_data"].get("product_schema")), bool(c["schema_data"].get("product_schema")), "bool"),
            ("FAQ Schema", bool(b["schema_data"].get("faq_schema")), bool(c["schema_data"].get("faq_schema")), "bool"),

            # 9. Meta Signals
            ("Title Tag Optimized", bool(b["meta_html"].get("title_length_optimized")), bool(c["meta_html"].get("title_length_optimized")), "bool"),
            ("Meta Desc Presence", bool(b["meta_html"].get("meta_desc_presence")), bool(c["meta_html"].get("meta_desc_presence")), "bool"),
            ("H1 Hierarchy Valid", bool(b["meta_html"].get("heading_hierarchy_valid")), bool(c["meta_html"].get("heading_hierarchy_valid")), "bool"),
            ("Img Alt Coverage", float(b["meta_html"].get("image_alt_coverage") or 0), float(c["meta_html"].get("image_alt_coverage") or 0), "%"),
        ]

        
        gaps_count = 0
        for label, bv, cv, unit in params_to_compare:
            status = "Optimized"
            if isinstance(bv, (int, float)) and isinstance(cv, (int, float)):
                if label == "Page Load Time" or label == "Thin Content Ratio":
                    if bv > cv: 
                        status = "Warning"
                        gaps_count += 1
                else:
                    if bv < cv: 
                        status = "Warning"
                        gaps_count += 1
            elif isinstance(bv, bool) and isinstance(cv, bool):
                if not bv and cv: 
                    status = "Warning"
                    gaps_count += 1
            
            details.append({
                "label": label,
                "baseline": f"{bv}{unit}" if unit != "bool" else ("Yes" if bv else "No"),
                "competitor": f"{cv}{unit}" if unit != "bool" else ("Yes" if cv else "No"),
                "status": status
            })

        from services.ai_service import AIService
        ai_summary = await AIService().compare_seo_data(b, c)

        return {
            "overall_score": f"{int(baseline.overall_score)}/100",
            "competitor_score": f"{int(competitor.overall_score)}/100",
            "gaps": str(gaps_count),
            "techDebt": "High" if (baseline.technical.page_load_time or 0.0) > 3.0 or gaps_count > 3 else "Low",
            "categories": categories,
            "comp_categories": comp_categories,
            "details": details,
            "baseline_url": baseline.url,
            "competitor_url": competitor.url,
            "ai_analysis": ai_summary
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")



@router.get("/results/{competitor_domain}")
async def get_comparison_report(competitor_domain: str):
    """
    Returns the JSON report for a specific comparison.
    """
    try:
        baseline = extractor_service.get_baseline_data()
        return baseline.model_dump()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Baseline not found.")


@router.get("/compare/stream")
async def compare_sites_stream(competitor_url: str = Query(...)):
    """
    Streams the comparison process, yielding events for each step.
    """
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting analysis...'})}\n\n"
            
            baseline = extractor_service.get_baseline_data()
            
            # Extract on the fly
            from services.crawler_service import CrawlerService
            crawler = CrawlerService()
            
            pages = []
            yield f"data: {json.dumps({'type': 'status', 'message': f'Crawling {competitor_url}...'})}\n\n"
            
            async for page in crawler.crawl_stream(competitor_url):
                pages.append(page)
                yield f"data: {json.dumps({'type': 'log', 'url': page['url'], 'status': page['status'], 'depth': page.get('depth', 0)})}\n\n"
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Analyzing content (100+ parameters)...'})}\n\n"
            competitor = await extractor_service.extract_full_site_data(competitor_url, pages)
            await extractor_service.save_competitor(competitor)

            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating comparison report...'})}\n\n"
            
            # Build detailed comparison
            b = baseline.model_dump(mode='json')
            c = competitor.model_dump(mode='json')

            # Categorical scores (Same logic as compare_sites)
            def get_cat_scores(data):
                def safe_get(d, keys, default=0):
                    for k in keys:
                        d = d.get(k, {}) if isinstance(d, dict) else {}
                    return d if isinstance(d, (int, float, bool)) else default

                plt = safe_get(data, ["technical", "page_load_time"], 3.0)
                rds = safe_get(data, ["content", "readability_score"], 0.7)
                mss = safe_get(data, ["mobile", "mobile_speed_score"], 70)
                da = safe_get(data, ["domain_authority", "domain_authority"], 50)
                
                tech_score = max(0, 100 - (float(plt) * 20))
                content_score = float(rds) * 100
                
                is_irdai = safe_get(data, ["ymyl", "irdai_registration"], False)
                is_claim = safe_get(data, ["ymyl", "claim_settlement_ratio"], False)
                trust_score = 100 if is_irdai and is_claim else 60
                
                mobile_score = float(mss)
                auth_score = float(da)
                
                return {
                    "Technical": round(tech_score, 1),
                    "Content": round(content_score, 1),
                    "Trust (YMYL)": round(float(trust_score), 1),
                    "Mobile": round(mobile_score, 1),
                    "Authority": round(auth_score, 1)
                }

            categories = get_cat_scores(b)
            comp_categories = get_cat_scores(c)

            # Detailed parameters for table with strict logic
            details = []
            params_to_compare = [
                ("Domain Authority", float(b["domain_authority"].get("domain_authority") or 0), float(c["domain_authority"].get("domain_authority") or 0), "/100"),
                ("Backlinks", int(b["domain_authority"].get("total_backlinks") or 0), int(c["domain_authority"].get("total_backlinks") or 0), ""),
                ("Referring Domains", int(b["domain_authority"].get("referring_domains") or 0), int(c["domain_authority"].get("referring_domains") or 0), ""),
                ("Organic Keywords", int(b["domain_authority"].get("organic_keywords") or 0), int(c["domain_authority"].get("organic_keywords") or 0), ""),
                ("HTTPS Secured", bool(b["domain_authority"].get("https_status")), bool(c["domain_authority"].get("https_status")), "bool"),

                ("Robots.txt", bool(b["crawlability"].get("robots_txt_exists")), bool(c["crawlability"].get("robots_txt_exists")), "bool"),
                ("XML Sitemap", bool(b["crawlability"].get("xml_sitemap_exists")), bool(c["crawlability"].get("xml_sitemap_exists")), "bool"),
                ("Orphan Pages", int(b["crawlability"].get("orphan_pages") or 0), int(c["crawlability"].get("orphan_pages") or 0), ""),
                ("Crawl Depth", int(b["crawlability"].get("crawl_depth") or 0), int(c["crawlability"].get("crawl_depth") or 0), ""),
                
                ("Avg Word Count", int(b["content"].get("avg_word_count") or 0), int(c["content"].get("avg_word_count") or 0), " words"),
                ("Thin Content Ratio", float(b["content"].get("thin_content_ratio") or 0), float(c["content"].get("thin_content_ratio") or 0), "%"),
                ("Readability Score", float(b["content"].get("readability_score") or 0), float(c["content"].get("readability_score") or 0), "/1.0"),
                ("FAQ Presence", bool(b["content"].get("faq_presence")), bool(c["content"].get("faq_presence")), "bool"),

                ("IRDAI Reg. Display", bool(b["ymyl"].get("irdai_registration")), bool(c["ymyl"].get("irdai_registration")), "bool"),
                ("Claim Settlement Ratio", bool(b["ymyl"].get("claim_settlement_ratio")), bool(c["ymyl"].get("claim_settlement_ratio")), "bool"),
                ("Risk Disclaimer", bool(b["ymyl"].get("risk_disclaimer")), bool(c["ymyl"].get("risk_disclaimer")), "bool"),
                ("Privacy Policy", bool(b["ymyl"].get("privacy_policy_quality")), bool(c["ymyl"].get("privacy_policy_quality")), "bool"),
                ("Contact/Grievance", bool(b["ymyl"].get("contact_grievance_info")), bool(c["ymyl"].get("contact_grievance_info")), "bool"),

                ("Page Load Time", float(b["technical"].get("page_load_time") or 0), float(c["technical"].get("page_load_time") or 0), "s"),
                ("TTFB", float(b["technical"].get("ttfb") or 0), float(c["technical"].get("ttfb") or 0), "ms"),
                ("LCP Score", float(b["technical"].get("lcp_score") or 0), float(c["technical"].get("lcp_score") or 0), "s"),
                ("CLS Score", float(b["technical"].get("cls_score") or 0), float(c["technical"].get("cls_score") or 0), ""),
                ("JS Bundle Size", float(b["technical"].get("js_bundle_weight") or 0), float(c["technical"].get("js_bundle_weight") or 0), "KB"),
                
                ("Mobile Responsiveness", bool(b["mobile"].get("mobile_responsive")), bool(c["mobile"].get("mobile_responsive")), "bool"),
                ("Mobile Speed Score", float(b["mobile"].get("mobile_speed_score") or 0), float(c["mobile"].get("mobile_speed_score") or 0), "/100"),
                ("Tap Target Spacing", bool(b["mobile"].get("tap_element_spacing")), bool(c["mobile"].get("tap_element_spacing")), "bool"),

                ("INR Currency Use", bool(b["india_specific"].get("inr_currency_use")), bool(c["india_specific"].get("inr_currency_use")), "bool"),
                ("Tax Keywords (80C)", bool(b["india_specific"].get("india_tax_keywords")), bool(c["india_specific"].get("india_tax_keywords")), "bool"),
                ("Hreflang en-IN", bool(b["india_specific"].get("hreflang_en_in")), bool(c["india_specific"].get("hreflang_en_in")), "bool"),
                
                ("Organization Schema", bool(b["schema_data"].get("organization_schema")), bool(c["schema_data"].get("organization_schema")), "bool"),
                ("Product/Plan Schema", bool(b["schema_data"].get("product_schema")), bool(c["schema_data"].get("product_schema")), "bool"),
                ("FAQ Schema", bool(b["schema_data"].get("faq_schema")), bool(c["schema_data"].get("faq_schema")), "bool"),

                ("Title Tag Optimized", bool(b["meta_html"].get("title_length_optimized")), bool(c["meta_html"].get("title_length_optimized")), "bool"),
                ("Meta Desc Presence", bool(b["meta_html"].get("meta_desc_presence")), bool(c["meta_html"].get("meta_desc_presence")), "bool"),
                ("H1 Hierarchy Valid", bool(b["meta_html"].get("heading_hierarchy_valid")), bool(c["meta_html"].get("heading_hierarchy_valid")), "bool"),
                ("Img Alt Coverage", float(b["meta_html"].get("image_alt_coverage") or 0), float(c["meta_html"].get("image_alt_coverage") or 0), "%"),
            ]

            gaps_count = 0
            for label, bv, cv, unit in params_to_compare:
                status = "Optimized"
                if isinstance(bv, (int, float)) and isinstance(cv, (int, float)):
                    if label == "Page Load Time" or label == "Thin Content Ratio":
                        if bv > cv: 
                            status = "Warning"
                            gaps_count += 1
                    else:
                        if bv < cv: 
                            status = "Warning"
                            gaps_count += 1
                elif isinstance(bv, bool) and isinstance(cv, bool):
                    if not bv and cv: 
                        status = "Warning"
                        gaps_count += 1
                
                details.append({
                    "label": label,
                    "baseline": f"{bv}{unit}" if unit != "bool" else ("Yes" if bv else "No"),
                    "competitor": f"{cv}{unit}" if unit != "bool" else ("Yes" if cv else "No"),
                    "status": status
                })

            from services.ai_service import AIService
            ai_summary = await AIService().compare_seo_data(b, c)

            result = {
                "overall_score": f"{int(baseline.overall_score)}/100",
                "competitor_score": f"{int(competitor.overall_score)}/100",
                "gaps": str(gaps_count),
                "techDebt": "High" if (baseline.technical.page_load_time or 0.0) > 3.0 or gaps_count > 3 else "Low",
                "categories": categories,
                "comp_categories": comp_categories,
                "details": details,
                "baseline_url": baseline.url,
                "competitor_url": competitor.url,
                "ai_analysis": ai_summary
            }
            yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
