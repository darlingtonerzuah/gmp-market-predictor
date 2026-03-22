from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import sqlite3
import time
from datetime import datetime

def init_database():
    """Create SQLite database for storing stock data"""
    conn = sqlite3.connect('data/gse_stocks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY,
            symbol TEXT UNIQUE,
            bid_size INTEGER,
            bid_price REAL,
            ask_size INTEGER,
            ask_price REAL,
            last_trade_price REAL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            change REAL,
            percent_change REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def scrape_stocks():
    """Scrape GSE stocks and store in database"""
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        url = "https://gsemarketwatch.com"
        print(f"Loading {url}...")
        driver.get(url)
        
        print("Waiting for data to load...")
        time.sleep(8)
        
        # Find all table rows
        rows = driver.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} rows")
        
        stocks_data = []
        
        # Skip header row, extract data from remaining rows
        for row in rows[1:]:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 13:
                    stock = {
                        'symbol': cells[0].text,
                        'bid_size': cells[1].text,
                        'bid_price': cells[2].text,
                        'ask_size': cells[3].text,
                        'ask_price': cells[4].text,
                        'last_trade_price': cells[5].text,
                        'open_price': cells[6].text,
                        'high_price': cells[7].text,
                        'low_price': cells[8].text,
                        'close_price': cells[9].text,
                        'change': cells[10].text,
                        'percent_change': cells[11].text,
                    }
                    stocks_data.append(stock)
            except:
                pass
        
        driver.quit()
        print(f"\nExtracted {len(stocks_data)} stocks")
        
        # Store in database
        if stocks_data:
            store_stocks(stocks_data)
        
        return stocks_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def store_stocks(stocks_data):
    """Store stock data in SQLite"""
    conn = sqlite3.connect('data/gmp_stocks.db')
    cursor = conn.cursor()
    
    for stock in stocks_data:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO stocks 
                (symbol, bid_size, bid_price, ask_size, ask_price, last_trade_price,
                 open_price, high_price, low_price, close_price, change, percent_change)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock['symbol'],
                stock['bid_size'] if stock['bid_size'] else 0,
                float(stock['bid_price']) if stock['bid_price'] else 0,
                stock['ask_size'] if stock['ask_size'] else 0,
                float(stock['ask_price']) if stock['ask_price'] else 0,
                float(stock['last_trade_price']) if stock['last_trade_price'] else 0,
                float(stock['open_price']) if stock['open_price'] else 0,
                float(stock['high_price']) if stock['high_price'] else 0,
                float(stock['low_price']) if stock['low_price'] else 0,
                float(stock['close_price']) if stock['close_price'] else 0,
                float(stock['change']) if stock['change'] else 0,
                float(stock['percent_change']) if stock['percent_change'] else 0,
            ))
        except Exception as e:
            print(f"Error inserting {stock['symbol']}: {e}")
    
    conn.commit()
    conn.close()
    print("Data stored in database!")

if __name__ == "__main__":
    init_database()
    scrape_stocks()