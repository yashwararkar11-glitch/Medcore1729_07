import base64

from fastapi import FastAPI, File, HTTPException, UploadFile

import prompts
from llm import SCAN_MODEL, ask_json
from logic import (
    create_side_by_side_comparison,
    draw_anomaly_indicator,
    read_pdf,
    validate_image,
)

app = FastAPI()


@app.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    data = await file.read()
    mt = file.content_type

    if mt == "application/pdf":
        text, img = read_pdf(data)
    else:
        text, img = "", data

    msg = (
        "Extract the tests.\n\nREPORT TEXT:\n" + text
        if text
        else "Extract the tests from this image."
    )
    extracted = ask_json(prompts.REPORT_EXTRACT, msg, img)
    return extracted


@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    data = await file.read()
    result = ask_json(prompts.IMAGE, "Describe this scan.", data, model=SCAN_MODEL)
    return result


@app.post("/compare-images")
async def compare_images(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(
            status_code=400, detail="Upload at least two images to compare."
        )

    image_bytes_list = []
    for file in files:
        data = await file.read()
        try:
            validate_image(data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        image_bytes_list.append(data)

    return ask_json(
        prompts.IMAGE_COMPARISON,
        "Compare these uploaded images thoroughly according to the required parameters.",
        image_bytes_list,
        model=SCAN_MODEL,
    )


@app.post("/comprehensive-analysis")
async def comprehensive_analysis(file: UploadFile = File(...)):
    data = await file.read()
    try:
        validate_image(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    diagnostic_result = ask_json(
        prompts.IMAGE,
        "Analyze this image for findings and describe what is visible.",
        data,
        model=SCAN_MODEL,
    )
    comparison_bytes = create_side_by_side_comparison(data, diagnostic_result)
    return {
        "diagnostics": diagnostic_result,
        "comparison_image": base64.b64encode(comparison_bytes).decode("ascii"),
        "status": "Analysis and side-by-side comparison generated successfully",
    }


@app.post("/detailed-diagnosis")
async def detailed_diagnosis(file: UploadFile = File(...)):
    data = await file.read()
    mt = file.content_type

    if mt == "application/pdf":
        text, img = read_pdf(data)
    else:
        text, img = "", data
        try:
            validate_image(img)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    msg = (
        "Analyze this report text:\n\n" + text
        if text
        else "Analyze this image for diagnostics."
    )
    diagnostic = ask_json(
        prompts.DIAGNOSTIC_BREAKDOWN, msg, img, model=SCAN_MODEL
    )
    annotated_image = None
    if img:
        annotated_bytes = draw_anomaly_indicator(img, diagnostic)
        annotated_image = base64.b64encode(annotated_bytes).decode("ascii")

    return {
        "diagnostic": diagnostic,
        "annotated_image": annotated_image,
    }