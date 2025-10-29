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
final_text = ""

@app.post("/process")
async def process_text(data: TextIn):
    start_word = "start recording"
    end_word = "stop recording"
    show_word = "show summary"

    global is_recording, recorded_text
    text = data.text.lower().strip()

    # Start recording
    if start_word in text and not is_recording:
        is_recording = True
        recorded_text = ""
        return {"return": "recording started"}

    # Stop recording
    if end_word in text and is_recording:
        is_recording = False
        final_text = recorded_text.strip()
        recorded_text = ""
        # Here you can run your LLM or editing logic
        edited = final_text.upper()  # simple example
        return {"return": edited}

    # During recording
    if is_recording:
        recorded_text += " " + text
        return {"return": "recording"}

    if show_word in text and not is_recording:
        return {"return": recorded_text}
    
    return {"return": ""}