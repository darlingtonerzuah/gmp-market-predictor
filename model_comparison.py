import sqlite3
import pandas as pd
from predictor import predict_price
from predictor_arima import predict_arima

def compare_predictions(symbol):
    """Compare Linear Regression vs ARIMA for a stock"""
    lr_pred = predict_price(symbol)
    arima_pred = predict_arima(symbol)
    
    if not lr_pred or not arima_pred:
        return None
    
    return {
        'symbol': symbol,
        'current_price': lr_pred['current_price'],
        'lr_predicted': lr_pred['predicted_price'],
        'lr_change': lr_pred['percent_change'],
        'arima_predicted': arima_pred['predicted_price'],
        'arima_change': arima_pred['percent_change'],
        'data_points': lr_pred['data_points']
    }

def get_all_comparisons():
    """Get comparisons for all stocks"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT symbol FROM stock_history ORDER BY symbol')
    symbols = cursor.fetchall()
    conn.close()
    
    comparisons = []
    for (symbol,) in symbols:
        comp = compare_predictions(symbol)
        if comp:
            comparisons.append(comp)
    
    return comparisons

if __name__ == "__main__":
    print("Comparing models...")
    comps = get_all_comparisons()
    
    if comps:
        print(f"\nModel Comparison for {len(comps)} stocks:\n")
        print(f"{'Symbol':<10} {'Current':<10} {'LR Pred':<10} {'ARIMA Pred':<12} {'LR %':<8} {'ARIMA %':<8}")
        print("-" * 70)
        for comp in comps[:15]:
            print(f"{comp['symbol']:<10} {comp['current_price']:<10.2f} {comp['lr_predicted']:<10.2f} {comp['arima_predicted']:<12.2f} {comp['lr_change']:<8.2f}% {comp['arima_change']:<8.2f}%")
    else:
        print("Not enough data yet for comparison")