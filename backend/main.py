from pathlib import Path
import webview
from app_api import AppApi

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = (BASE_DIR.parent / "ui" / "index.html").as_uri()

def run():
    webview.create_window(
        title="Kiosk",
        url=UI_PATH,
        js_api=AppApi(),
        fullscreen=True,
        resizable=False,
        frameless=True
    )
    webview.start(debug=False)

if __name__ == "__main__":
    run()
