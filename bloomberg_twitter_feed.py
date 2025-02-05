import blpapi
import time
from datetime import datetime
import os
import json  # Add this import and remove xml.sax.saxutils

class BloombergTwitterFeed:
    def __init__(self):
        self.session = None
        self.output_dir = os.path.join(os.path.dirname(__file__), "twitter_feed_output")
        
        # Create output directory if it doesn't exist
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
        """Create and send subscription for social media and sentiment data"""
        subscriptions = blpapi.SubscriptionList()
        
        # Market data subscription for tech companies
        securities = [
            "AAPL US Equity",
            "MSFT US Equity",
            "GOOGL US Equity"
        ]
        
        fields = [
            "LAST_PRICE",
            "SOCIAL_MEDIA_ANALYTICS",  # Social media sentiment
            "SOCIAL_VELOCITY",         # Tweet volume/velocity
            "NEWS_SENTIMENT",          # News sentiment score
            "NEWS_HEADLINES",          # Related news
            "NEWS_STORY"              # Full news stories
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
        """Handle subscription data"""
        for msg in event:
            security = msg.correlationId().value()
            self._processSocialMessage(msg, security)

    def _processSocialMessage(self, msg, security):
        """Process and save social media and sentiment data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        social_data = {
            "security": security,
            "timestamp": timestamp,
            "type": "social",
            "data": {}
        }
        
        # Add data fields only if they exist
        if msg.hasElement("LAST_PRICE"):
            social_data["data"]["last_price"] = msg.getElementAsFloat("LAST_PRICE")
            print(f"\n=== Social Media Update for {security} ===")
            print(f"Time: {timestamp}")
            print(f"Price: {social_data['data']['last_price']}")
        
        if msg.hasElement("SOCIAL_MEDIA_ANALYTICS"):
            social_data["data"]["social_sentiment"] = msg.getElement("SOCIAL_MEDIA_ANALYTICS").getValueAsString()
            print("Social Media Sentiment:", social_data["data"]["social_sentiment"])
            
        if msg.hasElement("SOCIAL_VELOCITY"):
            social_data["data"]["tweet_volume"] = msg.getElement("SOCIAL_VELOCITY").getValueAsString()
            print("Tweet Volume/Velocity:", social_data["data"]["tweet_volume"])
            
        if msg.hasElement("NEWS_SENTIMENT"):
            social_data["data"]["news_sentiment"] = msg.getElement("NEWS_SENTIMENT").getValueAsString()
            print("News Sentiment Score:", social_data["data"]["news_sentiment"])
            
        if msg.hasElement("NEWS_HEADLINES"):
            social_data["data"]["headlines"] = msg.getElement("NEWS_HEADLINES").getValueAsString()
            print("Related Headlines:", social_data["data"]["headlines"])
            
        if msg.hasElement("NEWS_STORY"):
            story = msg.getElement("NEWS_STORY").getValueAsString()
            social_data["data"]["story"] = story
            story_preview = story[:200] + "..." if len(story) > 200 else story
            print("News Story Preview:", story_preview)
        
        filename = os.path.join(self.output_dir, f"social_{security}_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(social_data, f, indent=2, ensure_ascii=False)
        
        if msg.hasElement("LAST_PRICE") or msg.hasElement("SOCIAL_MEDIA_ANALYTICS"):
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
    feed = BloombergTwitterFeed()
    
    if not feed.start():
        return
    
    feed.subscribe()
    
    try:
        print("\nSubscribed to social media and sentiment data. Press Ctrl+C to exit.")
        print("Monitoring AAPL, MSFT, and GOOGL...\n")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()

if __name__ == "__main__":
    main() 