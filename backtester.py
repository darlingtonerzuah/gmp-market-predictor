import sqlite3
import pandas as pd
import numpy as np
from predictor import predict_price
from predictor_arima import predict_arima

def get_historical_predictions(symbol, days=7):
    """Get past predictions and actual prices"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    
    # Get historical data
    query = """
        SELECT price, timestamp FROM stock_history 
        WHERE symbol = ? 
        ORDER BY timestamp ASC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(symbol, days))
    conn.close()
    
    if len(df) < 5:
        return None
    
    results = []
    for i in range(5, len(df)):
        # Use data up to point i to predict point i+1
        past_data = df.iloc[:i]['price'].values
        actual = df.iloc[i]['price']
        
        # Simple LR prediction
        X = np.array(range(len(past_data))).reshape(-1, 1)
        y = past_data
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        predicted = model.predict(np.array([[len(past_data)]]))[0]
        
        error = abs(predicted - actual)
        percent_error = (error / actual * 100) if actual != 0 else 0
        
        results.append({
            'symbol': symbol,
            'actual': float(actual),
            'predicted': float(predicted),
            'error': float(error),
            'percent_error': float(percent_error)
        })
    
    return results

def calculate_accuracy(symbol):
    """Calculate overall model accuracy"""
    results = get_historical_predictions(symbol)
    
    if not results or len(results) == 0:
        return None
    
    errors = [r['percent_error'] for r in results]
    mean_error = np.mean(errors)
    accuracy = 100 - mean_error
    
    return {
        'symbol': symbol,
        'accuracy': float(max(0, accuracy)),
        'mean_error': float(mean_error),
        'predictions_tested': len(results)
    }

def get_all_accuracies():
    """Get accuracy for all stocks"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT symbol FROM stock_history')
    symbols = cursor.fetchall()
    conn.close()
    
    accuracies = []
    for (symbol,) in symbols:
        acc = calculate_accuracy(symbol)
        if acc:
            accuracies.append(acc)
    
    # Sort by accuracy descending
    return sorted(accuracies, key=lambda x: x['accuracy'], reverse=True)

if __name__ == "__main__":
    print("Running backtest...")
    accuracies = get_all_accuracies()
    
    if accuracies:
        print(f"\nModel Accuracy for {len(accuracies)} stocks:\n")
        print(f"{'Symbol':<10} {'Accuracy':<12} {'Mean Error %':<15} {'Tests':<10}")
        print("-" * 50)
        for acc in accuracies[:15]:
            print(f"{acc['symbol']:<10} {acc['accuracy']:<12.2f}% {acc['mean_error']:<15.2f}% {acc['predictions_tested']:<10}")
        
        avg_accuracy = np.mean([a['accuracy'] for a in accuracies])
        print(f"\nAverage Accuracy: {avg_accuracy:.2f}%")
    else:
        print("Not enough data for backtesting yet")