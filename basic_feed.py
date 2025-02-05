import blpapi
import time
from datetime import datetime
import os
import json

class BloombergBasicFeed:
    def __init__(self):
        self.session = None
        self.output_dir = os.path.join(os.path.dirname(__file__), "basic_feed_output")
        
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
            
        # Open market data service
        if not self.session.openService("//blp/mktdata"):
            print("Failed to open market data service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for market data and headlines"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to AAPL market data
        market_correlationId = blpapi.CorrelationId("AAPL_MKT")
        subscriptions.add(
            topic="AAPL US Equity",
            correlationId=market_correlationId,
            fields=["LAST_PRICE", "BID", "ASK", "VOLUME", "NEWS_HEADLINES"],  # Add NEWS_HEADLINES field
            options=None
        )

        print("Subscribing to AAPL market data...")
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
            try:
                if msg.hasElement("NEWS_HEADLINES"):
                    self._handleNewsData(msg)
                self._handleMarketData(msg)
            except Exception as e:
                print(f"Error processing event: {e}")

    def _handleMarketData(self, msg):
        """Handle market data updates"""
        try:
            market_data = {
                "security": "AAPL",
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "type": "market_data",
                "data": {}
            }
            
            for field in ["LAST_PRICE", "BID", "ASK", "VOLUME"]:
                if msg.hasElement(field):
                    element = msg.getElement(field)
                    if field == "VOLUME":
                        market_data["data"][field.lower()] = element.getValueAsInteger()
                    else:
                        market_data["data"][field.lower()] = element.getValueAsFloat()
            
            filename = os.path.join(self.output_dir, f"market_data_AAPL_{market_data['timestamp']}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(market_data, f, indent=2, ensure_ascii=False)
            
            if market_data["data"]:  # Only print if we have data
                print(f"\nMarket Data Update for AAPL:")
                print(f"Time: {market_data['timestamp']}")
                for key, value in market_data["data"].items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
                print("========================")
        except blpapi.Exception as e:
            print(f"Error processing market data: {e}")

    def _handleNewsData(self, msg):
        """Handle news updates"""
        try:
            if msg.hasElement("NEWS_HEADLINES"):
                news_data = {
                    "security": "AAPL",
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "type": "news",
                    "data": {
                        "headline": msg.getElement("NEWS_HEADLINES").getValueAsString()
                    }
                }
                
                filename = os.path.join(self.output_dir, f"news_AAPL_{news_data['timestamp']}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(news_data, f, indent=2, ensure_ascii=False)
                
                print(f"\nNews Update for AAPL:")
                print(f"Time: {news_data['timestamp']}")
                print(f"Headline: {news_data['data']['headline']}")
                print("========================")
        except blpapi.Exception as e:
            print(f"Error processing news: {e}")

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
    feed = BloombergBasicFeed()
    
    if not feed.start():
        return
    
    feed.subscribe()
    
    try:
        print("\nSubscribed to AAPL market data. Press Ctrl+C to exit.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()
        feed.session.destroy()

if __name__ == "__main__":
    main() 