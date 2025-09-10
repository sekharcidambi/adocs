#!/usr/bin/env python3
"""
Test script for the Comprehensive ADocS Service
"""

import asyncio
import json
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from comprehensive_adocs_service import ComprehensiveADocSService

async def test_service():
    """Test the comprehensive ADocS service with a sample repository."""
    
    # Initialize the service - API keys are handled internally via environment variables
    service = ComprehensiveADocSService()
    
    # Test with a sample repository
    test_repo_url = "https://github.com/vercel/next.js"
    
    try:
        print(f"Testing comprehensive ADocS service with: {test_repo_url}")
        print("=" * 60)
        
        # Run the complete analysis
        result = await service.analyze_and_generate_documentation(test_repo_url)
        
        print("✅ Analysis completed successfully!")
        print(f"Repository: {result['repository']['name']}")
        print(f"Business Domain: {result['repository']['businessDomain']}")
        print(f"Architecture: {result['repository']['architecture']['pattern']}")
        print(f"Output Directory: {result['generatedFiles']['outputDirectory']}")
        print(f"Generated Files: {len(result['generatedFiles']['files']['markdownFiles'])} markdown files")
        
        # Print navigation structure
        print("\n📋 Navigation Structure:")
        for item in result['navigation'][:3]:  # Show first 3 items
            print(f"  - {item['title']}")
            if 'children' in item and item['children']:
                for child in item['children'][:2]:  # Show first 2 children
                    print(f"    - {child['title']}")
        
        print(f"\n📁 Full result saved to: {result['generatedFiles']['outputDirectory']}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
