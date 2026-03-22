from exporter import export_stocks_to_csv, export_predictions_to_csv
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_stocks():
    """Fetch all stocks from database"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks ORDER BY symbol')
        stocks = cursor.fetchall()
        conn.close()
        return [dict(stock) for stock in stocks]
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/')
def index():
    """Display dashboard"""
    stocks = get_stocks()
    return render_template('index.html', stocks=stocks)

@app.route('/api/stocks')
def api_stocks():
    """API endpoint for stock data"""
    stocks = get_stocks()
    return jsonify(stocks)

@app.route('/api/predictions')
def api_predictions():
    """API endpoint for predictions"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions 
            ORDER BY percent_change DESC
        ''')
        predictions = cursor.fetchall()
        conn.close()
        return jsonify([dict(p) for p in predictions])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])
    
@app.route('/api/model-comparison')
def api_model_comparison():
    """API endpoint for model comparison"""
    try:
        from model_comparison import get_all_comparisons
        comps = get_all_comparisons()
        return jsonify(comps)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])
    
@app.route('/comparison')
def comparison():
    """Model comparison page"""
    return render_template('comparison.html')

@app.route('/api/backtest')
def api_backtest():
    """API endpoint for backtest results"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM backtest_results 
            ORDER BY accuracy DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        return jsonify([dict(r) for r in results])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])
    
@app.route('/api/stock-history/<symbol>')
def api_stock_history(symbol):
    """API endpoint for stock price history"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, timestamp FROM stock_history 
            WHERE symbol = ? 
            ORDER BY timestamp ASC
            LIMIT 100
        ''', (symbol,))
        rows = cursor.fetchall()
        conn.close()
        
        data = [{'time': row[1], 'price': row[0]} for row in rows]
        return jsonify(data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])
    
@app.route('/charts')
def charts():
    """Charts page"""
    return render_template('charts.html')

@app.route('/api/export/stocks')
def export_stocks():
    """Export stocks as CSV"""
    try:
        csv_data = export_stocks_to_csv()
        if not csv_data:
            return jsonify({'error': 'No data to export'}), 400
        
        return csv_data, 200, {
            'Content-Disposition': f'attachment; filename=stocks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/predictions')
def export_predictions():
    """Export predictions as CSV"""
    try:
        csv_data = export_predictions_to_csv()
        if not csv_data:
            return jsonify({'error': 'No data to export'}), 400
        
        return csv_data, 200, {
            'Content-Disposition': f'attachment; filename=predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat')
def chat():
    """Chat page"""
    return render_template('chat.html')

@app.route('/api/chat/messages')
def api_chat_messages():
    """Get all chat messages"""
    try:
        conn = sqlite3.connect('data/gmp_stocks.db')
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY,
                username TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        
        cursor.execute('SELECT username, message, timestamp FROM chat_messages ORDER BY timestamp DESC LIMIT 50')
        messages = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'username': msg[0] or 'Anonymous',
            'message': msg[1],
            'timestamp': msg[2]
        } for msg in reversed(messages)])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

@app.route('/api/chat/send', methods=['POST'])
def api_chat_send():
    """Send a chat message"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message or len(message) > 500:
            return jsonify({'error': 'Invalid message'}), 400
        
        conn = sqlite3.connect('data/gmp_stocks.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (username, message)
            VALUES (?, ?)
        ''', ('Trader', message))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

from groq_handler import groq_handler

if __name__ == '__main__':
    app.run(debug=True, port=5000)