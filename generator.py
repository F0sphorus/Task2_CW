import base64
import os
import time
from pathlib import Path
from plantuml import PlantUML
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

API_KEY = os.getenv("APIFREE_API_KEY")
BASE_URL = os.getenv("APIFREE_BASE_URL", "https://api.apifree.ai/v1")
MODEL = os.getenv("APIFREE_MODEL", "openai/gpt-5.4-mini")
IMAGE_MODEL = os.getenv("APIFREE_IMAGE_MODEL", "openai/gpt-image-1.5")


def get_client() -> OpenAI:
    """Create an OpenAI-compatible client using environment variables."""
    if not API_KEY:
        raise RuntimeError(
            "APIFREE_API_KEY is not set. Add it in your local .env file "
            "or in Render Environment Variables."
        )

    return OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )


def ask_llm(prompt: str) -> str:
    """Send a prompt to the LLM and return generated text."""
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional software engineering assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=2500,
        temperature=0.3,
        stream=False,
    )

    return response.choices[0].message.content.strip()


def generate_requirements(system_description: str) -> str:
    """Generate a concise requirements document."""
    prompt = f"""
Generate a concise software requirements document for this business problem:

{system_description}

Use this format:

Actors:
- ...

Functional Requirements:
- ...

Non-functional Requirements:
- ...
"""
    return ask_llm(prompt)


def generate_uml(system_description: str) -> str:
    """Generate PlantUML use case diagram code."""
    prompt = f"""
Generate a PlantUML Use Case Diagram for:

{system_description}

Rules:
- Return only PlantUML code
- Start with @startuml
- End with @enduml
"""
    return ask_llm(prompt)

def render_uml_image():
    server = PlantUML(
        url="http://www.plantuml.com/plantuml/img/"
    )

    server.processes_file(
        "generated/uml.puml"
    )

    return "generated/uml.png"

def generate_flask_api(system_description: str) -> str:
    """Generate a minimal Flask API."""
    prompt = f"""
Generate a minimal but functional Python Flask API for the following business problem:

{system_description}

Requirements:
- At least two API endpoints
- Return JSON responses
- Include dummy data for demonstration
- Keep code concise and runnable
- Return only Python code, no Markdown fences
"""
    return ask_llm(prompt)


def generate_website(system_description: str) -> str:
    """Generate a simple HTML website for the requested software system."""
    prompt = f"""
Generate a complete, minimal but functional HTML website for a software project.

The website should:
- Display requirements for the following system: {system_description}
- Display UML diagram from uml.png
- Display generated Flask API code
- Include a form to input business problem and submit to Flask API
- Use simple HTML/CSS, no external frameworks
- Return only HTML code, no Markdown fences
"""
    return ask_llm(prompt)


def generate_image(system_description: str) -> str:
    """Generate an AI image and save it to generated/generated_image.png."""
    if not API_KEY:
        raise RuntimeError(
            "APIFREE_API_KEY is not set. Image generation cannot run."
        )

    prompt = f"""
Create a clean professional software project illustration for:
{system_description}

Style:
- modern web application dashboard
- software engineering theme
- clean UI
- suitable for a university coursework project
"""

    submit_url = "https://api.apifree.ai/v1/image/submit"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": IMAGE_MODEL,
        "num_images": 1,
        "prompt": prompt,
        "quality": "high",
        "size": "1024x1024",
    }

    submit_response = requests.post(
        submit_url,
        headers=headers,
        json=payload,
        timeout=60,
    )
    submit_response.raise_for_status()
    submit_data = submit_response.json()

    request_id = submit_data["resp_data"]["request_id"]
    result_url = f"https://api.apifree.ai/v1/image/{request_id}/result"

    image_url = None
    image_base64 = None

    for _ in range(30):
        time.sleep(3)

        result_response = requests.get(
            result_url,
            headers=headers,
            timeout=60,
        )
        result_response.raise_for_status()
        result_data = result_response.json()

        resp_data = result_data.get("resp_data", {})
        status = resp_data.get("status")

        if status == "success":
            image_list = resp_data.get("image_list", [])
            if image_list:
                image_url = image_list[0]
                break

        elif status in ["failed", "error"]:
            raise RuntimeError(f"Image generation failed: {resp_data}")

        if "image_url" in resp_data:
            image_url = resp_data["image_url"]
            break

        if "url" in resp_data:
            image_url = resp_data["url"]
            break

        if "images" in resp_data and resp_data["images"]:
            first_image = resp_data["images"][0]

            if isinstance(first_image, str):
                image_url = first_image
                break

            if isinstance(first_image, dict):
                image_url = first_image.get("url")
                image_base64 = first_image.get("b64_json")
                break

        if "b64_json" in resp_data:
            image_base64 = resp_data["b64_json"]
            break

    output_path = GENERATED_DIR / "generated_image.png"

    if image_url:
        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        output_path.write_bytes(image_response.content)

    elif image_base64:
        output_path.write_bytes(base64.b64decode(image_base64))

    else:
        raise RuntimeError(
            "Image generation did not return an image URL or base64 data."
        )

    return "generated/generated_image.png"

