#!/usr/bin/env python3
"""
Test script for the enhanced ADocS service with detailed content generation.
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from enhanced_adocs_service import EnhancedADocSService

def test_detailed_generation():
    """Test the enhanced service with detailed content generation."""
    
    # Sample repository metadata (you can replace this with actual data)
    repo_metadata = {
        "github_url": "https://github.com/apache/ofbiz-framework",
        "description": "Apache OFBiz is an open source enterprise resource planning (ERP) system",
        "business_domain": "Enterprise Resource Planning",
        "architecture": {
            "pattern": "Multi-tier Architecture",
            "components": ["Presentation Layer", "Business Logic Layer", "Data Access Layer"]
        },
        "tech_stack": {
            "languages": ["Java", "Groovy", "JavaScript"],
            "frameworks": ["Apache OFBiz Framework", "Spring", "Hibernate"],
            "databases": ["MySQL", "PostgreSQL", "Derby"],
            "frontend": ["React", "Angular", "Vue.js"],
            "devops": ["Docker", "Jenkins", "Maven"]
        },
        "setup_commands": [
            "git clone https://github.com/apache/ofbiz-framework.git",
            "cd ofbiz-framework",
            "./gradlew build",
            "./gradlew ofbiz"
        ],
        "stats": {
            "stars": 1200,
            "forks": 800,
            "size": 50000
        }
    }
    
    # Initialize the service
    service = EnhancedADocSService()
    
    try:
        print("🚀 Testing enhanced ADocS service with detailed content generation...")
        
        # Generate and store documentation
        result = service.generate_and_store_documentation(
            repo_metadata=repo_metadata,
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        print("✅ Documentation generation completed!")
        print(f"📁 Output directory: {result['output_directory']}")
        print(f"📄 Files created: {len(result['files_created'])}")
        
        # List the created files
        print("\n📋 Generated files:")
        for file_path in result['files_created']:
            print(f"  - {file_path}")
        
        # Show a sample of the generated content
        if result['files_created']:
            sample_file = result['files_created'][0]
            if sample_file.endswith('.md'):
                print(f"\n📖 Sample content from {Path(sample_file).name}:")
                print("-" * 50)
                with open(sample_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Show first 500 characters
                    print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Check if API key is available
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment variables.")
        print("   The service will use fallback content generation.")
    
    test_detailed_generation()

