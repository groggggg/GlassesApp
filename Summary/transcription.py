from fastapi import FastAPI, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from your Node/MentraOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextIn(BaseModel):
    text: str

# --- Module-level state persists between POST calls ---
is_recording = False
recorded_text = ""

@app.post("/process")
async def process_text(data: TextIn):
    """
    Only responds when "stop" is said.  
    Accumulates text between "start" and "stop".
    """
    global is_recording, recorded_text
    text = (data.text or "").lower().strip()

    # Start recording
    if "start" in text and not is_recording:
        is_recording = True
        recorded_text = ""
        return Response(status_code=204)  # do not send anything to Node

    # Stop recording
    if "stop" in text and is_recording:
        is_recording = False
        final_text = recorded_text.strip()
        recorded_text = ""
        # Here you can run your editing logic or LLM
        edited = final_text.upper()  # simple example
        return {"edited_text": edited}

    # During recording → append text silently
    if is_recording:
        recorded_text += (" " if recorded_text else "") + text
        return Response(status_code=204)  # do not send anything yet

    # Outside recording → do nothing
    return Response(status_code=204)
