import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
import logging
from db import Database
from agent import create_agent, LyricsAndVocabulary
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Ollama host from environment or use default
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:9000')
MODEL_NAME = "llama3.2:1b"

app = FastAPI(title="Lyrics Vocabulary API")
db = Database()

class LyricsRequest(BaseModel):
    message_request: str

class LyricsResponse(BaseModel):
    lyrics: str
    vocabulary: List[str]
    result_file: str

# Initialize Ollama client
ollama_client = ollama.Client(host=OLLAMA_HOST)
agent = create_agent(ollama_client)

@app.post("/api/agent")
async def get_lyrics_endpoint(lyrics_request: LyricsRequest):
    try:
        result = agent(lyrics_request.message_request)
        result_file = db.save_result(
            query=lyrics_request.message_request,
            lyrics=result.lyrics,
            vocabulary=result.vocabulary
        )
        return LyricsResponse(
            lyrics=result.lyrics,
            vocabulary=result.vocabulary,
            result_file=result_file
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)