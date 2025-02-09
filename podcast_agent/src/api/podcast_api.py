from fastapi import APIRouter, BackgroundTasks
from typing import Optional
import uuid
from ..core.podcast.downloader import PodcastDownloader
from ..core.podcast.processor import AudioPipeline
from ..core.podcast.transcriber import transcribe_with_timestamps
from ..core.podcast.summarizer import generate_summary
from ..core.podcast.exceptions import PodcastError

router = APIRouter(prefix="/podcast", tags=["podcast"])

class PodcastTask:
    def __init__(self, url: str, task_id: str):
        self.url = url
        self.task_id = task_id
        self.status = "queued"
        self.progress = 0.0

podcast_queue = []

@router.post("/process")
async def process_podcast(
    url: str,
    background_tasks: BackgroundTasks,
    language: Optional[str] = "auto",
    model_size: Optional[str] = "base"
):
    try:
        task_id = str(uuid.uuid4())
        task = PodcastTask(url=url, task_id=task_id)
        podcast_queue.append(task)

        background_tasks.add_task(process_podcast_task, task, language, model_size)

        return {
            "task_id": task_id,
            "status": task.status,
            "progress": task.progress
        }
    except Exception as e:
        raise PodcastError(3, str(e)) from e

async def process_podcast_task(task: PodcastTask, language: str, model_size: str):
    try:
        task.status = "downloading"
        downloader = PodcastDownloader()
        audio_path = await downloader.download(task.url)

        task.progress = 0.3
        task.status = "processing"
        processor = AudioPipeline()
        processed_path = await processor.process(audio_path)

        task.progress = 0.6
        task.status = "transcribing"
        transcript = transcribe_with_timestamps(processed_path, language, model_size)

        task.progress = 0.8
        task.status = "summarizing"
        summary = generate_summary(transcript)

        task.progress = 1.0
        task.status = "completed"
        return {
            "transcript": transcript,
            "summary": summary,
            "duration": transcript[-1]["end"] if transcript else 0
        }
    except Exception as e:
        task.status = "failed"
        raise PodcastError(2, str(e)) from e
