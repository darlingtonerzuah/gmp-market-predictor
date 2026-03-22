import sqlite3
from predictor_arima import get_all_arima_predictions
from datetime import datetime

def save_arima_predictions():
    """Generate and save ARIMA predictions"""
    predictions = get_all_arima_predictions()
    
    if not predictions:
        print("No ARIMA predictions generated yet")
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
    print(f"Saved {len(predictions)} ARIMA predictions at {datetime.now()}")

if __name__ == "__main__":
    save_arima_predictions()