import json
import os
import urllib.request


def notify(message):
    """
    Posts a message to Google Chat via an incoming webhook.
    Silently no-ops if GCHAT_WEBHOOK_URL isn't set (e.g. local runs),
    and never raises — a notification failure must not break the
    actual crawl/import.
    """

    webhook_url = os.environ.get("GCHAT_WEBHOOK_URL")

    if not webhook_url:
        return

    try:
        body = json.dumps({"text": message}).encode("utf-8")

        request = urllib.request.Request(
            webhook_url,
            data=body,
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )

        urllib.request.urlopen(request, timeout=10)
    except Exception as e:
        print(f"Google Chat notification failed (non-fatal): {e}")
