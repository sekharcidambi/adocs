#!/usr/bin/env python3
"""
Test script for the new ADocS service architecture.
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend_env_example'))

from adocs_service import ADocSService

async def test_new_architecture():
    """Test the new ADocS service architecture."""
    
    print("=== Testing New ADocS Service Architecture ===\n")
    
    # Initialize service
    service = ADocSService()
    
    # Test 1: Get repositories
    print("1. Testing get_repositories...")
    try:
        result = service.get_repositories('docs')
        print(f"   Success: {result['success']}")
        print(f"   Count: {result['count']}")
        if result['repositories']:
            print(f"   Sample repo: {result['repositories'][0]['name']}")
        print("   ✓ get_repositories test passed\n")
    except Exception as e:
        print(f"   ✗ get_repositories test failed: {e}\n")
    
    # Test 2: Get repositories (wiki type)
    print("2. Testing get_repositories (wiki type)...")
    try:
        result = service.get_repositories('wiki')
        print(f"   Success: {result['success']}")
        print(f"   Count: {result['count']}")
        print("   ✓ get_repositories (wiki) test passed\n")
    except Exception as e:
        print(f"   ✗ get_repositories (wiki) test failed: {e}\n")
    
    # Test 3: Get documentation (if any repos exist)
    print("3. Testing get_documentation...")
    try:
        # First get repositories to see if any exist
        repos_result = service.get_repositories('docs')
        if repos_result['success'] and repos_result['repositories']:
            test_repo = repos_result['repositories'][0]['github_url']
            result = service.get_documentation(test_repo, 'docs')
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Repository: {result['repository']}")
                print(f"   Available sections: {len(result['available_sections'])}")
            print("   ✓ get_documentation test passed\n")
        else:
            print("   No repositories available for testing\n")
    except Exception as e:
        print(f"   ✗ get_documentation test failed: {e}\n")
    
    # Test 4: Get documentation section (if any repos exist)
    print("4. Testing get_documentation_section...")
    try:
        repos_result = service.get_repositories('docs')
        if repos_result['success'] and repos_result['repositories']:
            test_repo = repos_result['repositories'][0]['github_url']
            # Try to get a section
            result = service.get_documentation(test_repo, 'docs')
            if result['success'] and result['available_sections']:
                section = result['available_sections'][0]
                section_result = service.get_documentation_section(test_repo, section, 'docs')
                print(f"   Success: {section_result['success']}")
                if section_result['success']:
                    print(f"   Section: {section_result['section']}")
                    print(f"   Content length: {len(section_result['content'])}")
                print("   ✓ get_documentation_section test passed\n")
            else:
                print("   No sections available for testing\n")
        else:
            print("   No repositories available for testing\n")
    except Exception as e:
        print(f"   ✗ get_documentation_section test failed: {e}\n")
    
    # Test 5: Get repository info
    print("5. Testing get_repository_info...")
    try:
        repos_result = service.get_repositories('docs')
        if repos_result['success'] and repos_result['repositories']:
            test_repo = repos_result['repositories'][0]['github_url']
            result = service.get_repository_info(test_repo, 'docs')
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Repository: {result['repository']['name']}")
                print(f"   Generated at: {result['repository']['generated_at']}")
            print("   ✓ get_repository_info test passed\n")
        else:
            print("   No repositories available for testing\n")
    except Exception as e:
        print(f"   ✗ get_repository_info test failed: {e}\n")
    
    # Test 6: Analyze repository (this will take longer and requires API keys)
    print("6. Testing analyze_repository...")
    try:
        test_repo_url = "https://github.com/vercel/next.js"
        print(f"   Analyzing: {test_repo_url}")
        result = await service.analyze_repository(test_repo_url)
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Output directory: {result['output_directory']}")
            print(f"   Generated at: {result['generated_at']}")
        else:
            print(f"   Error: {result['error']}")
        print("   ✓ analyze_repository test completed\n")
    except Exception as e:
        print(f"   ✗ analyze_repository test failed: {e}\n")
    
    # Test 7: Generate wiki (this will take longer and requires API keys)
    print("7. Testing generate_wiki...")
    try:
        test_repo_url = "https://github.com/facebook/react"
        print(f"   Generating wiki for: {test_repo_url}")
        result = await service.generate_wiki(test_repo_url)
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Output directory: {result['output_directory']}")
            print(f"   Pages generated: {len(result['pages'])}")
        else:
            print(f"   Error: {result['error']}")
        print("   ✓ generate_wiki test completed\n")
    except Exception as e:
        print(f"   ✗ generate_wiki test failed: {e}\n")
    
    print("=== New ADocS Service Architecture Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_new_architecture())
