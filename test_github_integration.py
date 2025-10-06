#!/usr/bin/env python3
"""
Test script for GitHub integration
This script helps you verify that your GitHub OAuth and repository setup is working correctly.
"""

import os
import requests
import json
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    required_vars = [
        'GITHUB_CLIENT_ID',
        'GITHUB_CLIENT_SECRET', 
        'GITHUB_REPO_OWNER',
        'GITHUB_REPO_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('your-'):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or incomplete environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with the correct values.")
        return False
    
    return True

def test_github_oauth():
    """Test GitHub OAuth configuration"""
    print("🔍 Testing GitHub OAuth configuration...")
    
    client_id = os.getenv('GITHUB_CLIENT_ID')
    client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    # Test OAuth app exists
    oauth_url = f"https://api.github.com/applications/{client_id}"
    response = requests.get(oauth_url, auth=(client_id, client_secret))
    
    if response.status_code == 200:
        app_data = response.json()
        print(f"✅ OAuth App found: {app_data['name']}")
        print(f"   Homepage URL: {app_data['html_url']}")
        return True
    else:
        print(f"❌ OAuth App not found or invalid credentials")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_github_repository():
    """Test GitHub repository access"""
    print("\n🔍 Testing GitHub repository access...")
    
    repo_owner = os.getenv('GITHUB_REPO_OWNER')
    repo_name = os.getenv('GITHUB_REPO_NAME')
    
    # Test repository exists
    repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    response = requests.get(repo_url)
    
    if response.status_code == 200:
        repo_data = response.json()
        print(f"✅ Repository found: {repo_data['full_name']}")
        print(f"   Private: {repo_data['private']}")
        print(f"   URL: {repo_data['html_url']}")
        return True
    else:
        print(f"❌ Repository not found or not accessible")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_trades_file():
    """Test if trades.json file exists in repository"""
    print("\n🔍 Testing trades.json file...")
    
    repo_owner = os.getenv('GITHUB_REPO_OWNER')
    repo_name = os.getenv('GITHUB_REPO_NAME')
    
    # Check if trades.json exists
    file_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/trades.json"
    response = requests.get(file_url)
    
    if response.status_code == 200:
        file_data = response.json()
        print(f"✅ trades.json file found")
        print(f"   Size: {file_data['size']} bytes")
        print(f"   Last updated: {file_data['updated_at']}")
        return True
    elif response.status_code == 404:
        print("❌ trades.json file not found")
        print("   Please create this file in your repository with initial content:")
        print("   {\n     \"last_sync\": \"2024-01-01T00:00:00\",\n     \"trades\": []\n   }")
        return False
    else:
        print(f"❌ Error checking trades.json file")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_oauth_callback_url():
    """Test OAuth callback URL configuration"""
    print("\n🔍 Testing OAuth callback URL...")
    
    client_id = os.getenv('GITHUB_CLIENT_ID')
    client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    # Get OAuth app details
    oauth_url = f"https://api.github.com/applications/{client_id}"
    response = requests.get(oauth_url, auth=(client_id, client_secret))
    
    if response.status_code == 200:
        app_data = response.json()
        callback_url = app_data.get('callback_url', 'Not set')
        print(f"✅ OAuth App callback URL: {callback_url}")
        
        if callback_url == 'http://localhost:5000/github-callback':
            print("✅ Callback URL is correctly configured")
            return True
        else:
            print("❌ Callback URL is not correctly configured")
            print("   Expected: http://localhost:5000/github-callback")
            print("   Actual: " + callback_url)
            return False
    else:
        print("❌ Could not retrieve OAuth app details")
        return False

def main():
    """Run all tests"""
    print("🚀 GitHub Integration Test Suite")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        return
    
    # Run tests
    tests = [
        test_github_oauth,
        test_github_repository,
        test_trades_file,
        test_oauth_callback_url
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your GitHub integration should work correctly.")
        print("\nNext steps:")
        print("1. Start your Trade Tracker application: python3 run.py")
        print("2. Go to http://localhost:5000")
        print("3. Login and click 'Sync to GitHub' to authorize")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        print("\nCommon fixes:")
        print("1. Update your .env file with correct values")
        print("2. Create the GitHub repository")
        print("3. Create the trades.json file in your repository")
        print("4. Update OAuth app callback URL")

if __name__ == '__main__':
    main()