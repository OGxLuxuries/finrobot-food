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
            
        # Open news service with correct service name
        if not self.session.openService("//blp/newssvc"):
            print("Failed to open news service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for market data and news"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to AAPL market data
        market_correlationId = blpapi.CorrelationId("AAPL_MKT")
        subscriptions.add(
            topic="AAPL US Equity",
            correlationId=market_correlationId,
            fields=["LAST_PRICE", "BID", "ASK", "VOLUME"],
            options=None
        )

        # Subscribe to AAPL news with correct topic format
        news_correlationId = blpapi.CorrelationId("AAPL_NEWS")
        subscriptions.add(
            topic="NEWS_STORY_FILTER//AAPL US Equity",  # Updated news topic format
            correlationId=news_correlationId,
            fields=["STORY_TEXT", "HEADLINE", "TIME_STAMP"],  # Updated field names
            options=None
        )

        print("Subscribing to AAPL market data and news...")
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
            
            if security == "AAPL_MKT":
                self._handleMarketData(msg)
            elif security == "AAPL_NEWS":
                self._handleNewsData(msg)

    def _handleMarketData(self, msg):
        """Handle market data updates"""
        market_data = {
            "security": "AAPL",
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "type": "market_data",
            "data": {}
        }
        
        if msg.hasElement("LAST_PRICE"):
            market_data["data"]["last_price"] = msg.getElementAsFloat("LAST_PRICE")
        if msg.hasElement("BID"):
            market_data["data"]["bid"] = msg.getElementAsFloat("BID")
        if msg.hasElement("ASK"):
            market_data["data"]["ask"] = msg.getElementAsFloat("ASK")
        if msg.hasElement("VOLUME"):
            market_data["data"]["volume"] = msg.getElementAsInteger("VOLUME")
        
        filename = os.path.join(self.output_dir, f"market_data_AAPL_{market_data['timestamp']}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(market_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nMarket Data Update for AAPL:")
        print(f"Time: {market_data['timestamp']}")
        for key, value in market_data["data"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("========================")

    def _handleNewsData(self, msg):
        """Handle news updates"""
        if msg.hasElement("HEADLINE"):
            news_data = {
                "security": "AAPL",
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "type": "news",
                "data": {
                    "headline": msg.getElementAsString("HEADLINE"),
                    "story": msg.getElementAsString("STORY_TEXT") if msg.hasElement("STORY_TEXT") else "",
                    "time": msg.getElementAsString("TIME_STAMP") if msg.hasElement("TIME_STAMP") else ""
                }
            }
            
            filename = os.path.join(self.output_dir, f"news_AAPL_{news_data['timestamp']}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(news_data, f, indent=2, ensure_ascii=False)
            
            print(f"\nNews Update for AAPL:")
            print(f"Time: {news_data['timestamp']}")
            print(f"Headline: {news_data['data']['headline']}")
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
    feed = BloombergBasicFeed()
    
    if not feed.start():
        return
    
    feed.subscribe()
    
    try:
        print("\nSubscribed to AAPL market data and news. Press Ctrl+C to exit.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()
        feed.session.destroy()

if __name__ == "__main__":
    main() 