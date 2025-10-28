from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    start_word = "start"
    end_word = "end"

    global is_recording, recorded_text
    text = data.text.lower().strip()

    # Start recording
    if start_word in text and not is_recording:
        is_recording = True
        recorded_text = ""
        return {"status": "recording started"}

    # Stop recording
    if end_word in text and is_recording:
        is_recording = False
        final_text = recorded_text.strip()
        recorded_text = ""
        # Here you can run your LLM or editing logic
        edited = final_text.upper()  # simple example
        return {"edited_text": edited}

    # During recording
    if is_recording:
        recorded_text += " " + text
        return {"status": "recording"}

    # Outside recording
    return {"status": "ignored"}