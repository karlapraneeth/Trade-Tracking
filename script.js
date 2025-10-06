// Trade Tracker Application
class TradeTracker {
    constructor() {
        this.trades = this.loadTrades();
        this.settings = this.loadSettings();
        this.currentTab = 'add-trade';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updatePortfolioSummary();
        this.displayTrades();
        this.updateAnalytics();
        this.setCurrentDate();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Trade form submission
        document.getElementById('tradeForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTrade();
        });

        // Search functionality
        document.getElementById('searchTrades').addEventListener('input', (e) => {
            this.filterTrades();
        });

        // Status filter
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filterTrades();
        });

        // Settings
        document.getElementById('initialCapital').addEventListener('change', (e) => {
            this.updateSetting('initialCapital', parseFloat(e.target.value) || 0);
        });

        document.getElementById('riskPerTrade').addEventListener('change', (e) => {
            this.updateSetting('riskPerTrade', parseFloat(e.target.value) || 2);
        });
    }

    setCurrentDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('entryDate').value = today;
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.currentTab = tabName;

        // Update content based on tab
        if (tabName === 'trade-log') {
            this.displayTrades();
        } else if (tabName === 'analytics') {
            this.updateAnalytics();
        }
    }

    addTrade() {
        const formData = new FormData(document.getElementById('tradeForm'));
        const trade = {
            id: Date.now().toString(),
            ticker: formData.get('ticker').toUpperCase(),
            tradeType: formData.get('tradeType'),
            entryDate: formData.get('entryDate'),
            entryPrice: parseFloat(formData.get('entryPrice')),
            strikePrice: parseFloat(formData.get('strikePrice')) || null,
            expirationDate: formData.get('expirationDate') || null,
            quantity: parseInt(formData.get('quantity')),
            entryReason: formData.get('entryReason'),
            exitDate: formData.get('exitDate') || null,
            exitPrice: parseFloat(formData.get('exitPrice')) || null,
            exitReason: formData.get('exitReason') || null,
            notes: formData.get('notes') || null,
            createdAt: new Date().toISOString(),
            status: formData.get('exitDate') ? 'closed' : 'open'
        };

        // Calculate P&L if trade is closed
        if (trade.status === 'closed') {
            trade.pnl = this.calculatePnL(trade);
        }

        this.trades.push(trade);
        this.saveTrades();
        this.updatePortfolioSummary();
        this.displayTrades();
        this.updateAnalytics();
        this.clearForm();
        
        // Show success message
        this.showNotification('Trade added successfully!', 'success');
    }

    calculatePnL(trade) {
        if (!trade.exitPrice) return 0;
        return (trade.exitPrice - trade.entryPrice) * trade.quantity;
    }

    displayTrades() {
        const tradesList = document.getElementById('tradesList');
        const searchTerm = document.getElementById('searchTrades').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;

        let filteredTrades = this.trades.filter(trade => {
            const matchesSearch = trade.ticker.toLowerCase().includes(searchTerm) ||
                                trade.entryReason.toLowerCase().includes(searchTerm) ||
                                (trade.exitReason && trade.exitReason.toLowerCase().includes(searchTerm));
            
            const matchesStatus = statusFilter === 'all' || trade.status === statusFilter;
            
            return matchesSearch && matchesStatus;
        });

        // Sort by date (newest first)
        filteredTrades.sort((a, b) => new Date(b.entryDate) - new Date(a.entryDate));

        if (filteredTrades.length === 0) {
            tradesList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-chart-line"></i>
                    <h3>No trades found</h3>
                    <p>Start by adding your first trade or adjust your search criteria.</p>
                </div>
            `;
            return;
        }

        tradesList.innerHTML = filteredTrades.map(trade => this.createTradeCard(trade)).join('');
    }

    createTradeCard(trade) {
        const pnl = trade.pnl || 0;
        const pnlClass = pnl > 0 ? 'positive' : pnl < 0 ? 'negative' : '';
        const pnlDisplay = trade.status === 'closed' ? `$${pnl.toFixed(2)}` : 'Open';
        
        return `
            <div class="trade-card ${trade.status}">
                <div class="trade-header">
                    <div class="trade-symbol">${trade.ticker}</div>
                    <div class="trade-type">${trade.tradeType.replace('-', ' ')}</div>
                </div>
                <div class="trade-details">
                    <div class="detail-item">
                        <div class="detail-label">Entry Date</div>
                        <div class="detail-value">${this.formatDate(trade.entryDate)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Entry Price</div>
                        <div class="detail-value">$${trade.entryPrice.toFixed(2)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Quantity</div>
                        <div class="detail-value">${trade.quantity}</div>
                    </div>
                    ${trade.strikePrice ? `
                    <div class="detail-item">
                        <div class="detail-label">Strike Price</div>
                        <div class="detail-value">$${trade.strikePrice.toFixed(2)}</div>
                    </div>
                    ` : ''}
                    ${trade.expirationDate ? `
                    <div class="detail-item">
                        <div class="detail-label">Expiration</div>
                        <div class="detail-value">${this.formatDate(trade.expirationDate)}</div>
                    </div>
                    ` : ''}
                    ${trade.status === 'closed' ? `
                    <div class="detail-item">
                        <div class="detail-label">Exit Date</div>
                        <div class="detail-value">${this.formatDate(trade.exitDate)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Exit Price</div>
                        <div class="detail-value">$${trade.exitPrice.toFixed(2)}</div>
                    </div>
                    ` : ''}
                    <div class="detail-item">
                        <div class="detail-label">P&L</div>
                        <div class="detail-value pnl ${pnlClass}">${pnlDisplay}</div>
                    </div>
                </div>
                <div class="trade-reasons">
                    <div class="reason-section">
                        <strong>Entry Reason:</strong> ${trade.entryReason}
                    </div>
                    ${trade.exitReason ? `
                    <div class="reason-section">
                        <strong>Exit Reason:</strong> ${trade.exitReason}
                    </div>
                    ` : ''}
                    ${trade.notes ? `
                    <div class="reason-section">
                        <strong>Notes:</strong> ${trade.notes}
                    </div>
                    ` : ''}
                </div>
                <div class="trade-actions">
                    ${trade.status === 'open' ? `
                    <button class="btn btn-primary btn-small" onclick="tradeTracker.closeTrade('${trade.id}')">
                        <i class="fas fa-times"></i> Close Trade
                    </button>
                    ` : ''}
                    <button class="btn btn-secondary btn-small" onclick="tradeTracker.editTrade('${trade.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger btn-small" onclick="tradeTracker.deleteTrade('${trade.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }

    closeTrade(tradeId) {
        const trade = this.trades.find(t => t.id === tradeId);
        if (!trade) return;

        const exitPrice = prompt('Enter exit price:');
        if (exitPrice === null) return;

        const exitDate = prompt('Enter exit date (YYYY-MM-DD) or leave blank for today:');
        
        trade.exitPrice = parseFloat(exitPrice);
        trade.exitDate = exitDate || new Date().toISOString().split('T')[0];
        trade.exitReason = prompt('Enter exit reason:') || '';
        trade.status = 'closed';
        trade.pnl = this.calculatePnL(trade);

        this.saveTrades();
        this.updatePortfolioSummary();
        this.displayTrades();
        this.updateAnalytics();
        this.showNotification('Trade closed successfully!', 'success');
    }

    editTrade(tradeId) {
        const trade = this.trades.find(t => t.id === tradeId);
        if (!trade) return;

        // Populate form with trade data
        Object.keys(trade).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.value = trade[key] || '';
            }
        });

        // Switch to add trade tab
        this.switchTab('add-trade');
        
        // Add edit mode indicator
        const form = document.getElementById('tradeForm');
        form.dataset.editMode = tradeId;
        
        // Change submit button text
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-save"></i> Update Trade';
    }

    deleteTrade(tradeId) {
        if (!confirm('Are you sure you want to delete this trade?')) return;

        this.trades = this.trades.filter(t => t.id !== tradeId);
        this.saveTrades();
        this.updatePortfolioSummary();
        this.displayTrades();
        this.updateAnalytics();
        this.showNotification('Trade deleted successfully!', 'success');
    }

    filterTrades() {
        this.displayTrades();
    }

    updatePortfolioSummary() {
        const totalCapital = this.settings.initialCapital || 0;
        const closedTrades = this.trades.filter(t => t.status === 'closed');
        const openTrades = this.trades.filter(t => t.status === 'open');
        
        const realizedPnL = closedTrades.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
        const openPositions = openTrades.length;

        document.getElementById('totalCapital').textContent = `$${totalCapital.toFixed(2)}`;
        document.getElementById('realizedPnL').textContent = `$${realizedPnL.toFixed(2)}`;
        document.getElementById('openPositions').textContent = openPositions.toString();

        // Update P&L color
        const pnlElement = document.getElementById('realizedPnL');
        pnlElement.className = realizedPnL >= 0 ? 'positive' : 'negative';
    }

    updateAnalytics() {
        const closedTrades = this.trades.filter(t => t.status === 'closed');
        
        if (closedTrades.length === 0) {
            document.getElementById('winRate').textContent = '0%';
            document.getElementById('avgWin').textContent = '$0.00';
            document.getElementById('avgLoss').textContent = '$0.00';
            document.getElementById('profitFactor').textContent = '0.00';
            return;
        }

        const winningTrades = closedTrades.filter(t => (t.pnl || 0) > 0);
        const losingTrades = closedTrades.filter(t => (t.pnl || 0) < 0);
        
        const winRate = (winningTrades.length / closedTrades.length) * 100;
        const avgWin = winningTrades.length > 0 ? 
            winningTrades.reduce((sum, t) => sum + (t.pnl || 0), 0) / winningTrades.length : 0;
        const avgLoss = losingTrades.length > 0 ? 
            Math.abs(losingTrades.reduce((sum, t) => sum + (t.pnl || 0), 0) / losingTrades.length) : 0;
        
        const totalWins = winningTrades.reduce((sum, t) => sum + (t.pnl || 0), 0);
        const totalLosses = Math.abs(losingTrades.reduce((sum, t) => sum + (t.pnl || 0), 0));
        const profitFactor = totalLosses > 0 ? totalWins / totalLosses : totalWins > 0 ? '∞' : 0;

        document.getElementById('winRate').textContent = `${winRate.toFixed(1)}%`;
        document.getElementById('avgWin').textContent = `$${avgWin.toFixed(2)}`;
        document.getElementById('avgLoss').textContent = `$${avgLoss.toFixed(2)}`;
        document.getElementById('profitFactor').textContent = profitFactor.toString();
    }

    clearForm() {
        document.getElementById('tradeForm').reset();
        this.setCurrentDate();
        
        // Remove edit mode
        const form = document.getElementById('tradeForm');
        delete form.dataset.editMode;
        
        // Reset submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-save"></i> Save Trade';
    }

    exportTrades() {
        const dataStr = JSON.stringify(this.trades, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `trades-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }

    exportAllData() {
        const allData = {
            trades: this.trades,
            settings: this.settings,
            exportDate: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(allData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `trade-tracker-backup-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }

    importData() {
        document.getElementById('importFile').click();
    }

    handleFileImport(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                
                if (data.trades) {
                    this.trades = data.trades;
                    this.saveTrades();
                }
                
                if (data.settings) {
                    this.settings = { ...this.settings, ...data.settings };
                    this.saveSettings();
                }
                
                this.updatePortfolioSummary();
                this.displayTrades();
                this.updateAnalytics();
                this.showNotification('Data imported successfully!', 'success');
            } catch (error) {
                this.showNotification('Error importing data. Please check file format.', 'error');
            }
        };
        reader.readAsText(file);
    }

    clearAllData() {
        if (!confirm('Are you sure you want to clear all data? This action cannot be undone.')) return;
        
        this.trades = [];
        this.settings = { initialCapital: 0, riskPerTrade: 2 };
        this.saveTrades();
        this.saveSettings();
        this.updatePortfolioSummary();
        this.displayTrades();
        this.updateAnalytics();
        this.showNotification('All data cleared!', 'success');
    }

    updateSetting(key, value) {
        this.settings[key] = value;
        this.saveSettings();
        this.updatePortfolioSummary();
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // Data persistence methods
    saveTrades() {
        localStorage.setItem('tradeTracker_trades', JSON.stringify(this.trades));
    }

    loadTrades() {
        const saved = localStorage.getItem('tradeTracker_trades');
        return saved ? JSON.parse(saved) : [];
    }

    saveSettings() {
        localStorage.setItem('tradeTracker_settings', JSON.stringify(this.settings));
    }

    loadSettings() {
        const saved = localStorage.getItem('tradeTracker_settings');
        return saved ? JSON.parse(saved) : { initialCapital: 0, riskPerTrade: 2 };
    }
}

// Global functions for HTML onclick handlers
function clearForm() {
    tradeTracker.clearForm();
}

function exportTrades() {
    tradeTracker.exportTrades();
}

function exportAllData() {
    tradeTracker.exportAllData();
}

function importData() {
    tradeTracker.importData();
}

function handleFileImport(event) {
    tradeTracker.handleFileImport(event);
}

function clearAllData() {
    tradeTracker.clearAllData();
}

// Initialize the application
let tradeTracker;
document.addEventListener('DOMContentLoaded', () => {
    tradeTracker = new TradeTracker();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .trade-reasons {
        margin: 15px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .reason-section {
        margin-bottom: 10px;
    }
    
    .reason-section:last-child {
        margin-bottom: 0;
    }
    
    .reason-section strong {
        color: #2c3e50;
        margin-right: 8px;
    }
`;
document.head.appendChild(style);