import streamlit as st
import asyncio
import websockets
import json

# WebSocket URL of FastAPI backend
FASTAPI_WS_URL = "ws://127.0.0.1:8000/ws"

# Create a function to handle WebSocket communication
async def get_location_data():
    async with websockets.connect(FASTAPI_WS_URL) as websocket:
        while True:
            # Wait for location update from the backend
            location_data = await websocket.recv()
            yield location_data  # Yield data for streaming

# Create a Streamlit function to display real-time data
def display_real_time_data():
    st.title("Real-Time Location Tracker")
    st.write("Tracking live location updates...")

    # Use Streamlit's `st.empty()` to create an empty container that we will update
    live_location_placeholder = st.empty()

    # Start the WebSocket communication and get the data
    async def update_ui():
        async for location_data in get_location_data():
            # Display the received location data
            live_location_placeholder.write(f"New Location Update: {location_data}")
    
    # Run the asynchronous event loop
    asyncio.run(update_ui())

if __name__ == "__main__":
    display_real_time_data()
