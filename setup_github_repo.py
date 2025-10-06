#!/usr/bin/env python3
"""
GitHub Repository Setup Helper
This script helps you set up the GitHub repository structure for your trade tracker.
"""

import os
import requests
import json
from dotenv import load_dotenv

def load_environment():
    """Load environment variables"""
    load_dotenv()
    
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPO_OWNER')
    repo_name = os.getenv('GITHUB_REPO_NAME')
    
    if not all([github_token, repo_owner, repo_name]):
        print("❌ Missing required environment variables:")
        if not github_token:
            print("   - GITHUB_TOKEN (create a Personal Access Token)")
        if not repo_owner:
            print("   - GITHUB_REPO_OWNER (your GitHub username)")
        if not repo_name:
            print("   - GITHUB_REPO_NAME (repository name)")
        return None, None, None
    
    return github_token, repo_owner, repo_name

def create_trades_file(github_token, repo_owner, repo_name):
    """Create the initial trades.json file in the repository"""
    print("📝 Creating trades.json file...")
    
    trades_content = {
        "last_sync": "2024-01-01T00:00:00",
        "trades": []
    }
    
    # Encode content as base64
    import base64
    content = json.dumps(trades_content, indent=2)
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/trades.json"
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'message': 'Initialize trades.json for Trade Tracker',
        'content': encoded_content
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ trades.json file created successfully")
        return True
    elif response.status_code == 422:
        print("⚠️  trades.json file already exists")
        return True
    else:
        print(f"❌ Failed to create trades.json file")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def create_gitignore_file(github_token, repo_owner, repo_name):
    """Create a .gitignore file for the repository"""
    print("📝 Creating .gitignore file...")
    
    gitignore_content = """# Backup files
*.backup
*.bak

# Temporary files
*.tmp
*.temp

# Log files
*.log

# Environment files (if any)
.env.local
.env.production
"""
    
    # Encode content as base64
    import base64
    encoded_content = base64.b64encode(gitignore_content.encode('utf-8')).decode('utf-8')
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/.gitignore"
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'message': 'Add .gitignore file',
        'content': encoded_content
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ .gitignore file created successfully")
        return True
    elif response.status_code == 422:
        print("⚠️  .gitignore file already exists")
        return True
    else:
        print(f"❌ Failed to create .gitignore file")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def create_readme_file(github_token, repo_owner, repo_name):
    """Create a README file for the repository"""
    print("📝 Creating README.md file...")
    
    readme_content = f"""# Trade Tracker Data

This repository contains my options trading data, automatically synced from the Trade Tracker application.

## Data Structure

- `trades.json` - Contains all trade data in JSON format
- `.gitignore` - Git ignore rules for the repository

## Security

This repository is private and contains sensitive financial data. Do not share or make public.

## Usage

This data is automatically managed by the Trade Tracker application. Manual editing is not recommended.

## Last Updated

Data is automatically synced when trades are added, modified, or deleted in the Trade Tracker application.

---

*This repository is managed by Trade Tracker - A Python Flask application for tracking options trades.*
"""
    
    # Encode content as base64
    import base64
    encoded_content = base64.b64encode(readme_content.encode('utf-8')).decode('utf-8')
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/README.md"
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'message': 'Add README.md file',
        'content': encoded_content
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ README.md file created successfully")
        return True
    elif response.status_code == 422:
        print("⚠️  README.md file already exists")
        return True
    else:
        print(f"❌ Failed to create README.md file")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    """Main setup function"""
    print("🚀 GitHub Repository Setup Helper")
    print("=" * 50)
    
    # Load environment
    github_token, repo_owner, repo_name = load_environment()
    
    if not github_token:
        print("\n📋 To use this script, you need to:")
        print("1. Create a GitHub Personal Access Token:")
        print("   - Go to GitHub.com → Settings → Developer settings → Personal access tokens")
        print("   - Generate new token with 'repo' permissions")
        print("   - Add it to your .env file as GITHUB_TOKEN")
        print("2. Set GITHUB_REPO_OWNER and GITHUB_REPO_NAME in your .env file")
        print("3. Run this script again")
        return
    
    print(f"📁 Setting up repository: {repo_owner}/{repo_name}")
    
    # Create files
    success = True
    success &= create_trades_file(github_token, repo_owner, repo_name)
    success &= create_gitignore_file(github_token, repo_owner, repo_name)
    success &= create_readme_file(github_token, repo_owner, repo_name)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Repository setup completed successfully!")
        print(f"📂 Repository URL: https://github.com/{repo_owner}/{repo_name}")
        print("\nNext steps:")
        print("1. Set up GitHub OAuth App (see GITHUB_SETUP.md)")
        print("2. Update your .env file with OAuth credentials")
        print("3. Start your Trade Tracker application")
        print("4. Authorize GitHub integration in the app")
    else:
        print("❌ Some files failed to create. Please check the errors above.")

if __name__ == '__main__':
    main()