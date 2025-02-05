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
            
        if not self.session.openService("//blp/mktnews-content"):
            print("Failed to open market news content service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for Twitter feed data"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to Twitter feed with EID 70028
        correlationId = blpapi.CorrelationId("twitter_feed")
        subscriptions.add(
            topic="//blp/mktnews-content/news/eid/70028?format=json",
            correlationId=correlationId
        )

        print("Subscribing to Twitter feed...")
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
        """Process and save social media data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        social_data = {
            "security": security,
            "timestamp": timestamp,
            "type": "social",
            "data": {
                "tweet": {
                    "body": msg.getElement("StoryContent").getElement("Story").getElement("Body").getValueAsString() if msg.hasElement("StoryContent") else "",
                    "url": msg.getElement("StoryContent").getElement("Story").getElement("WebURL").getValueAsString() if msg.hasElement("StoryContent") else "",
                    "language": msg.getElement("StoryContent").getElement("Story").getElement("LanguageString").getValueAsString() if msg.hasElement("StoryContent") else "",
                },
                "user": {
                    "handle": msg.getElement("StoryContent").getElement("Story").getElement("SocialMediaInfo").getElement("TwitterGNIPMeta").getElement("UserInfo").getElement("Handle").getValueAsString() if msg.hasElement("StoryContent") else "",
                    "followers": msg.getElement("StoryContent").getElement("Story").getElement("SocialMediaInfo").getElement("TwitterGNIPMeta").getElement("UserInfo").getElement("Followers").getValueAsInteger() if msg.hasElement("StoryContent") else 0,
                    "lists": msg.getElement("StoryContent").getElement("Story").getElement("SocialMediaInfo").getElement("TwitterGNIPMeta").getElement("UserInfo").getElement("TwitterLists").getValueAsInteger() if msg.hasElement("StoryContent") else 0,
                    "tweets": msg.getElement("StoryContent").getElement("Story").getElement("SocialMediaInfo").getElement("TwitterGNIPMeta").getElement("UserInfo").getElement("Tweets").getValueAsInteger() if msg.hasElement("StoryContent") else 0
                },
                "metadata": {
                    "assigned_topics": self._getAssignedTopics(msg),
                    "derived_topics": self._getDerivedTopics(msg),
                    "assigned_tickers": self._getAssignedTickers(msg),
                    "derived_tickers": self._getDerivedTickers(msg)
                }
            }
        }
        
        filename = os.path.join(self.output_dir, f"social_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(social_data, f, indent=2, ensure_ascii=False)

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