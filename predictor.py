import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import json

def get_stock_history(symbol, days=30):
    """Get historical data for a stock"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    query = f"""
        SELECT price, timestamp FROM stock_history 
        WHERE symbol = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(symbol, days))
    conn.close()
    return df

def predict_price(symbol):
    """Predict next price for a stock using Linear Regression"""
    try:
        df = get_stock_history(symbol)
        
        if len(df) < 3:
            return None
        
        # Prepare data
        df = df.iloc[::-1].reset_index(drop=True)
        X = np.array(range(len(df))).reshape(-1, 1)
        y = df['price'].values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next day
        next_day = np.array([[len(df)]])
        predicted_price = model.predict(next_day)[0]
        
        # Calculate trend
        current_price = y[-1]
        change = predicted_price - current_price
        percent_change = (change / current_price * 100) if current_price != 0 else 0
        
        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'predicted_price': float(predicted_price),
            'change': float(change),
            'percent_change': float(percent_change),
            'data_points': len(df)
        }
    except Exception as e:
        print(f"Error predicting {symbol}: {e}")
        return None

def get_all_predictions():
    """Get predictions for all stocks"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT symbol FROM stock_history')
    symbols = cursor.fetchall()
    conn.close()
    
    predictions = []
    for (symbol,) in symbols:
        pred = predict_price(symbol)
        if pred:
            predictions.append(pred)
    
    return predictions

if __name__ == "__main__":
    print("Generating predictions...")
    predictions = get_all_predictions()
    
    if predictions:
        print(f"\nPredictions for {len(predictions)} stocks:\n")
        for pred in predictions[:10]:  # Show first 10
            print(f"{pred['symbol']}: {pred['current_price']:.2f} → {pred['predicted_price']:.2f} ({pred['percent_change']:+.2f}%)")
    else:
        print("Not enough data yet. Wait for more collection...")