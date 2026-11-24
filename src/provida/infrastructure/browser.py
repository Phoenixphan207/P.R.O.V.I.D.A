"""Safe browser boundary. It never executes shell commands."""

import webbrowser


class BrowserService:
    def __init__(self, opener=None):
        self._opener = opener or webbrowser.open

    def open(self, url: str) -> bool:
        return bool(self._opener(url, new=2, autoraise=True))
