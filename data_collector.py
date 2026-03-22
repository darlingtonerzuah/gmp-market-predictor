import sqlite3
from datetime import datetime
import time

def create_historical_table():
    """Create table for historical stock data"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Historical table created!")

def save_historical_data():
    """Save historical data from current stocks"""
    print(f"[{datetime.now()}] Collecting data...")
    
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    
    # Get current stocks from main table
    cursor.execute('SELECT symbol, close_price FROM stocks')
    stocks = cursor.fetchall()
    
    # Save each stock's closing price to history
    for symbol, price in stocks:
        try:
            cursor.execute('''
                INSERT INTO stock_history (symbol, price, timestamp)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (symbol, price))
        except:
            pass
    
    conn.commit()
    conn.close()
    print(f"Saved {len(stocks)} data points")

if __name__ == "__main__":
    create_historical_table()
    
    # Collect data every 60 seconds for demo
    print("Starting data collection. Press Ctrl+C to stop...")
    try:
        while True:
            save_historical_data()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nData collection stopped.")