#!/usr/bin/env python3
"""
Test script for the Documentation Retrieval Service
"""

import json
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from documentation_retrieval_service import DocumentationRetrievalService

def test_service():
    """Test the documentation retrieval service with sample operations."""
    
    # Initialize the service
    service = DocumentationRetrievalService()
    
    try:
        print("Testing Documentation Retrieval Service")
        print("=" * 50)
        
        # Test 1: List available repositories
        print("\n1. Testing list available repositories...")
        result = service.list_available_repositories('docs')
        if result['success']:
            print(f"✅ Found {result['count']} repositories with docs documentation")
            for repo in result['repositories'][:3]:  # Show first 3
                print(f"   - {repo['name']} (generated: {repo['generated_at']})")
        else:
            print(f"❌ Error listing repositories: {result['error']}")
        
        # Test 2: List available wiki repositories
        print("\n2. Testing list available wiki repositories...")
        result = service.list_available_repositories('wiki')
        if result['success']:
            print(f"✅ Found {result['count']} repositories with wiki documentation")
            for repo in result['repositories'][:3]:  # Show first 3
                print(f"   - {repo['name']} (generated: {repo['generated_at']})")
        else:
            print(f"❌ Error listing wiki repositories: {result['error']}")
        
        # Test 3: Get documentation info for a sample repository
        print("\n3. Testing get documentation info...")
        test_repo = "https://github.com/vercel/next.js"
        result = service.get_documentation_info(test_repo, 'docs')
        if result['success']:
            print(f"✅ Found documentation for {test_repo}")
            print(f"   Generated: {result['generated_at']}")
            print(f"   Sections: {result['section_count']}")
            print(f"   Available sections: {', '.join(result['available_sections'][:3])}...")
        else:
            print(f"❌ No documentation found for {test_repo}: {result['error']}")
        
        # Test 4: Get complete documentation structure
        print("\n4. Testing get complete documentation structure...")
        result = service.get_documentation_structure(test_repo, 'docs')
        if result['success']:
            print(f"✅ Retrieved complete structure for {test_repo}")
            print(f"   Generated: {result['generated_at']}")
            print(f"   Available sections: {len(result['available_sections'])}")
            print(f"   Has structure: {bool(result['structure'])}")
            print(f"   Has metadata: {bool(result['metadata'])}")
            print(f"   Has index: {bool(result['index'])}")
        else:
            print(f"❌ Error retrieving structure: {result['error']}")
        
        # Test 5: Get specific section content (if available)
        if result['success'] and result['available_sections']:
            section = result['available_sections'][0]
            print(f"\n5. Testing get specific section content ('{section}')...")
            section_result = service.get_section_content(test_repo, section, 'docs')
            if section_result['success']:
                print(f"✅ Retrieved section '{section}'")
                print(f"   Content length: {len(section_result['content'])} characters")
                print(f"   File path: {section_result['file_path']}")
            else:
                print(f"❌ Error retrieving section: {section_result['error']}")
        
        print("\n" + "=" * 50)
        print("Documentation Retrieval Service test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()
