import blpapi
import time
from datetime import datetime
import os

class BloombergDowJonesNews:
    def __init__(self):
        self.session = None
        self.DOW_JONES_EID = "81347"  # Dow Jones News Feed EID
        self.output_dir = os.path.join(os.path.dirname(__file__), "dowjones_output")
        
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
            
        if not self.session.openService("//blp/mktnews-dowjonesnews"):
            print("Failed to open Dow Jones news service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for Dow Jones news"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to Dow Jones News Feed with XML format
        topic = f"//blp/mktnews-dowjonesnews/eid/{self.DOW_JONES_EID}?format=xml"
        correlationId = blpapi.CorrelationId("DowJones-News")
        
        subscriptions.add(topic=topic,
                         correlationId=correlationId)

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
            self._processNewsMessage(msg)

    def _processNewsMessage(self, msg):
        """Process and save Dow Jones news message"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Extract key fields based on documentation
            story = msg.getElement("ContentT").getElement("StoryContent")
            
            # Get metadata
            metadata = story.getElement("Story").getElement("Metadata")
            headline = metadata.getElementAsString("Headline") if metadata.hasElement("Headline") else "N/A"
            wire_name = metadata.getElementAsString("WireName") if metadata.hasElement("WireName") else "N/A"
            time_of_arrival = metadata.getElementAsString("TimeOfArrival") if metadata.hasElement("TimeOfArrival") else "N/A"
            
            # Get story content
            story_content = story.getElement("Story")
            body = story_content.getElementAsString("Body") if story_content.hasElement("Body") else "N/A"
            hot_level = story_content.getElementAsString("HotLevel") if story_content.hasElement("HotLevel") else "0"
            language = story_content.getElementAsString("LanguageString") if story_content.hasElement("LanguageString") else "N/A"
            
            # Print formatted news
            print("\n=== Dow Jones News Update ===")
            print(f"Time: {time_of_arrival}")
            print(f"Source: {wire_name}")
            print(f"Language: {language}")
            print(f"Hot Level: {hot_level}")
            print(f"Headline: {headline}")
            print("Body Preview:", body[:200] + "..." if len(body) > 200 else body)
            print("========================\n")
            
            # Save full message to XML file
            filename = os.path.join(self.output_dir, f"dj_news_{timestamp}.xml")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(msg.toString())
                
        except Exception as e:
            print(f"Error processing news message: {e}")

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
        print("\nSubscribed to Dow Jones News Feed. Press Ctrl+C to exit.")
        print("Monitoring for news updates...\n")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()

if __name__ == "__main__":
    main() 