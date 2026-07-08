#!/usr/bin/env python3
"""
Setup script to configure Gemini API key
"""

import os

def setup_gemini_api():
    print("=" * 60)
    print("🤖 GEMINI AI SETUP FOR PROGRESSIONPRED")
    print("=" * 60)
    
    print("\n📋 Steps to get your Gemini API key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated API key")
    
    api_key = input("\n🔑 Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Skipping setup.")
        return
    
    # Update app.py with the API key
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual API key
        updated_content = content.replace(
            'GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"',
            f'GEMINI_API_KEY = "{api_key}"'
        )
        
        with open('app.py', 'w') as f:
            f.write(updated_content)
        
        # Update gemini_insights.py
        with open('gemini_insights.py', 'r') as f:
            content = f.read()
        
        # Add API key configuration at the top
        if 'genai.configure' not in content:
            lines = content.split('\n')
            lines.insert(1, f'import os')
            lines.insert(2, f'genai.configure(api_key="{api_key}")')
            content = '\n'.join(lines)
            
            with open('gemini_insights.py', 'w') as f:
                f.write(content)
        
        print("✅ Gemini API key configured successfully!")
        print("\n🚀 Features now available:")
        print("  • AI-powered health insights")
        print("  • Smart medication reminders")
        print("  • Health trend analysis")
        print("  • Prescription scanning insights")
        
    except Exception as e:
        print(f"❌ Error configuring API key: {e}")
        print("Please manually replace 'YOUR_GEMINI_API_KEY_HERE' in app.py")

def install_dependencies():
    print("\n📦 Installing required dependencies...")
    os.system("pip install google-generativeai")
    print("✅ Dependencies installed!")

if __name__ == "__main__":
    install_dependencies()
    setup_gemini_api()
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("Run: python app.py")
    print("Then visit: http://localhost:5000")
    print("=" * 60)