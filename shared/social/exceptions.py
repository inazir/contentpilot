# shared/social/exceptions.py

class PublishError(Exception):
    """Raised when a platform publisher fails permanently."""

    def __init__(self, message: str, platform: str):
        self.platform = platform
        super().__init__(f"[{platform}] {message}")
