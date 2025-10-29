from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from summary import Summarize

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextIn(BaseModel):
    text: str

is_recording = False
recorded_text = ""
edited = ""
recording_text = "Recording started"

@app.post("/process")
async def process_text(data: TextIn):
    start_word = "start recording"
    end_word = "stop recording"
    show_word = "show summary"

    global is_recording, recorded_text, recording_text, edited
    text = data.text.lower().strip()
    print(recorded_text)

    # Start recording
    if start_word in text and not is_recording:
        is_recording = True
        recorded_text = text.split(start_word, 1)[1]
        recording_text = "Recording started"
        return {"return": recording_text}

    # Stop recording
    if end_word in text and is_recording:
        is_recording = False
        final_text = recorded_text.strip()
        recorded_text = ""

        edited = Summarize(final_text)  
        print(edited)
        return {"return": edited}

    # During recording
    if is_recording:
        recorded_text += " " + text
        recording_text += "."
        return {"return": recording_text}

    if show_word in text and not is_recording:
        return {"return": edited}
    
    return {"return": ""}