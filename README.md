# StockTwits Watcher Counter

This script scrapes the number of watchers for specified stocks from StockTwits.com and exports the data in multiple formats.

## Prerequisites

- Python 3.x
- Google Chrome browser
- Internet connection

## Installation

1. Clone this repository or download the files
2. Install the required Python packages:
```sh

pip install -r requirements.txt
```

## Dependencies

The following Python packages are required:
- selenium (>=4.15.2): For web automation
- beautifulsoup4 (>=4.12.2): For HTML parsing
- pandas (>=2.1.3): For data manipulation and export
- openpyxl (>=3.1.2): For Excel file export
- webdriver-manager (>=4.0.1): For Chrome driver management
- requests (>=2.31.0): For HTTP requests

## Project Structure


## Usage

Run the script using Python:

```sh

python stocktwits.py
```
## Features

- Scrapes watcher counts for 38 predefined stocks
- Handles rate limiting with automatic retries
- Exports data in multiple formats (CSV, Excel, JSON)
- Comprehensive logging system
- Progress tracking in console
- Automatic file organization with timestamps

## Output Files

The script creates a `stock_data` directory containing:
1. CSV file: `stocktwits_watchers_[timestamp].csv`
2. Excel file: `stocktwits_watchers_[timestamp].xlsx`
3. JSON file: `stocktwits_watchers_[timestamp].json`

Additionally, a `stocktwits_scraper.log` file is created in the root directory for logging.

## Tracked Stocks

The script tracks the following stocks:
- MSFT, AAPL, CRM, CRWD, GOOGL
- CYBR, NVDA, LMT, SHLD, WWD (SHLD breaks, but you'll see error handling)
- LYB, HON, HTHIY, WM, V
- FISI, JPM, MA, AXP, EW
- XLV, NVO, WMT, COKE, DIS
- AMZN, GM, DAL, TSLA, DFH
- DLR, STAG, AMT, NTSX, CPK
- GEV, NETZ, GLD

## Error Handling

- Implements retry mechanism with exponential backoff
- Maximum 3 retry attempts per stock
- Logs all errors to `stocktwits_scraper.log`
- Continues processing remaining stocks if one fails

## Logging

The script logs:
- Processing status for each stock
- Number of watchers found
- Any errors or retry attempts
- Export status for each file format

## Notes

- The script uses Chrome in headless mode
- Timestamps are in local time zone
- Data is sorted by watcher count in descending order in the final display

## Troubleshooting

If you encounter issues:
1. Check `stocktwits_scraper.log` for error details
2. Ensure Chrome is installed and updated
3. Verify internet connection
4. Check if StockTwits.com is accessible
5. Ensure all dependencies are installed correctly

## License

This project is open source and available under the MIT License.
