from pydantic import BaseModel, Field, ConfigDict

from typing import Dict, List, Optional, Any
from datetime import datetime

class SEOParameter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    value: Any
    score: float = 0.0
    status: str = "unknown" # leading, lagging, equal
    details: Optional[str] = None

class DomainAuthority(BaseModel):
    model_config = ConfigDict(extra="ignore")
    domain_age: Optional[float] = None
    domain_authority: Optional[float] = None
    total_backlinks: Optional[int] = None
    referring_domains: Optional[int] = None
    organic_keywords: Optional[int] = None
    branded_keyword_presence: bool = False
    indexed_pages: Optional[int] = None
    domain_trust_signals: Optional[float] = None
    https_status: bool = False
    ssl_validity: bool = False

class CrawlabilityIndexing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    robots_txt_exists: bool = False
    xml_sitemap_exists: bool = False
    sitemap_validity: bool = False
    noindex_tags: bool = False
    canonical_tags_correct: bool = True
    orphan_pages: int = 0
    crawl_depth: int = 0
    duplicate_url_patterns: int = 0
    parameterized_urls: int = 0
    crawl_budget_waste: float = 0.0

class URLStructure(BaseModel):
    model_config = ConfigDict(extra="ignore")
    url_readability_score: float = 0.0
    keyword_in_url: bool = False
    url_length_consistency: bool = True
    folder_hierarchy_depth: int = 0
    trailing_slash_consistency: bool = True
    http_to_https_redirect: bool = False
    www_vs_non_www: bool = True
    static_vs_dynamic_ratio: float = 1.0

class MetaHTMLSignals(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title_presence: bool = False
    title_length_optimized: bool = False
    duplicate_titles: int = 0
    meta_desc_presence: bool = False
    meta_desc_length: bool = False
    h1_presence: bool = False
    multiple_h1_issues: bool = False
    heading_hierarchy_valid: bool = True
    image_alt_coverage: float = 0.0

class ContentQuality(BaseModel):
    model_config = ConfigDict(extra="ignore")
    avg_word_count: int = 0
    thin_content_ratio: float = 0.0
    duplicate_content_signals: float = 0.0
    readability_score: float = 0.0
    structured_content_usage: bool = False
    faq_presence: bool = False
    blog_volume: int = 0
    update_frequency: str = "unknown"

class SearchIntent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    informational_pages: int = 0
    transactional_pages: int = 0
    intent_alignment_score: float = 0.0
    topic_depth: float = 0.0
    featured_snippet_ready: bool = False

class YMYLTrust(BaseModel):
    model_config = ConfigDict(extra="ignore")
    irdai_registration: bool = False
    legal_details: bool = False
    claim_settlement_ratio: bool = False
    risk_disclaimer: bool = False
    privacy_policy_quality: bool = False
    terms_conditions: bool = False
    contact_grievance_info: bool = False
    physical_address: bool = False

class EEATSignals(BaseModel):
    model_config = ConfigDict(extra="ignore")
    author_presence: bool = False
    author_bio: bool = False
    expertise_indicators: bool = False
    about_us_depth: bool = False
    leadership_transparency: bool = False
    awards_certifications: bool = False

class TechnicalPerformance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lcp_score: Optional[float] = 0.0
    cls_score: Optional[float] = 0.0
    page_load_time: Optional[float] = 0.0
    ttfb: Optional[float] = 0.0
    js_bundle_weight: Optional[float] = 0.0
    css_blocking: Optional[int] = 0
    image_optimization: Optional[float] = 0.0
    lazy_loading: bool = False

class MobileUX(BaseModel):
    model_config = ConfigDict(extra="ignore")
    mobile_responsive: bool = False
    viewport_config: bool = False
    tap_element_spacing: bool = False
    mobile_speed_score: float = 0.0
    form_ux_complexity: str = "medium"
    calculator_usability: bool = False

class Linking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    internal_linking_density: float = 0.0
    anchor_text_diversity: float = 0.0
    orphan_money_pages: int = 0
    contextual_vs_footer_ratio: float = 0.0
    external_authority_links: int = 0

class SchemaStructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    organization_schema: bool = False
    product_schema: bool = False
    faq_schema: bool = False
    breadcrumb_schema: bool = False
    review_schema: bool = False
    schema_validation_errors: int = 0

class IndiaSpecific(BaseModel):
    model_config = ConfigDict(extra="ignore")
    inr_currency_use: bool = False
    india_tax_keywords: bool = False
    hreflang_en_in: bool = False
    localized_content_relevance: float = 0.0

class HealthErrors(BaseModel):
    model_config = ConfigDict(extra="ignore")
    error_404_count: int = 0
    redirect_chains: int = 0
    broken_links: int = 0
    simulated_index_errors: int = 0

class BrandUX(BaseModel):
    model_config = ConfigDict(extra="ignore")
    structured_nav_clarity: bool = False
    cta_optimization: bool = False
    content_freshness: bool = False

class FullSEOResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    domain_authority: DomainAuthority
    crawlability: CrawlabilityIndexing
    url_structure: URLStructure
    meta_html: MetaHTMLSignals
    content: ContentQuality
    intent: SearchIntent
    ymyl: YMYLTrust
    eeat: EEATSignals
    technical: TechnicalPerformance
    mobile: MobileUX
    linking: Linking
    schema_data: SchemaStructuredData
    india_specific: IndiaSpecific
    health: HealthErrors
    brand_ux: BrandUX
    overall_score: float = 0.0
    ai_insights: Optional[Dict[str, Any]] = None

class ComparisonResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    baseline_url: str
    competitor_url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    gaps: List[Dict[str, Any]]
    scores: Dict[str, float]
    overall_grade: float
    summary: str
    ai_analysis: Optional[str] = None
