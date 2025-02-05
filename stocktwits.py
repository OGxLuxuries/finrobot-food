import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import os
import sys
import re
import requests
import json
from datetime import datetime
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stocktwits_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create a sample CSV file with some stock symbols first
stock_data = {
    'Symbol': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
}
df = pd.DataFrame(stock_data)
df.to_csv('Stock_indices_NASDAQ.csv', index=False)

# Now read the CSV file
csvfile = pd.read_csv('Stock_indices_NASDAQ.csv')
listOfStocks = csvfile["Symbol"]
listOfStocks_A = listOfStocks[0:5]
listOfStocks_B = listOfStocks[21:41]

# Initiating the dictionary with its column names
dict_stocks = {}
dict_stocks['Symbol'] = []
dict_stocks['Watchers'] = []

def setup_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')  # Suppress console messages
    return webdriver.Chrome(options=chrome_options)

def find_n_watchers():
    stocks_list = [
        'MSFT', 'AAPL', 'CRM', 'CRWD', 'GOOGL', 'CYBR', 'NVDA', 'LMT', 'SHLD', 
        'WWD', 'LYB', 'HON', 'HTHIY', 'WM', 'V', 'FISI', 'JPM', 'MA', 'AXP', 
        'EW', 'XLV', 'NVO', 'WMT', 'COKE', 'DIS', 'AMZN', 'GM', 'DAL', 'TSLA',
        'DFH', 'DLR', 'STAG', 'AMT', 'NTSX', 'CPK', 'GEV', 'NETZ', 'GLD'
    ]
    
    dict_stocks = {}
    driver = setup_chrome()
    retry_delay = 60  # Initial retry delay in seconds
    max_retries = 3
    
    try:
        for stock in stocks_list:
            retries = 0
            while retries < max_retries:
                try:
                    logging.info(f"Processing {stock}...")
                    url = f"https://stocktwits.com/symbol/{stock}"
                    driver.get(url)
                    time.sleep(3)  # Reduced initial wait time
                    
                    page_source = driver.page_source
                    json_match = re.search(r'"watchlistCount":(\d+)', page_source)
                    
                    if json_match:
                        watchers = int(json_match.group(1))
                        dict_stocks[stock] = watchers
                        logging.info(f"Found {watchers:,} watchers for {stock}")
                        break  # Success, move to next stock
                    else:
                        raise ValueError("Watchers count not found in page source")
                    
                except Exception as e:
                    retries += 1
                    if retries < max_retries:
                        wait_time = retry_delay * retries
                        logging.warning(f"Attempt {retries} failed for {stock}: {str(e)}")
                        logging.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        logging.error(f"Failed to get data for {stock} after {max_retries} attempts")
                
            time.sleep(2)  # Delay between stocks
            
    finally:
        driver.quit()
    
    return dict_stocks

def export_data(dict_stocks):
    if not dict_stocks:
        logging.error("No data to export")
        return
    
    # Create output directory if it doesn't exist
    output_dir = Path('stock_data')
    output_dir.mkdir(exist_ok=True)
    
    # Create DataFrame
    df = pd.DataFrame.from_dict(dict_stocks, orient='index', columns=['Watchers'])
    df.index.name = 'Symbol'
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export to multiple formats
    try:
        # CSV export
        csv_path = output_dir / f'stocktwits_watchers_{timestamp}.csv'
        df.to_csv(csv_path)
        logging.info(f"Data exported to CSV: {csv_path}")
        
        # Excel export
        excel_path = output_dir / f'stocktwits_watchers_{timestamp}.xlsx'
        df.to_excel(excel_path)
        logging.info(f"Data exported to Excel: {excel_path}")
        
        # JSON export
        json_path = output_dir / f'stocktwits_watchers_{timestamp}.json'
        df.to_json(json_path, indent=4, orient='index')
        logging.info(f"Data exported to JSON: {json_path}")
        
        # Display results
        print("\nFinal Results:")
        print(df.sort_values('Watchers', ascending=False))
        
    except Exception as e:
        logging.error(f"Error exporting data: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting StockTwits scraper...")
    dict_stocks = find_n_watchers()
    export_data(dict_stocks)
    logging.info("Scraping completed!")




