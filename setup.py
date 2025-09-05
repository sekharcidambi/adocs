"""
Setup script for ADocS project
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    directories = [
        "data/repo_metadata",
        "src"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_api_key():
    """Check if Anthropic API key is set."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your_api_key_here'")
        print("   Get your API key from: https://console.anthropic.com/")
    else:
        print("✓ ANTHROPIC_API_KEY is set")

def main():
    """Main setup function."""
    print("=== ADocS Setup ===")
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create directories
    create_directories()
    
    # Check API key
    check_api_key()
    
    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("1. Place your data files in the data/ directory")
    print("2. Set your ANTHROPIC_API_KEY environment variable")
    print("3. Run: python main.py build")
    print("4. Run: python main.py (for demonstration)")

if __name__ == "__main__":
    main()
