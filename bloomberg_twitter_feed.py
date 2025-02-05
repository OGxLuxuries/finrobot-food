import blpapi
import time
from datetime import datetime
import os
import xml.sax.saxutils as saxutils  # For XML escaping

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

    def _escape_xml(self, text):
        """Escape special characters for XML"""
        if not isinstance(text, str):
            text = str(text)
        return saxutils.escape(text)

    def _processSocialMessage(self, msg, security):
        """Process and save social media and sentiment data"""
        # Only save if we have sentiment-related data
        has_sentiment_data = any([
            msg.hasElement("SOCIAL_MEDIA_ANALYTICS"),
            msg.hasElement("SOCIAL_VELOCITY"),
            msg.hasElement("NEWS_SENTIMENT"),
            msg.hasElement("NEWS_HEADLINES"),
            msg.hasElement("NEWS_STORY")
        ])
        
        if not has_sentiment_data and not msg.hasElement("LAST_PRICE"):
            return  # Skip empty updates
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a simplified XML structure
        simplified_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<SocialData>
    <Security>{security}</Security>
    <Timestamp>{timestamp}</Timestamp>"""
        
        if msg.hasElement("LAST_PRICE"):
            price = msg.getElementAsFloat("LAST_PRICE")
            simplified_data += f"\n    <LastPrice>{price}</LastPrice>"
            print(f"\n=== Social Media Update for {security} ===")
            print(f"Time: {timestamp}")
            print(f"Price: {price}")
        
        if msg.hasElement("SOCIAL_MEDIA_ANALYTICS"):
            analytics = msg.getElement("SOCIAL_MEDIA_ANALYTICS").getValueAsString()
            simplified_data += f"\n    <SocialMediaSentiment>{analytics}</SocialMediaSentiment>"
            print("Social Media Sentiment:", analytics)
            
        if msg.hasElement("SOCIAL_VELOCITY"):
            velocity = msg.getElement("SOCIAL_VELOCITY").getValueAsString()
            simplified_data += f"\n    <TweetVolume>{velocity}</TweetVolume>"
            print("Tweet Volume/Velocity:", velocity)
            
        if msg.hasElement("NEWS_SENTIMENT"):
            sentiment = msg.getElement("NEWS_SENTIMENT").getValueAsString()
            simplified_data += f"\n    <NewsSentiment>{sentiment}</NewsSentiment>"
            print("News Sentiment Score:", sentiment)
            
        if msg.hasElement("NEWS_HEADLINES"):
            headlines = msg.getElement("NEWS_HEADLINES").getValueAsString()
            simplified_data += f"\n    <Headlines>{headlines}</Headlines>"
            print("Related Headlines:", headlines)
            
        if msg.hasElement("NEWS_STORY"):
            story = msg.getElement("NEWS_STORY").getValueAsString()
            simplified_data += f"\n    <NewsStory>{story}</NewsStory>"
            story_preview = story[:200] + "..." if len(story) > 200 else story
            print("News Story Preview:", story_preview)
        
        simplified_data += "\n</SocialData>"
        
        # Only save if we have sentiment-related data
        if has_sentiment_data:
            filename = os.path.join(self.output_dir, f"social_{security}_{timestamp}.xml")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(simplified_data)
        
        if has_sentiment_data or msg.hasElement("LAST_PRICE"):
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