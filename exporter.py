import sqlite3
import csv
from datetime import datetime
from io import StringIO

def export_stocks_to_csv():
    """Export current stocks to CSV"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks ORDER BY symbol')
        stocks = cursor.fetchall()
        conn.close()
        
        if not stocks:
            return None
        
        # Get column names
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(stocks)')
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        
        for stock in stocks:
            writer.writerow(stock)
        
        return output.getvalue()
    except Exception as e:
        print(f"Error: {e}")
        return None

def export_predictions_to_csv():
    """Export predictions to CSV"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM predictions ORDER BY symbol')
        preds = cursor.fetchall()
        conn.close()
        
        if not preds:
            return None
        
        # Get column names
        conn = sqlite3.connect('data/gmp_stocks.db')
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(predictions)')
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        
        for pred in preds:
            writer.writerow(pred)
        
        return output.getvalue()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    csv_data = export_stocks_to_csv()
    if csv_data:
        with open('stocks_export.csv', 'w') as f:
            f.write(csv_data)
        print("Exported to stocks_export.csv")