import os
from typing import Optional


class Settings:

    @property
    def show_charts(self) -> bool:
        return os.environ.get("WELLETS_API_URL") or True

    @property
    def save_charts(self) -> bool:
        return os.environ.get("WELLETS_SAVE_CHARTS") or False

    @property
    def date_format(self) -> str:
        return os.environ.get("WELLETS_DATE_FORMAT") or "%b %d, %Y"

    @property
    def datetime_format(self) -> str:
        return os.environ.get("WELLETS_DATETIME_FORMAT") or "%b %d, %Y %H:%M"

    @property
    def api_url(self) -> str:
        return (
            os.environ.get("WELLETS_API_URL") or "https://wellets-backend.herokuapp.com"
        )

    @property
    def api_username(self) -> Optional[str]:
        return os.environ.get("WELLETS_API_USERNAME") or None

    @property
    def api_password(self) -> Optional[str]:
        return os.environ.get("WELLETS_API_PASSWORD") or None

    def __str__(self):
        return f'Settings(show_charts={self.show_charts}, save_charts={self.save_charts}, date_format="{self.date_format}", datetime_format="{self.datetime_format}", api_url="{self.api_url}", api_username="{self.api_username}", api_password=<secret>)'


settings = Settings()

print(settings)
