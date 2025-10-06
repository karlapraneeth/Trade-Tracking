from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import requests
import json
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///trades.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# GitHub OAuth settings
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_REPO_OWNER = os.environ.get('GITHUB_REPO_OWNER', 'your-username')
GITHUB_REPO_NAME = os.environ.get('GITHUB_REPO_NAME', 'trade-tracker-data')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120))
    github_token = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trades = db.relationship('Trade', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    trade_type = db.Column(db.String(50), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    strike_price = db.Column(db.Float)
    expiration_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, nullable=False)
    entry_reason = db.Column(db.Text, nullable=False)
    exit_date = db.Column(db.Date)
    exit_price = db.Column(db.Float)
    exit_reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')
    pnl = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_pnl(self):
        if self.exit_price and self.status == 'closed':
            return (self.exit_price - self.entry_price) * self.quantity
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'trade_type': self.trade_type,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'entry_price': self.entry_price,
            'strike_price': self.strike_price,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'quantity': self.quantity,
            'entry_reason': self.entry_reason,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'exit_price': self.exit_price,
            'exit_reason': self.exit_reason,
            'notes': self.notes,
            'status': self.status,
            'pnl': self.pnl,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# GitHub API Integration
class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_file_content(self, path):
        """Get file content from GitHub repository"""
        url = f"{self.base_url}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            import base64
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            return json.loads(content)
        return None

    def update_file_content(self, path, content, message):
        """Update file content in GitHub repository"""
        url = f"{self.base_url}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{path}"
        
        # Get current file to get SHA
        current_file = requests.get(url, headers=self.headers)
        sha = None
        if current_file.status_code == 200:
            sha = current_file.json()['sha']
        
        import base64
        data = {
            'message': message,
            'content': base64.b64encode(json.dumps(content, indent=2).encode('utf-8')).decode('utf-8')
        }
        
        if sha:
            data['sha'] = sha
            
        response = requests.put(url, headers=self.headers, json=data)
        return response.status_code == 200

    def sync_trades_to_github(self, trades):
        """Sync trades data to GitHub repository"""
        if not self.token:
            return False
        
        try:
            # Create trades data structure
            trades_data = {
                'last_sync': datetime.utcnow().isoformat(),
                'trades': [trade.to_dict() for trade in trades]
            }
            
            return self.update_file_content('trades.json', trades_data, f'Update trades data - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        except Exception as e:
            print(f"Error syncing to GitHub: {e}")
            return False

    def sync_trades_from_github(self):
        """Sync trades data from GitHub repository"""
        if not self.token:
            return []
        
        try:
            trades_data = self.get_file_content('trades.json')
            if trades_data and 'trades' in trades_data:
                return trades_data['trades']
        except Exception as e:
            print(f"Error syncing from GitHub: {e}")
        
        return []

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/github-auth')
def github_auth():
    """Initiate GitHub OAuth flow"""
    if not GITHUB_CLIENT_ID:
        flash('GitHub OAuth not configured')
        return redirect(url_for('dashboard'))
    
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo"
    return redirect(github_auth_url)

@app.route('/github-callback')
@login_required
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get('code')
    if not code:
        flash('GitHub authorization failed')
        return redirect(url_for('dashboard'))
    
    # Exchange code for access token
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    
    response = requests.post(token_url, data=token_data, headers={'Accept': 'application/json'})
    if response.status_code == 200:
        token = response.json().get('access_token')
        if token:
            current_user.github_token = token
            db.session.commit()
            flash('GitHub integration successful!')
        else:
            flash('Failed to get GitHub access token')
    else:
        flash('GitHub authorization failed')
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.entry_date.desc()).all()
    
    # Calculate portfolio summary
    closed_trades = [t for t in trades if t.status == 'closed']
    open_trades = [t for t in trades if t.status == 'open']
    
    total_capital = 10000  # Default, should be configurable
    realized_pnl = sum(t.pnl for t in closed_trades)
    open_positions = len(open_trades)
    
    # Calculate analytics
    win_rate = 0
    avg_win = 0
    avg_loss = 0
    profit_factor = 0
    
    if closed_trades:
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl < 0]
        
        win_rate = (len(winning_trades) / len(closed_trades)) * 100
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = abs(sum(t.pnl for t in losing_trades) / len(losing_trades)) if losing_trades else 0
        
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf') if total_wins > 0 else 0
    
    portfolio_summary = {
        'total_capital': total_capital,
        'realized_pnl': realized_pnl,
        'open_positions': open_positions,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor
    }
    
    return render_template('dashboard.html', trades=trades, portfolio_summary=portfolio_summary)

# API Routes
@app.route('/api/trades', methods=['GET'])
@login_required
def get_trades():
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.entry_date.desc()).all()
    return jsonify([trade.to_dict() for trade in trades])

