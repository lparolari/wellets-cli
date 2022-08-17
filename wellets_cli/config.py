import os


class Config:
    api_url = os.getenv("API_URL") or "https://wellets-backend.herokuapp.com"
    api_username = os.getenv("API_USERNAME")
    api_password = os.getenv("API_PASSWORD")
