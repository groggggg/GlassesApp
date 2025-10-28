from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# allow the Render app to call this (for dev; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextIn(BaseModel):
    text: str

@app.post("/process")
async def process_text(data: TextIn):
    # Put whatever editing logic you want here.
    # Example: uppercasing and trimming filler words
    text = data.text or ""
    # simple filler removal example:
    for filler in [" um ", " uh ", " like "]:
        text = text.replace(filler, " ")
    edited = text.strip().upper()
    return {"edited_text": edited}