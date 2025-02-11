import sounddevice as sd
import numpy as np
from pathlib import Path
import yaml
from typing import AsyncGenerator

class AudioStreamService:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        config_path = Path("config/audio_stream.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)

        self.sample_rate = config['sample_rate']
        self.channels = config['channels']
        self.dtype = config['dtype']
        self.chunk_duration = config['chunk_duration']

    async def __aenter__(self):
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype
        )
        self.stream.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.stream.stop()
        self.stream.close()

    async def read_stream(self) -> AsyncGenerator[np.ndarray, None]:
        chunk_size = int(self.sample_rate * self.chunk_duration)
        while True:
            data, _ = await asyncio.to_thread(
                self.stream.read,
                chunk_size
            )
            yield np.frombuffer(data, dtype=np.float32)
