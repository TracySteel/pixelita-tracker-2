from flask import Flask, request, send_file, render_template_string, redirect, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlparse
import csv
import datetime
import json
import os

app = Flask(__name__, static_folder="pixelita")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


def default_log_file():
    volume_path = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")
    if volume_path:
        return os.path.join(volume_path, "pixel_log.csv")
    return "pixel_log.csv"


CSV_FILE = os.environ.get("PIXELITA_LOG_FILE", default_log_file())
PNG_FILE = os.environ.get("PIXELITA_PIXEL_FILE", "transparent.png")

FIELDNAMES = [
    "timestamp",
    "event",
    "job",
    "email",
    "link",
    "pid",
    "redirect",
    "ip",
    "user_agent",
    "referer",
    "extra",
]

KNOWN_PARAMS = {"event", "job", "email", "link", "pid", "rid", "redirect", "url"}


def sanitize_csv_field(value):
    value_str = "" if value is None else str(value)
    if value_str and value_str[0] in "=+-@\t\r ":
        return "'" + value_str
    return value_str


def clean_event(value):
    value = (value or "").strip().lower()
    if value in {"open", "click"}:
        return value
    return "open"


def clean_redirect_url(value):
    value = (value or "").strip()
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https", "mailto"}:
        return value
    return ""


def ensure_log_file():
    if os.path.exists(CSV_FILE):
        return
    log_dir = os.path.dirname(CSV_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()


def append_log(event):
    ensure_log_file()

    extra = {
        key: request.args.getlist(key)
        for key in request.args.keys()
        if key not in KNOWN_PARAMS
    }

    pid = request.args.get("pid") or request.args.get("rid") or ""
    destination = request.args.get("redirect") or request.args.get("url") or ""

    row = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": event,
        "job": request.args.get("job", ""),
        "email": request.args.get("email", ""),
        "link": request.args.get("link", ""),
        "pid": pid,
        "redirect": destination,
        "ip": request.remote_addr or "",
        "user_agent": request.headers.get("User-Agent", ""),
        "referer": request.headers.get("Referer", ""),
        "extra": json.dumps(extra, sort_keys=True),
    }

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow({key: sanitize_csv_field(row.get(key, "")) for key in FIELDNAMES})


def read_log_rows():
    ensure_log_file()
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


@app.route("/open.png")
@app.route("/hit.png")
@app.route("/hit.gif")
def track_open():
    append_log(clean_event(request.args.get("event") or "open"))
    response = send_file(PNG_FILE, mimetype="image/png")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/click")
def track_click():
    destination = clean_redirect_url(request.args.get("redirect") or request.args.get("url"))
    append_log("click")

    if not destination:
        abort(400, "Missing or unsafe redirect URL.")

    return redirect(destination, code=302)


@app.route("/report")
def view_log():
    auth_token = request.args.get("token")
    expected_token = os.environ.get("REPORT_TOKEN")

    if not expected_token:
        return "Report access is disabled. Configure REPORT_TOKEN to enable it.", 403

    if auth_token != expected_token:
        return "Access denied.", 403

    rows = read_log_rows()

    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>Pixelita Log Report</title>
            <style>
              body { font-family: Arial, sans-serif; background: #f9f6ff; padding: 2em; color: #333; }
              table { width: 100%; border-collapse: collapse; box-shadow: 0 0 20px rgba(138, 43, 226, 0.2); }
              th, td { border-bottom: 1px solid #ccc; padding: 0.5em 1em; text-align: left; vertical-align: top; }
              th { background-color: #eae3ff; }
              code { background: #fff; padding: 0.15em 0.3em; border-radius: 4px; }
            </style>
          </head>
          <body>
            <h1>Pixelita Log Report</h1>
            <p><code>{{ count }}</code> events logged.</p>
            <table>
              <thead>
                <tr>
                  {% for field in fields %}<th>{{ field }}</th>{% endfor %}
                </tr>
              </thead>
              <tbody>
                {% for row in rows %}
                  <tr>
                    {% for field in fields %}<td>{{ row.get(field, "") }}</td>{% endfor %}
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          </body>
        </html>
        """,
        rows=rows,
        fields=FIELDNAMES,
        count=len(rows),
    )


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/")
def hello():
    return (
        "Pixelita is online. Use /open.png for opens, /click for clicks, "
        "and /report?token=YOUR_TOKEN for logs."
    )


@app.route("/test")
def test_page():
    return send_file("pixelita/index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
