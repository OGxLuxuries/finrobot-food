import blpapi
import time
from datetime import datetime
import os
import json

class BloombergMarketNews:
    def __init__(self):
        self.session = None
        self.output_dir = os.path.join(os.path.dirname(__file__), "market_news_output")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def start(self):
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost("localhost")
        sessionOptions.setServerPort(8194)
        sessionOptions.setMaxEventQueueSize(10000)

        self.session = blpapi.Session(sessionOptions, self.processEvent)
        
        if not self.session.start():
            print("Failed to start session.")
            return False
            
        if not self.session.openService("//blp/mktdata"):
            print("Failed to open market data service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for market data and news"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to AAPL news and data
        fields = [
            "LAST_PRICE",
            "NEWS_HEADLINES",
            "NEWS_STORY",
            "VOLUME",
            "BID",
            "ASK"
        ]
        
        securities = [
            "AAPL US Equity",
            "MSFT US Equity",
            "GOOGL US Equity"
        ]
        
        for security in securities:
            correlationId = blpapi.CorrelationId(security)
            subscriptions.add(
                topic=security,
                fields=fields,
                correlationId=correlationId
            )

        self.session.subscribe(subscriptions)

    def processEvent(self, event, session):
        try:
            if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                self._handleDataEvent(event)
            elif event.eventType() == blpapi.Event.SUBSCRIPTION_STATUS:
                self._handleStatusEvent(event)
            else:
                self._handleOtherEvent(event)
        except Exception as e:
            print(f"Error processing event: {e}")
        return True

    def _handleDataEvent(self, event):
        """Handle market data and news updates"""
        for msg in event:
            security = msg.correlationId().value()
            if msg.hasElement("NEWS_HEADLINES") or msg.hasElement("NEWS_STORY"):
                self._processNewsMessage(msg, security)
            else:
                self._processMarketDataMessage(msg, security)

    def _processNewsMessage(self, msg, security):
        """Process and save news message"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        news_data = {
            "security": security,
            "timestamp": timestamp,
            "type": "news",
            "data": {}
        }
        
        if msg.hasElement("NEWS_HEADLINES"):
            news_data["data"]["headlines"] = msg.getElement("NEWS_HEADLINES").getValueAsString()
            
        if msg.hasElement("NEWS_STORY"):
            news_data["data"]["story"] = msg.getElement("NEWS_STORY").getValueAsString()
        
        filename = os.path.join(self.output_dir, f"market_news_{security}_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        # Print to console
        print(f"\n=== News Update for {security} ===")
        print(f"Time: {timestamp}")
        
        if msg.hasElement("NEWS_HEADLINES"):
            print(f"Headline: {news_data['data']['headlines']}")
            
        if msg.hasElement("NEWS_STORY"):
            print(f"Story: {news_data['data']['story']}")
        
        print("========================")

    def _processMarketDataMessage(self, msg, security):
        """Process and save market data message"""
        if msg.hasElement("LAST_PRICE"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            market_data = {
                "security": security,
                "timestamp": timestamp,
                "data": {
                    "last_price": msg.getElementAsFloat("LAST_PRICE")
                }
            }
            
            if msg.hasElement("VOLUME"):
                market_data["data"]["volume"] = msg.getElementAsFloat("VOLUME")
            if msg.hasElement("BID"):
                market_data["data"]["bid"] = msg.getElementAsFloat("BID")
            if msg.hasElement("ASK"):
                market_data["data"]["ask"] = msg.getElementAsFloat("ASK")
            
            # Save to JSON file
            filename = os.path.join(self.output_dir, f"market_{security}_{timestamp}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(market_data, f, indent=2)
            
            print(f"\n=== Market Data for {security} ===")
            print(f"Time: {timestamp}")
            for key, value in market_data["data"].items():
                print(f"{key.title()}: {value}")
            print("========================")

    def _handleStatusEvent(self, event):
        """Handle subscription status"""
        for msg in event:
            if msg.messageType() == blpapi.Names.SUBSCRIPTION_FAILURE:
                print(f"Subscription failed: {msg}")
            elif msg.messageType() == blpapi.Names.SUBSCRIPTION_TERMINATED:
                print(f"Subscription terminated: {msg}")

    def _handleOtherEvent(self, event):
        """Handle other events"""
        for msg in event:
            if msg.messageType() == blpapi.Names.SESSION_TERMINATED:
                print("Session terminated")
                return False
        return True

def main():
    feed = BloombergMarketNews()
    
    if not feed.start():
        return
    
    feed.subscribe()
    
    try:
        print("\nSubscribed to market data and news. Press Ctrl+C to exit.")
        print("Monitoring AAPL, MSFT, and GOOGL for price updates and news...\n")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()

if __name__ == "__main__":
    main() 