# self.ie (Koyeb-ready)

This repo contains a Flask app configured for deployment on **Koyeb** (free tier).

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```

## Deploy to Koyeb

1. Push this repo to GitHub.
2. In **Koyeb** → *Create Service*, select this repo and the **Dockerfile** preset.
3. Set the service port to **8000**.
4. Add environment variables:
   - `SECRET_KEY` = a random string
   - `GOOGLE_APPLICATION_CREDENTIALS_JSON` = paste your **entire** service account JSON on one line
5. Deploy. Your app will be available at the URL Koyeb provides.

## Google Credentials (in-Python style)

If you use Google APIs in your code, import and use:

```python
from google_auth import get_credentials
creds = get_credentials()  # reads GOOGLE_APPLICATION_CREDENTIALS_JSON
```

Then pass `creds` to the Google client you need (e.g., `build(..., credentials=creds)` or storage client).

## Notes

- Production server is **gunicorn** (see `gunicorn.conf.py`).
- The app is exposed as `app:app` from `app.py`. If your entrypoint changes, update `Dockerfile`.
- A `Procfile` is included for optional Render deploys.
