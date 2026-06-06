# Task 2 - AI Software Generator Deployment

This folder contains the deployable Flask version of the Task 1 AI Software Generator.

## Local run

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Environment variables

Create a local `.env` file for testing, but do not upload it to GitHub.

```text
APIFREE_API_KEY=your_api_key_here
APIFREE_BASE_URL=https://api.apifree.ai/v1
APIFREE_MODEL=openai/gpt-5.4-mini
APIFREE_IMAGE_MODEL=openai/gpt-image-1.5
```

For Render deployment, add the same variables in the Render Environment Variables panel.

## Render settings

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app
```
