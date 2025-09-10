#!/usr/bin/env python3
"""
Test script for the Wiki Generation Service
"""

import asyncio
import json
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from wiki_generation_service import WikiGenerationService

async def test_service():
    """Test the wiki generation service with a sample repository."""
    
    # Initialize the service - API keys are handled internally via environment variables
    service = WikiGenerationService()
    
    # Test with a sample repository
    test_repo_url = "https://github.com/facebook/react"
    
    try:
        print(f"Testing wiki generation service with: {test_repo_url}")
        print("=" * 60)
        
        # Run the complete wiki generation
        result = await service.generate_enhanced_wiki(test_repo_url)
        
        print("✅ Wiki generation completed successfully!")
        print(f"Repository: {result['repository']['name']}")
        print(f"Description: {result['repository']['description']}")
        print(f"Stars: {result['repository']['stars']}")
        print(f"Language: {result['repository']['language']}")
        print(f"Output Directory: {result['generatedFiles']['outputDirectory']}")
        print(f"Enhanced Pages: {len(result['pages'])} pages")
        
        # Print some enhanced pages info
        print("\n📋 Enhanced Pages:")
        for page in result['pages'][:3]:  # Show first 3 pages
            print(f"  - {page['title']} ({page.get('type', 'other')})")
            print(f"    Summary: {page.get('summary', 'No summary')[:100]}...")
            print(f"    Key Points: {len(page.get('keyPoints', []))} points")
            print(f"    Improvements: {len(page.get('suggestedImprovements', []))} suggestions")
        
        print(f"\n📁 Full result saved to: {result['generatedFiles']['outputDirectory']}")
        
    except Exception as e:
        print(f"❌ Error during wiki generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
