import sqlite3
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

def get_stock_history(symbol, days=30):
    """Get historical data for a stock"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    query = f"""
        SELECT price, timestamp FROM stock_history 
        WHERE symbol = ? 
        ORDER BY timestamp ASC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(symbol, days))
    conn.close()
    return df

def predict_arima(symbol):
    """Predict using ARIMA model"""
    try:
        df = get_stock_history(symbol)
        
        if len(df) < 5:  # Need at least 5 data points
            return None
        
        prices = df['price'].values
        
        # Handle zero/constant prices
        if len(np.unique(prices)) == 1:
            return None
        
        try:
            # Fit ARIMA(1,1,1) - simple but effective
            model = ARIMA(prices, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Predict next value
            forecast = fitted_model.get_forecast(steps=1)
            predicted_price = forecast.predicted_mean.values[0]
            
            current_price = prices[-1]
            change = predicted_price - current_price
            percent_change = (change / current_price * 100) if current_price != 0 else 0
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'predicted_price': float(predicted_price),
                'change': float(change),
                'percent_change': float(percent_change),
                'data_points': len(prices),
                'model': 'ARIMA'
            }
        except:
            return None
            
    except Exception as e:
        print(f"Error with {symbol}: {e}")
        return None

def get_all_arima_predictions():
    """Get ARIMA predictions for all stocks"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT symbol FROM stock_history')
    symbols = cursor.fetchall()
    conn.close()
    
    predictions = []
    for (symbol,) in symbols:
        pred = predict_arima(symbol)
        if pred:
            predictions.append(pred)
    
    return predictions

if __name__ == "__main__":
    print("Generating ARIMA predictions...")
    predictions = get_all_arima_predictions()
    
    if predictions:
        print(f"\nARIMA Predictions for {len(predictions)} stocks:\n")
        for pred in predictions[:10]:
            print(f"{pred['symbol']}: {pred['current_price']:.2f} → {pred['predicted_price']:.2f} ({pred['percent_change']:+.2f}%)")
    else:
        print("Not enough data yet...")