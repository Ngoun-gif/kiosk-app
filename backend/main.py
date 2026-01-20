from pathlib import Path
import webview
from src.kiosk.app_api import Api

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = (BASE_DIR / "ui" / "index.html").as_uri()

if __name__ == "__main__":
    api = Api()

    webview.create_window(
        title="Kiosk",
        url=UI_PATH,          # absolute file URI (more reliable)
        js_api=api,
        fullscreen=True,
        resizable=False,
        frameless=True
    )

    webview.start(debug=False)  # keep debug off for kiosk
