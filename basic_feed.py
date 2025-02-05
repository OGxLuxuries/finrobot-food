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
            
        if not self.session.openService("//blp/mktdata"):
            print("Failed to open market data service.")
            return False
            
        return True

    def subscribe(self):
        """Create and send subscription for market data"""
        subscriptions = blpapi.SubscriptionList()
        
        # Subscribe to AAPL market data with proper correlation ID
        correlationId = blpapi.CorrelationId("AAPL")
        subscriptions.add(
            topic="AAPL US Equity",
            correlationId=correlationId,
            fields=["LAST_PRICE", "BID", "ASK", "VOLUME"],
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
        except blpapi.Exception as e:
            print(f"Error processing event: {e}")
        return False

    def _handleDataEvent(self, event):
        """Handle subscription data"""
        for msg in event:
            try:
                topic = msg.correlationId().value()
                market_data = {
                    "security": topic,
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
                
                if market_data["data"]:
                    filename = os.path.join(self.output_dir, f"market_data_{topic}_{market_data['timestamp']}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(market_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"\nMarket Data Update for {topic}:")
                    print(f"Time: {market_data['timestamp']}")
                    for key, value in market_data["data"].items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
                    print("========================")
            except blpapi.Exception as e:
                print(f"Error processing market data: {e}")

    def _handleStatusEvent(self, event):
        """Handle subscription status"""
        for msg in event:
            if msg.messageType() == blpapi.Names.SUBSCRIPTION_FAILURE:
                topic = msg.correlationId().value()
                print(f"Subscription failed for topic {topic}: {msg}")
            elif msg.messageType() == blpapi.Names.SUBSCRIPTION_TERMINATED:
                topic = msg.correlationId().value()
                print(f"Subscription terminated for topic {topic}")
            elif msg.messageType() == blpapi.Names.SUBSCRIPTION_STARTED:
                topic = msg.correlationId().value()
                print(f"Subscription started for topic {topic}")

    def _handleOtherEvent(self, event):
        """Handle other events"""
        for msg in event:
            if msg.messageType() == blpapi.Names.SESSION_TERMINATED:
                print("Session terminated")
                return False
            elif msg.messageType() == blpapi.Names.SLOW_CONSUMER_WARNING:
                print("Warning: Slow consumer")
            elif msg.messageType() == blpapi.Names.DATA_LOSS:
                topic = msg.correlationId().value()
                print(f"Warning: Data loss for topic {topic}")
        return True

def main():
    feed = BloombergBasicFeed()
    
    try:
        if not feed.start():
            return
        
        feed.subscribe()
        
        print("\nSubscribed to AAPL market data. Press Ctrl+C to exit.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping...")
    finally:
        if feed.session:
            feed.session.stop()
            feed.session.destroy()

if __name__ == "__main__":
    main() 