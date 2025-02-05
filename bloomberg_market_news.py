import blpapi
import time
from datetime import datetime
import os

class BloombergMarketNews:
    def __init__(self):
        self.session = None
        # EIDs for Market Moving News
        self.BLOOMBERG_MMN_EID = "80048"  # Bloomberg Company Market Moving News
        self.MISC_MMN_EID = "80180"      # Miscellaneous Market Moving News
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
            
        if not self.session.openService("//blp/mktnews-content"):
            print("Failed to open market news service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for market moving news"""
        subscriptions = blpapi.SubscriptionList()
        
        # Bloomberg Company Market Moving News
        bloomberg_topic = f"//blp/mktnews-content/analytics/eid/{self.BLOOMBERG_MMN_EID}"
        bloomberg_correlationId = blpapi.CorrelationId("Bloomberg-MMN")
        subscriptions.add(topic=bloomberg_topic,
                         correlationId=bloomberg_correlationId)

        # Miscellaneous Market Moving News
        misc_topic = f"//blp/mktnews-content/analytics/eid/{self.MISC_MMN_EID}"
        misc_correlationId = blpapi.CorrelationId("Misc-MMN")
        subscriptions.add(topic=misc_topic,
                         correlationId=misc_correlationId)

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
        """Handle market moving news updates"""
        for msg in event:
            self._processNewsMessage(msg)

    def _processNewsMessage(self, msg):
        """Process and save market moving news message"""
        try:
            # Parse the XML structure based on documentation
            if msg.hasElement("StoryAnalytics"):
                analytics = msg.getElement("StoryAnalytics")
                
                # Get metadata
                metadata = analytics.getElement("Metadata")
                headline = metadata.getElementAsString("Headline") if metadata.hasElement("Headline") else "N/A"
                time_of_arrival = metadata.getElementAsString("TimeOfArrival") if metadata.hasElement("TimeOfArrival") else "N/A"
                
                # Get score information
                score_list = analytics.getElement("StructuredScoreList")
                if score_list.hasElement("StructuredScore"):
                    score = score_list.getElement("StructuredScore")
                    confidence = score.getElementAsFloat("Confidence") if score.hasElement("Confidence") else 0.0
                    entity_id = score.getElementAsString("EntityId") if score.hasElement("EntityId") else "N/A"
                
                # Print formatted news
                print("\n=== Market Moving News ===")
                print(f"Time: {time_of_arrival}")
                print(f"Headline: {headline}")
                print(f"Entity: {entity_id}")
                print(f"Confidence: {confidence:.4f}")
                print("========================\n")
                
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.output_dir, f"mmn_{timestamp}.xml")
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
    feed = BloombergMarketNews()
    
    if not feed.start():
        return
    
    feed.subscribe()
    
    try:
        print("\nSubscribed to Market Moving News. Press Ctrl+C to exit.")
        print("Monitoring both Bloomberg and Miscellaneous market-moving news...\n")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        feed.session.stop()

if __name__ == "__main__":
    main() 