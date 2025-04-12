from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Define a model to validate incoming location data
class LocationData(BaseModel):
    latitude: float
    longitude: float
    timestamp: str

# Store connected WebSocket clients
connected_clients: List[WebSocket] = []

# Simple logging setup
logging.basicConfig(level=logging.INFO)

# Endpoint to receive location updates via HTTP POST
@app.post("/update-location")
async def update_location(location_data: LocationData):
    try:
        # Log the received data (in a real app, you'd store this in a database)
        logging.info(f"Received location: {location_data.latitude}, {location_data.longitude} at {location_data.timestamp}")

        # Send location update to all connected WebSocket clients
        for client in connected_clients:
            try:
                # Send the location update to all connected WebSocket clients
                await client.send_text(f"Location update: Latitude={location_data.latitude}, Longitude={location_data.longitude}, Timestamp={location_data.timestamp}")
            except WebSocketDisconnect:
                # Handle WebSocket disconnects and remove client from list
                connected_clients.remove(client)
        
        # Return a successful response
        return {"message": "Location received successfully", "data": location_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    connected_clients.append(websocket)  # Add client to the connected clients list

    try:
        while True:
            # Wait for incoming location data from the WebSocket client
            data = await websocket.receive_text()
            logging.info(f"Received location update from WebSocket client: {data}")

            # You could process the location data here (store it, broadcast, etc.)
            # Send a confirmation message back to the client
            await websocket.send_text(f"Received your location update: {data}")
            
            # Optionally, broadcast location data to all other connected clients
            for client in connected_clients:
                if client != websocket:  # Avoid sending the data back to the sender
                    try:
                        await client.send_text(f"Location update from another client: {data}")
                    except WebSocketDisconnect:
                        connected_clients.remove(client)

    except WebSocketDisconnect:
        # Handle WebSocket disconnect and remove client from the connected clients list
        connected_clients.remove(websocket)
        logging.info("A client disconnected.")

# Start the FastAPI server (use Uvicorn to run this file)
