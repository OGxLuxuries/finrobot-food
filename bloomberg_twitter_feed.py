import blpapi
import time
from datetime import datetime
import os

class BloombergTwitterFeed:
    def __init__(self):
        self.session = None
        self.TWITTER_EID = "70028"
        self.SENTIMENT_EID = "80047"
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def start(self):
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost("localhost")
        sessionOptions.setServerPort(8194)
        sessionOptions.setMaxEventQueueSize(10000)
        
        # Add authentication options
        sessionOptions.setAuthenticationOptions("AuthenticationMode=APPLICATION_ONLY;"
                                              "ApplicationAuthenticationType=APPNAME_AND_KEY;"
                                              "ApplicationName=YourAppName;"  # Replace with your app name
                                              "ApplicationVersion=1.0")

        self.session = blpapi.Session(sessionOptions, self.processEvent)
        
        if not self.session.start():
            print("Failed to start session.")
            return False
            
        if not self.session.openService("//blp/mktnews-content"):
            print("Failed to open service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for Twitter feed and sentiment"""
        subscriptions = blpapi.SubscriptionList()
        
        # Twitter feed subscription
        twitter_topic = f"/news/eid/{self.TWITTER_EID}"  # Simplified topic format
        twitter_correlationId = blpapi.CorrelationId("TwitterFeed-AAPL")
        subscriptions.add(topic=twitter_topic,
                         correlationId=twitter_correlationId)

        # Sentiment subscription
        sentiment_topic = f"/analytics/eid/{self.SENTIMENT_EID}/AAPL US Equity"  # Modified topic format
        sentiment_correlationId = blpapi.CorrelationId("Sentiment-AAPL")
        subscriptions.add(topic=sentiment_topic,
                         correlationId=sentiment_correlationId)

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
            if msg.correlationId().value().startswith("TwitterFeed"):
                self._processTwitterMessage(msg)
            elif msg.correlationId().value().startswith("Sentiment"):
                self._processSentimentMessage(msg)

    def _processTwitterMessage(self, msg):
        """Process and save Twitter message"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"twitter_feed_{timestamp}.xml")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(msg.toString())
            print(f"Saved Twitter feed to {filename}")

    def _processSentimentMessage(self, msg):
        """Process and save sentiment message"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"sentiment_{timestamp}.xml")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(msg.toString())
            print(f"Saved sentiment data to {filename}")

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
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Stopping...")
    finally:
        feed.session.stop()

if __name__ == "__main__":
    main() 