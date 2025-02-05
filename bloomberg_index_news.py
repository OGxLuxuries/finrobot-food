import blpapi
import time
from datetime import datetime
import os
import json

class BloombergDowJonesNews:
    def __init__(self):
        self.session = None
        self.output_dir = os.path.join(os.path.dirname(__file__), "index_news_output")
        
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
        """Create and send subscription for Dow Jones news via market data"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to major indices to get their news
        securities = [
            "DJI Index",  # Dow Jones Industrial Average
            "INDU Index", # Bloomberg Dow Jones Industrial Index
            "SPX Index"   # S&P 500 for broader market news
        ]
        
        fields = [
            "LAST_PRICE",
            "NEWS_HEADLINES",
            "NEWS_STORY",
            "RT_NEWS_STORY",  # Real-time news
            "RT_NEWS_HEADLINE_ONLY"  # Real-time headlines
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
        """Handle news updates"""
        for msg in event:
            security = msg.correlationId().value()
            if (msg.hasElement("NEWS_HEADLINES") or 
                msg.hasElement("NEWS_STORY") or 
                msg.hasElement("RT_NEWS_STORY") or 
                msg.hasElement("RT_NEWS_HEADLINE_ONLY")):
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
            
        if msg.hasElement("RT_NEWS_STORY"):
            news_data["data"]["rt_story"] = msg.getElement("RT_NEWS_STORY").getValueAsString()
            
        if msg.hasElement("RT_NEWS_HEADLINE_ONLY"):
            news_data["data"]["rt_headline"] = msg.getElement("RT_NEWS_HEADLINE_ONLY").getValueAsString()
        
        filename = os.path.join(self.output_dir, f"index_news_{security}_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        # Print formatted news
        print(f"\n=== News Update for {security} ===")
        print(f"Time: {timestamp}")
        
        if msg.hasElement("NEWS_HEADLINES"):
            print(f"Headline: {news_data['data']['headlines']}")
            
        if msg.hasElement("NEWS_STORY"):
            print(f"Story: {news_data['data']['story']}")
            
        if msg.hasElement("RT_NEWS_STORY"):
            print(f"Real-time Story: {news_data['data']['rt_story']}")
            
        if msg.hasElement("RT_NEWS_HEADLINE_ONLY"):
            print(f"Real-time Headline: {news_data['data']['rt_headline']}")
            
        print("========================")

    def _processMarketDataMessage(self, msg, security):
        """Process and save market data message"""
        if msg.hasElement("LAST_PRICE"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            market_data = {
                "security": security,
                "timestamp": timestamp,
                "last_price": msg.getElementAsFloat("LAST_PRICE")
            }
            
            # Save to JSON file
            filename = os.path.join(self.output_dir, f"dj_market_{security}_{timestamp}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(market_data, f, indent=2)
            
            print(f"\n=== Market Data for {security} ===")
            print(f"Time: {timestamp}")
            print(f"Last Price: {market_data['last_price']}")
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
    feed = BloombergDowJonesNews()
    
    if not feed.start():
        return
    
    feed.subscribe()
    
    try:
        print("\nSubscribed to Dow Jones and market news. Press Ctrl+C to exit.")
        print("Monitoring DJI, INDU, and SPX indices for news and price updates...\n")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()

if __name__ == "__main__":
    main() 