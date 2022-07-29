import os


class Config:
    api_url = os.getenv("API_URL") or "http://localhost:3333"
    api_username = os.getenv("API_USERNAME")
    api_password = os.getenv("API_PASSWORD")
