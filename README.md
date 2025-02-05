# BLPAPI Research for Automated Stock Trading Project
Bloomberg API for Python 

Resources gathered on this API. Only successful run was with a PC with Bloomberg Terminal Software. Currently looking into Bloomberg anywhere capabilities.

## Important Links
- [Bloomberg Data License API Code Samples](https://developer.bloomberg.com/portal/downloads?releaseStatus=current#data_license_rest_api_code_samples)
- [All BLPAPI Data Capabilities/Extraction](https://developer.bloomberg.com/portal/apis/blpapi?chapterId=5447&entityType=document#api_services-service_table) ⭐
- [BLPAPI Data Capabilities](https://developer.bloomberg.com/portal/apis/blpapi?chapterId=5400&entityType=document)
- [API Tutorials](https://developer.bloomberg.com/portal/tutorials)
- [BLPAPI Docs](https://bloomberg.github.io/blpapi-docs/python/3.24.11/index.html)
- [BLPAPI Developer Guide PDF](https://data.bloomberglp.com/professional/sites/10/2017/03/BLPAPI-Core-Developer-Guide.pdf)
- [Developer Portal](https://developer.bloomberg.com/portal/products?interfaces=bloomberg_api_blpapi)
- [Curated Bloomberg Twitter Feed](https://developer.bloomberg.com/portal/products/edf?chapterId=767&entityType=document)


## Demo | Twitter Feed and XML to JSON Converter

### Overview
This project consists of two scripts that work together to collect and process Bloomberg Twitter feed sentiment data for AAPL.

### Prerequisites:
- Bloomberg Terminal
- Python 3.x.x
- pip

## Dependencies
Ensure you have the required dependencies installed before running the scripts:
```sh
python -m pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple blpapi
pip install blpapi xmltodict
```

### Step 1: Run the Bloomberg Twitter Subscription Script
In the first terminal, execute the following command to start collecting Bloomberg Twitter feed data:
```sh
python bloomberg_twitter_feed.py
```
## Expected Output
Without authentication, we won't receive any Twitter feed data at all - the subscription will fail with the PERMISSION_ERROR we saw.
With proper authentication, we'll receive Twitter feed data in this structure:
```
{
  "security": "twitter_feed",
  "timestamp": "20240204_234823",
  "type": "social",
  "data": {
    "tweet": {
      "body": "The actual tweet text content",
      "url": "https://twitter.com/username/status/123456789",
      "language": "EN"
    },
    "user": {
      "handle": "@username",
      "followers": 50000,
      "lists": 100,
      "tweets": 5000
    },
    "metadata": {
      "assigned_topics": ["TECH", "MARKETS"],
      "derived_topics": ["EARNINGS", "PRODUCTS"],
      "assigned_tickers": ["AAPL US Equity"],
      "derived_tickers": ["MSFT US Equity"]
    }
  }
}

```
### Step 2: Run the Bloomberg SPY, DJI, and Something Else Subscription Script
In the second  terminal, execute the following command to start collecting Bloomberg Twitter feed data:
```sh
python bloomberg_index_feed.py
```

### Step 3: Run the Bloomberg General Market News Subscription Script
In the third terminal, execute the following command to start collecting Bloomberg Twitter feed data:
```sh
python bloomberg_market_feed.py
```


## Functionality
- Subscribes to Bloomberg Twitter feed and sentiment data for AAPL.
- Saves incoming data as XML files.
- Automatically converts new XML files to JSON format.
- Stores JSON files in a `json_output` directory.

## Key Features
- Real-time data processing
- Automatic file conversion
- Error handling
- Clean shutdown on `Ctrl+C`
- Separation of concerns between data collection and conversion



## Important Notes
- Proper Bloomberg credentials and permissions are required to access the Twitter feed and sentiment data services.

