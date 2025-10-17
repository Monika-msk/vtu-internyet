#!/usr/bin/env python3
"""
Test script to verify the VTU Internship Watcher setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment variables and configuration."""
    print("🔍 Testing Environment Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or environment variables.")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_dependencies():
    """Test if all required packages are installed."""
    print("\n🔍 Testing Dependencies...")
    
    required_packages = [
        'requests',
        'python-dotenv',
        'schedule'
    ]
    # Map pip package names to their importable module names
    module_name_overrides = {
        'python-dotenv': 'dotenv',
    }
    
    missing_packages = []
    
    for package in required_packages:
        try:
            module_name = module_name_overrides.get(package, package).replace('-', '_')
            __import__(module_name)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def test_api_connection():
    """Test VTU API connection."""
    print("\n🔍 Testing VTU API Connection...")
    
    try:
        import requests
        
        url = "https://vtuapi.internyet.in/api/v1/internships?page=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success') and data.get('data', {}).get('data'):
            internships_count = len(data['data']['data'])
            total_count = data['data'].get('total', 0)
            print(f"✅ API connection working! Found {internships_count} internships on page 1 (Total: {total_count})")
            return True
        else:
            print("❌ API returned unexpected format")
            return False
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("Check your internet connection or the API might be down.")
        return False

def test_email_config():
    """Test email configuration (without sending)."""
    print("\n🔍 Testing Email Configuration...")
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    # Basic validation
    if not sender_email or '@' not in sender_email:
        print("❌ Invalid sender email format")
        return False
    
    if not sender_password or len(sender_password) < 10:
        print("❌ Sender password seems too short (should be Gmail app password)")
        return False
    
    if not recipient_email or '@' not in recipient_email:
        print("❌ Invalid recipient email format")
        return False
    
    print("✅ Email configuration looks valid!")
    print("Note: Actual email sending will be tested when the script runs.")
    return True

def test_file_permissions():
    """Test file read/write permissions."""
    print("\n🔍 Testing File Permissions...")
    
    try:
        # Test writing to seen_internships.json
        test_file = "test_permissions.json"
        with open(test_file, 'w') as f:
            f.write('{"test": true}')
        
        # Test reading
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Clean up
        os.remove(test_file)
        
        print("✅ File read/write permissions working!")
        return True
        
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 VTU Internship Watcher - Setup Test\n")
    
    tests = [
        ("Environment Variables", test_environment),
        ("Dependencies", test_dependencies),
        ("API Connection", test_api_connection),
        ("Email Configuration", test_email_config),
        ("File Permissions", test_file_permissions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("You can now run: python internship_watcher.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
