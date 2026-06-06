from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from generator import (
    generate_flask_api,
    generate_image,
    generate_requirements,
    generate_uml,
    generate_website,
    render_uml_image,
)

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    error = None

    if request.method == "POST":
        system_description = request.form.get("system_description", "").strip()

        if not system_description:
            error = "Please enter a business problem."
        else:
            try:
                requirements = generate_requirements(system_description)
                uml = generate_uml(system_description)

                with open(
                      "generated/uml.puml","w",encoding="utf-8"
                )as f:
                        f.write(uml)
                render_uml_image()

                flask_code = generate_flask_api(system_description)
                website_code = generate_website(system_description)
                image_path = None
                image_error = None
                try:
                    image_path = generate_image(system_description)
                except Exception as image_exc:
                    image_error = str(image_exc)

                (GENERATED_DIR / "requirements.md").write_text(
                    requirements,
                    encoding="utf-8",
                )
                (GENERATED_DIR / "uml.puml").write_text(
                    uml,
                    encoding="utf-8",
                )
                (GENERATED_DIR / "flask_api.py").write_text(
                    flask_code,
                    encoding="utf-8",
                )
                (GENERATED_DIR / "website.html").write_text(
                    website_code,
                    encoding="utf-8",
                )

                result = {
                    "system_description": system_description,
                    "requirements": requirements,
                    "uml": uml,
                    "flask_code": flask_code,
                    "website_code": website_code,
                    "image_path": image_path,
                    "image_error": image_error,
                }

            except Exception as exc:
                error = str(exc)

    return render_template("index.html", result=result, error=error)


@app.route("/api/status")
def status():
    return jsonify(
        {
            "message": "AI Software Generator Running",
            "status": "success",
        }
    )


@app.route("/generated/<path:filename>")
def generated_files(filename):
    return send_from_directory(GENERATED_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
