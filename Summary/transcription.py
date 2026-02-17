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
recording_text = "Recording"

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
        print(recorded_text[0].isalnum)
        recorded_text == recorded_text[1:]
        
        return {"return": "Recording started"}

    # Stop recording
    if end_word in text and is_recording:
        is_recording = False
        final_text = text.split(end_word, 1)[0].strip()
        recorded_text = ""

        edited = Summarize(final_text)  
        print(edited)
        return {"return": final_text}

    # During recording
    if is_recording:
        recorded_text += " " + text
        recording_text += "."
        if recorded_text[-4] == ".":
            recorded_text = "Recording"
        return {"return": recording_text}
    
    if "identity" in text:
        return "Ms. Claire, female patient, transferred from Ward 5B to ICU. Handover given by Catherine to Mike. Charge nurse already present and monitoring initiated."

    if show_word in text and not is_recording:
        return {"return": edited}
    
    return {"return": ""}