import json
import re

import ollama

MODEL = "qwen3-vl:4b"
SCAN_MODEL = MODEL


def ask_json(system, user_text, image_bytes=None, model=MODEL, retries=2):
    msg = {"role": "user", "content": user_text}
    if image_bytes:
        msg["images"] = (
            image_bytes if isinstance(image_bytes, list) else [image_bytes]
        )

    for _ in range(retries + 1):
        resp = ollama.chat(
            model=model,
            messages=[{"role": "system", "content": system}, msg],
            format="json",
            options={"temperature": 0},
        )
        text = resp["message"]["content"].strip()
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    raise ValueError("Model did not return valid JSON")