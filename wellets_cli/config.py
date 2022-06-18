import os


class Config:
    api_url = os.getenv("API_URL") or "http://localhost:3333"
