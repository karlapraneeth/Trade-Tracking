# Robinhood Options Trade Tracker

A comprehensive Python Flask web application for tracking your Robinhood options trades with GitHub integration for data backup and synchronization.

## Features

### Trade Tracking
- **Entry Details**: Ticker, trade type, entry price, strike price, expiration date, quantity, entry reason
- **Exit Details**: Exit price, exit date, exit reason
- **Additional Information**: Notes, P&L calculations, trade status
- **Trade Types**: Call/Put options, Spreads, Straddles, Strangles, Iron Condors, Butterflies

### Capital Management
- **Portfolio Overview**: Total capital, realized P&L, open positions
- **Performance Analytics**: Win rate, average win/loss, profit factor
- **Risk Tracking**: Position sizing and risk management tools

### GitHub Integration
- **Automatic Sync**: Sync your trade data to a GitHub repository
- **Data Backup**: Never lose your trading data
- **Version Control**: Track changes to your trading strategy over time
- **Collaboration**: Share your trading data with advisors or partners

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd trade-tracker
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///trades.db

# GitHub OAuth Configuration (Optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# GitHub Repository Configuration
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=trade-tracker-data
```

### 3. GitHub OAuth Setup (Optional)

To enable GitHub integration:

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App with:
   - Homepage URL: `http://localhost:5000`
   - Authorization callback URL: `http://localhost:5000/github-callback`
3. Copy the Client ID and Client Secret to your `.env` file

### 4. Create GitHub Repository

Create a new repository for storing your trade data:

```bash
# Create a new repository on GitHub
# Repository name: trade-tracker-data (or whatever you prefer)
# Make it private for security
```

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` to access the application.

## Usage

### Adding Trades

1. **Register/Login**: Create an account or login
2. **Add Trade**: Fill out the trade form with:
   - Basic info (ticker, trade type, dates, prices)
   - Entry reason (why you're taking the trade)
   - Exit details (when closing the trade)
   - Additional notes

### GitHub Sync

1. **Connect GitHub**: Click "Sync to GitHub" in the user menu
2. **Authorize**: Complete GitHub OAuth flow
3. **Automatic Sync**: Trades are automatically synced to your GitHub repository
4. **Manual Sync**: Use the sync buttons to manually sync data

### Data Management

- **Export**: Download your trade data as JSON
- **Import**: Upload trade data from backup files
- **Search**: Search trades by ticker, reason, or other criteria
- **Filter**: Filter by trade status (open/closed)

## API Endpoints

The application provides a REST API for programmatic access:

### Trades
- `GET /api/trades` - Get all trades
- `POST /api/trades` - Create new trade
- `PUT /api/trades/<id>` - Update trade
- `DELETE /api/trades/<id>` - Delete trade

### GitHub Sync
- `POST /api/sync-github` - Sync trades to GitHub
- `POST /api/sync-from-github` - Sync trades from GitHub

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - User email
- `password_hash` - Hashed password
- `github_token` - GitHub OAuth token
- `created_at` - Account creation timestamp

### Trades Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `ticker` - Stock symbol (e.g., AAPL)
- `trade_type` - Type of options trade
- `entry_date` - Date trade was opened
- `entry_price` - Price per contract
- `strike_price` - Strike price of option
- `expiration_date` - Option expiration date
- `quantity` - Number of contracts
- `entry_reason` - Why the trade was taken
- `exit_date` - Date trade was closed
- `exit_price` - Price per contract at exit
- `exit_reason` - Why the trade was closed
- `notes` - Additional notes
- `status` - 'open' or 'closed'
- `pnl` - Profit/Loss calculation
- `created_at` - Trade creation timestamp
- `updated_at` - Last update timestamp

## Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Security Considerations

1. **Change Secret Key**: Always change the SECRET_KEY in production
2. **Use HTTPS**: Deploy with SSL/TLS in production
3. **Database Security**: Use a secure database in production
4. **GitHub Tokens**: Store GitHub tokens securely
5. **Private Repository**: Use private GitHub repositories for trade data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the GitHub Issues page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## Roadmap

- [ ] Advanced analytics and charts
- [ ] Mobile app
- [ ] Real-time market data integration
- [ ] Trade alerts and notifications
- [ ] Portfolio performance tracking
- [ ] Risk management tools
- [ ] Export to Excel/CSV
- [ ] Multi-account support