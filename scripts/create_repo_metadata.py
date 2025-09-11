#!/usr/bin/env python3
"""
Interactive script to create repository metadata for ADocS
"""

import json
import os
import sys

def get_user_input(prompt, required=True):
    """Get user input with validation."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please provide a value.")

def get_list_input(prompt):
    """Get a list of items from user input."""
    print(f"{prompt} (enter items separated by commas, or press Enter to skip):")
    items = input().strip()
    if not items:
        return []
    return [item.strip() for item in items.split(',') if item.strip()]

def create_repo_metadata():
    """Create repository metadata interactively."""
    print("=== ADocS Repository Metadata Creator ===\n")
    print("This script will help you create metadata for your repository.")
    print("Press Enter to skip optional fields.\n")
    
    metadata = {}
    
    # Required fields
    metadata["github_repo"] = get_user_input("GitHub URL: ")
    metadata["overview"] = get_user_input("Project overview/description: ")
    metadata["business_domain"] = get_user_input("Business domain (e.g., 'Web Development', 'Data Science'): ")
    
    # Architecture
    print("\n--- Architecture ---")
    arch_desc = get_user_input("Architecture description: ", required=False)
    arch_components = get_list_input("Main components")
    
    metadata["architecture"] = {
        "description": arch_desc,
        "components": arch_components
    }
    
    # Tech stack
    print("\n--- Technology Stack ---")
    metadata["tech_stack"] = get_list_input("Technologies, frameworks, languages used")
    
    # Features
    print("\n--- Features ---")
    metadata["features"] = get_list_input("Key features of your project")
    
    # Target audience
    print("\n--- Target Audience ---")
    metadata["target_audience"] = get_user_input("Who will use this project: ", required=False)
    
    return metadata

def main():
    """Main function."""
    try:
        # Create metadata
        metadata = create_repo_metadata()
        
        # Save to file
        filename = "my_repo_analysis.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Repository metadata saved to: {filename}")
        print("\nNext steps:")
        print(f"1. Review the file: {filename}")
        print("2. Make any necessary edits")
        print("3. Run: python main.py generate my_repo_analysis.json")
        print("4. Or set ANTHROPIC_API_KEY and run: python main.py")
        
        # Show preview
        print(f"\n📋 Preview of your metadata:")
        print(json.dumps(metadata, indent=2))
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
