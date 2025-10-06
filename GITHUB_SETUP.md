# GitHub Integration Setup Guide

This guide will walk you through setting up GitHub integration for your Trade Tracker application, including OAuth authentication and data synchronization.

## Prerequisites

- A GitHub account
- Your Trade Tracker application running locally
- Basic familiarity with GitHub

## Step 1: Create a GitHub Repository for Your Trade Data

### 1.1 Create a New Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** button in the top right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name**: `trade-tracker-data` (or your preferred name)
   - **Description**: "My Robinhood Options Trade Data"
   - **Visibility**: Select **"Private"** (recommended for financial data)
   - **Initialize**: Check "Add a README file"
5. Click **"Create repository"**

### 1.2 Set Up Repository Structure

Once your repository is created, you'll need to add some initial files:

1. **Create a `trades.json` file** in your repository:
   - Click **"Add file"** > **"Create new file"**
   - Name it `trades.json`
   - Add this initial content:
   ```json
   {
     "last_sync": "2024-01-01T00:00:00",
     "trades": []
   }
   ```
   - Click **"Commit new file"**

2. **Create a `.gitignore` file** (optional but recommended):
   - Click **"Add file"** > **"Create new file"**
   - Name it `.gitignore`
   - Add this content:
   ```
   # Backup files
   *.backup
   *.bak
   
   # Temporary files
   *.tmp
   *.temp
   ```
   - Click **"Commit new file"**

## Step 2: Create a GitHub OAuth App

### 2.1 Navigate to OAuth Apps Settings

1. Go to [GitHub.com](https://github.com)
2. Click your profile picture in the top right
3. Select **"Settings"**
4. In the left sidebar, click **"Developer settings"**
5. Click **"OAuth Apps"**
6. Click **"New OAuth App"**

### 2.2 Configure Your OAuth App

Fill in the following details:

- **Application name**: `Trade Tracker` (or your preferred name)
- **Homepage URL**: `http://localhost:5000`
- **Application description**: `Personal options trade tracking application`
- **Authorization callback URL**: `http://localhost:5000/github-callback`

**Important Notes:**
- Use `http://localhost:5000` for local development
- If you deploy to a server, update these URLs to your domain
- The callback URL must match exactly what's in your application

### 2.3 Get Your OAuth Credentials

After creating the OAuth App:

1. You'll see a page with your app details
2. **Copy the Client ID** (you'll need this)
3. Click **"Generate a new client secret"**
4. **Copy the Client Secret** (you'll need this too)
5. **Keep these credentials secure** - don't share them publicly

## Step 3: Configure Your Trade Tracker Application

### 3.1 Update Environment Variables

1. Open your `.env` file in the trade tracker directory
2. Update the GitHub configuration section:

```env
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_actual_client_id_here
GITHUB_CLIENT_SECRET=your_actual_client_secret_here

# GitHub Repository Configuration
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=trade-tracker-data
```

**Replace:**
- `your_actual_client_id_here` with your OAuth App Client ID
- `your_actual_client_secret_here` with your OAuth App Client Secret
- `your_github_username` with your GitHub username
- `trade-tracker-data` with your repository name (if different)

### 3.2 Restart Your Application

After updating the `.env` file:

1. Stop your application (Ctrl+C)
2. Restart it:
   ```bash
   python3 run.py
   ```

## Step 4: Connect Your Account to GitHub

### 4.1 Login to Trade Tracker

1. Go to `http://localhost:5000`
2. Register a new account or login
3. You should see the dashboard

### 4.2 Authorize GitHub Integration

1. In the top navigation, click on your username
2. Click **"Sync to GitHub"** from the dropdown menu
3. You'll be redirected to GitHub's authorization page
4. Click **"Authorize Trade Tracker"** (or whatever you named your app)
5. You'll be redirected back to your application
6. You should see a success message

### 4.3 Test the Integration

1. Add a test trade to your application
2. The trade should automatically sync to your GitHub repository
3. Check your GitHub repository - you should see the trade data in `trades.json`

## Step 5: Verify Everything is Working

### 5.1 Check GitHub Repository

1. Go to your GitHub repository
2. Click on `trades.json`
3. You should see your trade data in JSON format
4. The file should update automatically when you add/modify trades

### 5.2 Test Manual Sync

1. In your Trade Tracker, try the **"Sync to GitHub"** button
2. You should see a success message
3. Check your GitHub repository to confirm the data updated

### 5.3 Test Import from GitHub

1. Try the **"Sync from GitHub"** button
2. This will import any data from your GitHub repository
3. Use this if you need to restore data or sync between devices

## Troubleshooting

### Common Issues and Solutions

#### 1. "GitHub not connected" Error
**Problem**: You see this error when trying to sync
**Solution**: 
- Make sure you've completed the OAuth authorization
- Check that your GitHub token is saved in the database
- Try re-authorizing by clicking "Sync to GitHub" again

#### 2. "Failed to sync to GitHub" Error
**Problem**: Sync operations fail
**Solutions**:
- Check your repository name and owner in `.env`
- Verify your GitHub token is valid
- Make sure the repository exists and you have write access
- Check that `trades.json` exists in your repository

#### 3. OAuth Redirect Issues
**Problem**: OAuth callback doesn't work
**Solutions**:
- Verify the callback URL in your OAuth App settings matches exactly
- Make sure you're using `http://localhost:5000` (not `https://`)
- Check that your application is running on port 5000

#### 4. Permission Denied Errors
**Problem**: Can't write to GitHub repository
**Solutions**:
- Make sure the repository is owned by the same GitHub account
- Check that the OAuth App has the correct permissions
- Verify the repository name and owner in your `.env` file

### Debug Mode

To see detailed error messages:

1. Set `FLASK_DEBUG=True` in your `.env` file
2. Restart your application
3. Check the console output for error details

## Security Best Practices

### 1. Keep Credentials Secure
- Never commit your `.env` file to version control
- Use strong, unique client secrets
- Regularly rotate your OAuth credentials

### 2. Repository Security
- Keep your trade data repository private
- Don't share your OAuth credentials
- Consider using GitHub's security features (2FA, etc.)

### 3. Data Privacy
- Your trade data is stored in your private GitHub repository
- Only you have access to this data
- The application doesn't store your GitHub credentials (only tokens)

## Advanced Configuration

### Custom Repository Structure

You can customize how your data is stored in GitHub by modifying the `GitHubAPI` class in `app.py`:

```python
# Example: Store data in a subfolder
def sync_trades_to_github(self, trades):
    trades_data = {
        'last_sync': datetime.utcnow().isoformat(),
        'trades': [trade.to_dict() for trade in trades]
    }
    return self.update_file_content('data/trades.json', trades_data, 'Update trades')
```

### Multiple Environments

For different environments (development, production), create separate OAuth Apps:

1. **Development**: `http://localhost:5000`
2. **Production**: `https://yourdomain.com`

Update your `.env` file accordingly for each environment.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the application logs for error messages
3. Verify your GitHub repository and OAuth App settings
4. Make sure all URLs and credentials are correct

## Next Steps

Once GitHub integration is working:

1. **Regular Backups**: Your data syncs automatically, but you can also manually sync
2. **Multiple Devices**: Access your data from any device by syncing from GitHub
3. **Data Analysis**: Use GitHub's file history to track your trading evolution
4. **Sharing**: Share specific trades or analysis by sharing GitHub links (if desired)

Your trade data is now safely backed up and version-controlled on GitHub! 🎉