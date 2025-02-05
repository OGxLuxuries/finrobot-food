# BLPAPI Research for Automated Stock Trading Project
Bloomberg API for Python 

Resources gathered on this API. Only successful run was with a PC with Bloomberg Terminal Software. Currently looking into Bloomberg anywhere capabilities.

## Important Links
- https://developer.bloomberg.com/portal/downloads?releaseStatus=current#data_license_rest_api_code_samples

- https://developer.bloomberg.com/portal/apis/blpapi?chapterId=5447&entityType=document#api_services-service_table (⭐)

- https://developer.bloomberg.com/portal/apis/blpapi?chapterId=5400&entityType=document

- https://developer.bloomberg.com/portal/tutorials

- https://bloomberg.github.io/blpapi-docs/python/3.24.11/index.html

- https://data.bloomberglp.com/professional/sites/10/2017/03/BLPAPI-Core-Developer-Guide.pdf

- https://developer.bloomberg.com/portal/products?interfaces=bloomberg_api_blpapi

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

### Step 1: Run the Bloomberg Subscription Script
In the first terminal, execute the following command to start collecting Bloomberg Twitter feed data:
```sh
python bloomberg_twitter_feed.py
```

### Step 2: Run the XML to JSON Converter
In another terminal, run the converter script to transform XML data into JSON format:
```sh
python xml_to_json_converter.py
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

