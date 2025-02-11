from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class PodcastEpisode(BaseModel):
    episode_url: str
    audio_format: str = "mp3"
    max_duration: int = 3600  # 最大时长限制（秒）

class ProcessingResult(BaseModel):
    original_url: str
    transcription: str
    summary: str
    key_points: List[str]
    entities: Dict[str, List[str]]
    processed_at: datetime
    duration: float
    audio_quality: Dict[str, float]
