import io
import json
import textwrap

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


def read_pdf(data: bytes):
    doc = fitz.open(stream=data, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc).strip()
    image = None
    if len(text) < 50:
        image = doc[0].get_pixmap(dpi=150).tobytes("png")
    return text, image


def validate_image(image_bytes: bytes) -> None:
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc


def draw_anomaly_indicator(image_bytes: bytes, diagnostic_data: dict) -> bytes:
    """Draw model-provided normalized bounding boxes without inventing locations."""
    validate_image(image_bytes)

    with Image.open(io.BytesIO(image_bytes)) as source:
        image = source.convert("RGB")

    draw = ImageDraw.Draw(image)
    width, height = image.size
    font = ImageFont.load_default()
    boxes = diagnostic_data.get("bounding_boxes", [])
    valid_boxes = []

    if isinstance(boxes, list):
        for box in boxes:
            if (
                isinstance(box, (list, tuple))
                and len(box) == 4
                and all(
                    isinstance(value, (int, float)) and not isinstance(value, bool)
                    for value in box
                )
            ):
                left, top, right, bottom = box
                if 0 <= left < right <= 1 and 0 <= top < bottom <= 1:
                    valid_boxes.append(
                        (
                            round(left * width),
                            round(top * height),
                            round(right * width),
                            round(bottom * height),
                        )
                    )

    for box in valid_boxes:
        draw.rectangle(box, outline="red", width=max(3, min(width, height) // 150))

    label = (
        "AI-highlighted region"
        if valid_boxes
        else "AI REVIEW - no region localized"
    )
    label_left = 8
    label_top = 8
    text_bounds = draw.textbbox((label_left, label_top), label, font=font)
    padding = 6
    draw.rectangle(
        (
            text_bounds[0] - padding,
            text_bounds[1] - padding,
            text_bounds[2] + padding,
            text_bounds[3] + padding,
        ),
        fill="red",
    )
    draw.text((label_left, label_top), label, fill="white", font=font)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=90)
    return output.getvalue()


def create_side_by_side_comparison(
    original_image_bytes: bytes, diagnostic_data: dict
) -> bytes:
    validate_image(original_image_bytes)

    with Image.open(io.BytesIO(original_image_bytes)) as image:
        original = image.convert("RGB")
    original.thumbnail((900, 900))

    font = ImageFont.load_default()
    margin = 24
    panel_width = max(original.width, 360)
    text_width = panel_width - margin * 2
    content = json.dumps(diagnostic_data, indent=2, ensure_ascii=True)
    lines = []
    for line in content.splitlines():
        lines.extend(textwrap.wrap(line, width=max(1, text_width // 7)) or [""])

    line_height = 18
    panel_height = max(
        original.height,
        margin * 2 + 42 + len(lines) * line_height,
    )
    comparison = Image.new(
        "RGB", (original.width + panel_width, panel_height), color="white"
    )
    comparison.paste(original, (0, (panel_height - original.height) // 2))

    panel = ImageDraw.Draw(comparison)
    panel_x = original.width
    panel.rectangle(
        (panel_x, 0, panel_x + panel_width - 1, panel_height - 1),
        fill=(248, 249, 251),
        outline=(210, 215, 222),
        width=2,
    )
    panel.text((panel_x + margin, margin), "AI ANALYSIS", fill=(25, 37, 55), font=font)

    y = margin + 38
    for line in lines:
        panel.text((panel_x + margin, y), line, fill=(35, 43, 52), font=font)
        y += line_height

    output = io.BytesIO()
    comparison.save(output, format="JPEG", quality=90)
    return output.getvalue()