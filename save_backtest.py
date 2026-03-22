import sqlite3
from backtester import get_all_accuracies

def save_backtests():
    """Save backtest results to database"""
    accuracies = get_all_accuracies()
    
    if not accuracies:
        print("No backtest results")
        return
    
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY,
            symbol TEXT UNIQUE,
            accuracy REAL,
            mean_error REAL,
            predictions_tested INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    for acc in accuracies:
        cursor.execute('''
            INSERT OR REPLACE INTO backtest_results 
            (symbol, accuracy, mean_error, predictions_tested)
            VALUES (?, ?, ?, ?)
        ''', (
            acc['symbol'],
            acc['accuracy'],
            acc['mean_error'],
            acc['predictions_tested']
        ))
    
    conn.commit()
    conn.close()
    print(f"Saved backtest results for {len(accuracies)} stocks")

if __name__ == "__main__":
    save_backtests()