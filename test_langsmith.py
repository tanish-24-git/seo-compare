"""
Test script to verify LangSmith tracing integration.
This will trigger a simple AI call and you should see it in LangSmith dashboard.
"""
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.ai_service import AIService

async def test_langsmith_tracing():
    print("🧪 Testing LangSmith Tracing Integration...")
    print("=" * 50)
    
    ai_service = AIService()
    
    # Test 1: analyze_seo_content
    print("\n📊 Test 1: Analyzing SEO content...")
    sample_html = """
    <html>
        <head><title>Test Insurance Page</title></head>
        <body>
            <h1>Life Insurance Plans</h1>
            <p>IRDAI Registration: 123456</p>
            <p>Our claim settlement ratio is 98%</p>
        </body>
    </html>
    """
    
    result = await ai_service.analyze_seo_content(sample_html, "https://test.com")
    print(f"✅ Result: {result}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\n📈 Check your LangSmith dashboard:")
    print("   https://smith.langchain.com/")
    print("   Project: seo-compare-engine")
    print("\nYou should see 1 trace for 'analyze_seo_content'")

if __name__ == "__main__":
    asyncio.run(test_langsmith_tracing())
