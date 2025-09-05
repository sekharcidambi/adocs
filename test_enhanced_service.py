#!/usr/bin/env python3
"""
Test script for the Enhanced ADocS Service
"""

import json
import os
from enhanced_adocs_service import EnhancedADocSService

def test_enhanced_service():
    """Test the enhanced ADocS service with sample repository metadata."""
    
    # Sample repository metadata (similar to what the Next.js API would send)
    sample_metadata = {
        "github_url": "https://github.com/apache/ofbiz-framework",
        "overview": "Apache OFBiz is an open source product for the automation of enterprise processes. It includes framework components and business applications for ERP, CRM, E-Business/E-Commerce, Supply Chain Management and Manufacturing Resource Planning.",
        "business_domain": "Software Development",
        "architecture": {
            "pattern": "Full-Stack",
            "description": "Full-stack application with separate frontend and backend"
        },
        "tech_stack": {
            "languages": ["Java", "Groovy", "JavaScript"],
            "frontend": ["React", "Angular"],
            "backend": ["Spring", "Hibernate"],
            "databases": ["MySQL", "PostgreSQL"],
            "devops": ["Docker", "Jenkins"]
        }
    }
    
    print("Testing Enhanced ADocS Service...")
    print(f"Sample metadata: {json.dumps(sample_metadata, indent=2)}")
    print()
    
    try:
        # Initialize the service
        service = EnhancedADocSService()
        
        # Generate and store documentation
        print("Generating documentation...")
        result = service.generate_and_store_documentation(sample_metadata)
        
        print("✅ Documentation generation completed successfully!")
        print()
        print("Results:")
        print(f"  Repository: {result['repository']}")
        print(f"  Output Directory: {result['output_directory']}")
        print(f"  Files Created: {len(result['files_created']['markdown_files'])} markdown files")
        print()
        print("Files created:")
        for file_type, file_path in result['files_created'].items():
            if file_type == 'markdown_files':
                print(f"  {file_type}: {len(file_path)} files")
                for i, path in enumerate(file_path[:3]):  # Show first 3 files
                    print(f"    - {os.path.basename(path)}")
                if len(file_path) > 3:
                    print(f"    ... and {len(file_path) - 3} more files")
            else:
                print(f"  {file_type}: {os.path.basename(file_path)}")
        
        print()
        print("📁 Check the generated_docs directory for the output files!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_service()
