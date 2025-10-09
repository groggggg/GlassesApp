import asyncio
import websockets

async def main():
    uri = "wss://api.grogg.dev"
    async with websockets.connect(uri) as websocket:
        print("Connected to Node WebSocket")

        async for message in websocket:
            print("🗣️ From Node:", message)
            response = message.upper()  
            await websocket.send(response)
            print("📤 Sent back:", response)

asyncio.run(main())