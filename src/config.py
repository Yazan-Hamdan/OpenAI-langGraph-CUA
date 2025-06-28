import os
from dotenv import load_dotenv
from threading import Lock

class Config:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.BROWSER_WIDTH = int(os.getenv("BROWSER_WIDTH", 1920))
        self.BROWSER_HEIGHT = int(os.getenv("BROWSER_HEIGHT", 1080))
        self.RECURSION_LIMIT = int(os.getenv("RECURSION_LIMIT", 50))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME")
        self.LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
        self.LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", True)


        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in .env file")

        if not self.EXPERIMENT_NAME:
            raise ValueError("EXPERIMENT_NAME is not set in .env file")

        if not self.LANGSMITH_API_KEY:
            raise ValueError("LANGSMITH_API_KEY is not set in .env file")
