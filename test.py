import blpapi
from blpapi import Session, SessionOptions

# Define a callback function to handle incoming events
def process_message(msg):
    if msg.hasElement("securityData"):
        security_data = msg.getElement("securityData")
        security_name = security_data.getElementAsString("security")
        print(f"Security: {security_name}")
        
        field_data = security_data.getElement("fieldData")
        for data in field_data.values():
            date = data.getElementAsString("date")
            px_last = data.getElementAsFloat("PX_LAST")
            print(f"  Date: {date}, PX_LAST: {px_last}")
    else:
        print("No security data in the message.")

# Create a session to connect to Bloomberg API
def start_bloomberg_session():
    print("Starting Bloomberg session...")
    options = SessionOptions()
    options.setServerHost('localhost')
    options.setServerPort(8194)
    session = Session(options)

    if not session.start():
        print("Failed to start session.")
        return None
    
    print("Session started successfully.")
    
    if not session.openService("//blp/refdata"):
        print("Failed to open Bloomberg reference data service.")
        return None
    
    print("Successfully opened reference data service.")
    return session

# Request and process the data
def get_data(session):
    print("Preparing request for historical data...")
    ref_data_service = session.getService("//blp/refdata")
    request = ref_data_service.createRequest("HistoricalDataRequest")
    
    # Set up the request parameters
    request.getElement("securities").appendValue("AAPL US Equity")
    request.getElement("fields").appendValue("PX_LAST")
    request.set("startDate", "20230101")
    request.set("endDate", "20230122")
    request.set("periodicitySelection", "DAILY")
    
    # Send the request
    print("Sending request for AAPL US Equity historical data...")
    session.sendRequest(request)

    while True:
        ev = session.nextEvent()
        
        for msg in ev:
            process_message(msg)

        # Break the loop when we receive the full response
        if ev.eventType() == blpapi.Event.RESPONSE:
            print("Received full response.")
            break

# Main execution block
if __name__ == "__main__":
    print("Starting the script...")
    session = start_bloomberg_session()
    
    if session:
        get_data(session)
        print("Data retrieval complete.")
        session.stop()
    else:
        print("Exiting due to session failure.")
