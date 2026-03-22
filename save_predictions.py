import sqlite3
from predictor import get_all_predictions
from datetime import datetime

def create_predictions_table():
    """Create table for predictions"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            current_price REAL,
            predicted_price REAL,
            change REAL,
            percent_change REAL,
            data_points INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Predictions table created!")

def save_predictions():
    """Generate and save predictions"""
    predictions = get_all_predictions()
    
    if not predictions:
        print("No predictions generated")
        return
    
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    
    for pred in predictions:
        cursor.execute('''
            INSERT INTO predictions 
            (symbol, current_price, predicted_price, change, percent_change, data_points)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            pred['symbol'],
            pred['current_price'],
            pred['predicted_price'],
            pred['change'],
            pred['percent_change'],
            pred['data_points']
        ))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(predictions)} predictions at {datetime.now()}")

if __name__ == "__main__":
    create_predictions_table()
    save_predictions()