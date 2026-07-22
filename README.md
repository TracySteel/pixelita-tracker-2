# Pixelita Tracker

Tiny Flask app for email open and click tracking.

## Endpoints

Open tracking pixel:

```html
<img src="https://YOUR-PIXELITA-DOMAIN/open.png?job=mcd-relo-other-side&email=other-side-email-1&event=open" width="1" height="1" alt="">
```

Click tracking redirect:

```html
<a href="https://YOUR-PIXELITA-DOMAIN/click?job=mcd-relo-other-side&email=other-side-email-1&link=smart-moves-guide&redirect=https%3A%2F%2Fexample.com%2Fguide">
  Read Smart Moves guide
</a>
```

Report:

```text
https://YOUR-PIXELITA-DOMAIN/report?token=YOUR_REPORT_TOKEN
```

## Logged fields

Pixelita logs to `pixel_log.csv`:

- `timestamp`
- `event`
- `job`
- `email`
- `link`
- `pid`
- `redirect`
- `ip`
- `user_agent`
- `referer`
- `extra`

`pid` is optional. If you do not include a per-contact value, reporting is campaign/email/link level only.

## Local run

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
REPORT_TOKEN=choose-a-secret-token python app.py
```

Then test:

```text
http://127.0.0.1:5000/open.png?job=test&email=test-email&event=open
http://127.0.0.1:5000/click?job=test&email=test-email&link=test-link&redirect=https%3A%2F%2Fexample.com
http://127.0.0.1:5000/report?token=choose-a-secret-token
```

## Production notes

The app needs a writable filesystem for `pixel_log.csv`. If the host has an ephemeral filesystem, use a persistent disk or database before using it for a real send.

## Railway setup

This folder is ready to deploy as a Railway web service.

### Deploy source

Use this folder as the Railway service root:

```text
emails/pixel-tracker/pixelita-tracker-main
```

Railway will use `Dockerfile` via `railway.json`.

### Variables

Set this variable in Railway:

```text
REPORT_TOKEN=choose-a-long-random-secret
```

You do not need to set `PIXELITA_LOG_FILE` if you attach a Railway Volume. Pixelita automatically uses `RAILWAY_VOLUME_MOUNT_PATH/pixel_log.csv`.

### Volume

Add a Railway Volume to the Pixelita service.

Recommended mount path:

```text
/data
```

Railway makes this available to the app as `RAILWAY_VOLUME_MOUNT_PATH`, and Pixelita writes the log to:

```text
/data/pixel_log.csv
```

### Domain

In the Railway service, generate a public domain. After deployment, test:

```text
https://YOUR-RAILWAY-DOMAIN/health
https://YOUR-RAILWAY-DOMAIN/open.png?job=test&email=test-email&event=open
https://YOUR-RAILWAY-DOMAIN/click?job=test&email=test-email&link=main-cta&redirect=https%3A%2F%2Fexample.com
https://YOUR-RAILWAY-DOMAIN/report?token=YOUR_REPORT_TOKEN
```

### Email replacements

For open tracking, use:

```html
<img src="https://YOUR-RAILWAY-DOMAIN/open.png?job=mcd-relo-other-side&email=other-side-email-1&event=open" width="1" height="1" alt="">
```

For all tracking, replace `{{PIXELITA_BASE_URL}}` with your Railway app URL:

```text
https://YOUR-RAILWAY-DOMAIN
```

The generated emails already add `/open.png` for opens and `/click` for the main CTA links. Leave normal footer, privacy, unsubscribe, and email links as direct links.