@app.route('/api/trades', methods=['POST'])
@login_required
def create_trade():
    data = request.get_json()
    
    trade = Trade(
        user_id=current_user.id,
        ticker=data['ticker'].upper(),
        trade_type=data['trade_type'],
        entry_date=datetime.strptime(data['entry_date'], '%Y-%m-%d').date(),
        entry_price=float(data['entry_price']),
        strike_price=float(data['strike_price']) if data.get('strike_price') else None,
        expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d').date() if data.get('expiration_date') else None,
        quantity=int(data['quantity']),
        entry_reason=data['entry_reason'],
        exit_date=datetime.strptime(data['exit_date'], '%Y-%m-%d').date() if data.get('exit_date') else None,
        exit_price=float(data['exit_price']) if data.get('exit_price') else None,
        exit_reason=data.get('exit_reason'),
        notes=data.get('notes'),
        status='closed' if data.get('exit_date') else 'open'
    )
    
    trade.pnl = trade.calculate_pnl()
    
    db.session.add(trade)
    db.session.commit()
    
    # Sync to GitHub if token is available
    if current_user.github_token:
        github_api = GitHubAPI(current_user.github_token)
        all_trades = Trade.query.filter_by(user_id=current_user.id).all()
        github_api.sync_trades_to_github(all_trades)
    
    return jsonify(trade.to_dict()), 201

@app.route('/api/trades/<int:trade_id>', methods=['PUT'])
@login_required
def update_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first()
    if not trade:
        return jsonify({'error': 'Trade not found'}), 404
    
    data = request.get_json()
    
    # Update trade fields
    for field in ['ticker', 'trade_type', 'entry_reason', 'exit_reason', 'notes']:
        if field in data:
            setattr(trade, field, data[field])
    
    for field in ['entry_price', 'strike_price', 'exit_price', 'quantity']:
        if field in data and data[field] is not None:
            setattr(trade, field, float(data[field]))
    
    for field in ['entry_date', 'expiration_date', 'exit_date']:
        if field in data and data[field]:
            setattr(trade, field, datetime.strptime(data[field], '%Y-%m-%d').date())
    
    if 'exit_date' in data:
        trade.status = 'closed' if data['exit_date'] else 'open'
    
    trade.pnl = trade.calculate_pnl()
    trade.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Sync to GitHub if token is available
    if current_user.github_token:
        github_api = GitHubAPI(current_user.github_token)
        all_trades = Trade.query.filter_by(user_id=current_user.id).all()
        github_api.sync_trades_to_github(all_trades)
    
    return jsonify(trade.to_dict())

@app.route('/api/trades/<int:trade_id>', methods=['DELETE'])
@login_required
def delete_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first()
    if not trade:
        return jsonify({'error': 'Trade not found'}), 404
    
    db.session.delete(trade)
    db.session.commit()
    
    # Sync to GitHub if token is available
    if current_user.github_token:
        github_api = GitHubAPI(current_user.github_token)
        all_trades = Trade.query.filter_by(user_id=current_user.id).all()
        github_api.sync_trades_to_github(all_trades)
    
    return jsonify({'message': 'Trade deleted successfully'})

@app.route('/api/sync-github', methods=['POST'])
@login_required
def sync_github():
    if not current_user.github_token:
        return jsonify({'error': 'GitHub not connected'}), 400
    
    github_api = GitHubAPI(current_user.github_token)
    
    # Sync trades to GitHub
    all_trades = Trade.query.filter_by(user_id=current_user.id).all()
    success = github_api.sync_trades_to_github(all_trades)
    
    if success:
        return jsonify({'message': 'Successfully synced to GitHub'})
    else:
        return jsonify({'error': 'Failed to sync to GitHub'}), 500

@app.route('/api/sync-from-github', methods=['POST'])
@login_required
def sync_from_github():
    if not current_user.github_token:
        return jsonify({'error': 'GitHub not connected'}), 400
    
    github_api = GitHubAPI(current_user.github_token)
    github_trades = github_api.sync_trades_from_github()
    
    if github_trades:
        # Clear existing trades and import from GitHub
        Trade.query.filter_by(user_id=current_user.id).delete()
        
        for trade_data in github_trades:
            trade = Trade(
                user_id=current_user.id,
                ticker=trade_data['ticker'],
                trade_type=trade_data['trade_type'],
                entry_date=datetime.strptime(trade_data['entry_date'], '%Y-%m-%d').date(),
                entry_price=trade_data['entry_price'],
                strike_price=trade_data.get('strike_price'),
                expiration_date=datetime.strptime(trade_data['expiration_date'], '%Y-%m-%d').date() if trade_data.get('expiration_date') else None,
                quantity=trade_data['quantity'],
                entry_reason=trade_data['entry_reason'],
                exit_date=datetime.strptime(trade_data['exit_date'], '%Y-%m-%d').date() if trade_data.get('exit_date') else None,
                exit_price=trade_data.get('exit_price'),
                exit_reason=trade_data.get('exit_reason'),
                notes=trade_data.get('notes'),
                status=trade_data['status'],
                pnl=trade_data.get('pnl', 0)
            )
            db.session.add(trade)
        
        db.session.commit()
        return jsonify({'message': f'Successfully imported {len(github_trades)} trades from GitHub'})
    else:
        return jsonify({'error': 'Failed to sync from GitHub'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)