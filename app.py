import base64
import binascii

import requests
import streamlit as st

import diet_logic
import i18n
from chatbot import render_chatbot_ui


st.set_page_config(
    page_title="AI Medical Diagnostic & Visual Indicator Workspace", page_icon="🩺"
)

with st.sidebar:
    i18n.init_language_selector()
    st.divider()
    feature_choice = st.radio(
        i18n.t("workspace"),
        ("original", "diet", "chat"),
        format_func=lambda choice: {
            "original": i18n.t("original_workspace"),
            "diet": i18n.t("diet_tab"),
            "chat": i18n.t("chat_tab"),
        }[choice],
        key="workspace_section",
    )

if feature_choice == "diet":
    st.title(i18n.t("diet_title"))
    st.write(i18n.t("diet_intro"))

    with st.form("diet_plan_form"):
        user_ingredients = st.text_input(
            i18n.t("ingredients_prompt"),
            help=i18n.t("ingredients_help"),
        )
        budget_limit = st.slider(
            i18n.t("budget_prompt"),
            min_value=100,
            max_value=1000,
            value=400,
            step=25,
        )
        generate_plan = st.form_submit_button(
            i18n.t("generate"), type="primary"
        )

    if generate_plan:
        st.session_state["diet_plan"] = diet_logic.get_diet_recommendations(
            user_ingredients, budget_limit
        )

    meal_plan = st.session_state.get("diet_plan", [])
    if meal_plan:
        st.subheader(i18n.t("recommendation_title"))
        for meal in meal_plan:
            matched = meal["matched_ingredients"]
            with st.expander(
                f"{i18n.t(meal['category'])}: {i18n.t(meal['name_key'])}"
            ):
                st.write(f"**{i18n.t('cuisine')}:** {i18n.t(meal['cuisine_key'])}")
                st.write(
                    f"**{i18n.t('estimated_cost')}:** "
                    f"₹{meal['cost_min']}–₹{meal['cost_max']} per serving"
                )
                st.write(
                    f"**{i18n.t('ingredients')}:** "
                    f"{', '.join(i18n.ingredient_name(item) for item in meal['ingredients'])}"
                )
                st.write(f"**{i18n.t('preparation')}:** {i18n.t(meal['prep_key'])}")
                if matched:
                    st.success(
                        f"{i18n.t('ingredients')}: "
                        f"{', '.join(i18n.ingredient_name(item) for item in matched)}"
                    )
                st.checkbox(
                    i18n.t("include_meal"),
                    value=True,
                    key=f"diet_include_{meal['id']}",
                )

        selected_meals = [
            meal
            for meal in meal_plan
            if st.session_state.get(f"diet_include_{meal['id']}", True)
        ]
        if selected_meals:
            st.subheader(i18n.t("grocery_title"))
            st.caption(i18n.t("grocery_help"))
            for ingredient in diet_logic.generate_grocery_list(selected_meals):
                st.checkbox(
                    i18n.ingredient_name(ingredient),
                    value=True,
                    key=f"diet_grocery_{ingredient}",
                )
    elif "diet_plan" in st.session_state:
        minimum = diet_logic.get_minimum_daily_budget()
        st.warning(i18n.t("no_plan", minimum=minimum))

    st.warning(i18n.t("disclaimer"))
    st.stop()

if feature_choice == "chat":
    render_chatbot_ui()
    st.stop()

st.title("AI Medical Diagnostic & Visual Indicator Workspace")
st.caption(
    "Extract report results, describe scans, or generate a structured report for clinician review."
)
st.warning(
    "AI-generated results can be inaccurate. They are not a diagnosis or a "
    "substitute for advice from a qualified medical professional."
)

api_url = st.text_input("Backend URL", value="http://127.0.0.1:8000").rstrip("/")
analysis = st.radio(
    "Choose an analysis",
    (
        "Extract report tests",
        "Describe an image",
        "Comprehensive image analysis",
        "Detailed diagnosis",
        "Compare images",
    ),
    horizontal=True,
)

if analysis == "Compare images":
    st.title("AI-powered image comparison")
    st.write(
        "Upload at least two images (JPG, JPEG, PNG, or WEBP) to find similarities, "
        "differences, and semantic similarity."
    )
    uploaded_files = st.file_uploader(
        "Upload images for comparison",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )

    if uploaded_files and len(uploaded_files) < 2:
        st.warning("Please upload at least two images to perform a comparison.")
    elif uploaded_files:
        st.success(f"Successfully loaded {len(uploaded_files)} images.")
        columns = st.columns(min(len(uploaded_files), 4))
        for index, file in enumerate(uploaded_files):
            with columns[index % len(columns)]:
                st.subheader(f"Image {index + 1}")
                st.image(
                    file.getvalue(),
                    alt=f"Uploaded comparison image {index + 1}",
                    width="stretch",
                )
                st.caption(file.name)

    if st.button(
        "Run image comparison analysis",
        type="primary",
        disabled=not uploaded_files or len(uploaded_files) < 2,
    ):
        if not api_url:
            st.error("Enter the backend URL.")
        else:
            files_payload = [
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        file.type or "application/octet-stream",
                    ),
                )
                for file in uploaded_files
            ]
            with st.spinner("Analyzing images locally via Ollama..."):
                try:
                    response = requests.post(
                        f"{api_url}/compare-images",
                        files=files_payload,
                        timeout=300,
                    )
                    response.raise_for_status()
                    result = response.json()
                except requests.RequestException as exc:
                    st.error(f"Could not complete image comparison: {exc}")
                except ValueError as exc:
                    st.error(f"The backend returned an invalid JSON response: {exc}")
                else:
                    if not isinstance(result, dict):
                        st.error("The backend returned an invalid comparison report.")
                    else:
                        st.markdown("---")
                        st.subheader("Comprehensive comparison report")
                        for key, label in (
                            ("image_descriptions", "Image descriptions"),
                            ("key_similarities", "Key similarities"),
                            ("important_differences", "Important differences"),
                            ("unique_features", "Unique features"),
                            ("visual_changes", "Visual changes"),
                            ("comparison_summary", "Comparison summary"),
                            ("similarity_score", "Semantic similarity score"),
                        ):
                            st.markdown(f"**{label}:**")
                            st.write(result.get(key, "Not provided."))
    st.stop()

if analysis == "Extract report tests":
    endpoint = "/analyze-report"
    file_types = ["pdf", "png", "jpg", "jpeg", "webp"]
    help_text = "Upload a PDF report or an image of a report."
elif analysis == "Describe an image":
    endpoint = "/analyze-image"
    file_types = ["png", "jpg", "jpeg", "webp"]
    help_text = "Upload a scan image."
elif analysis == "Detailed diagnosis":
    endpoint = "/detailed-diagnosis"
    file_types = ["jpg", "png", "jpeg", "pdf"]
    help_text = "Upload a medical report or scan image for a structured analysis."
else:
    endpoint = "/comprehensive-analysis"
    file_types = ["png", "jpg", "jpeg", "webp"]
    help_text = "Upload a scan image for analysis and side-by-side comparison."

uploaded_file = st.file_uploader("Select a file", type=file_types, help=help_text)

if uploaded_file is not None and endpoint in {
    "/comprehensive-analysis",
    "/detailed-diagnosis",
}:
    original_column, result_column = st.columns(2)
    with original_column:
        st.subheader("Original real input")
        if uploaded_file.type in ("image/png", "image/jpeg", "image/webp"):
            st.image(
                uploaded_file.getvalue(),
                alt="Original uploaded scan",
                width="stretch",
            )
        else:
            st.info("PDF document uploaded successfully.")

if st.button(
    "Run comprehensive analysis" if endpoint == "/comprehensive-analysis" else "Analyze",
    type="primary",
    disabled=uploaded_file is None,
):
    if not api_url:
        st.error("Enter the backend URL.")
    else:
        with st.spinner("Analyzing... This may take a little while."):
            try:
                response = requests.post(
                    f"{api_url}{endpoint}",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type or "application/octet-stream",
                        )
                    },
                    timeout=300,
                )
                response.raise_for_status()
                result = response.json()
            except requests.RequestException as exc:
                st.error(f"Could not reach the analysis backend: {exc}")
            except ValueError as exc:
                st.error(f"The backend returned an invalid JSON response: {exc}")
            else:
                if endpoint == "/detailed-diagnosis":
                    diagnostic = result.get("diagnostic", {})
                    annotated_base64 = result.get("annotated_image")
                    if not isinstance(diagnostic, dict):
                        st.error("The backend returned an invalid diagnostic report.")
                        diagnostic = {}

                    with result_column:
                        st.subheader("AI visual indicator")
                        if annotated_base64:
                            try:
                                annotated_bytes = base64.b64decode(
                                    annotated_base64, validate=True
                                )
                            except (binascii.Error, TypeError) as exc:
                                st.error(
                                    f"The backend returned an invalid annotated image: {exc}"
                                )
                            else:
                                st.image(
                                    annotated_bytes,
                                    alt="AI annotation of the uploaded scan",
                                    width="stretch",
                                )
                        else:
                            st.info(
                                "No image was available to annotate for this document."
                            )
                        st.success("Diagnostic breakdown generated!")
                        st.markdown("### Comprehensive diagnostic report")
                        st.markdown(
                            "**Abnormal behavior / symptoms observed:**"
                        )
                        st.write(
                            diagnostic.get(
                                "abnormal_behavior_or_symptoms", "Not provided."
                            )
                        )
                        st.markdown("**Name of the condition / disease:**")
                        st.write(diagnostic.get("condition_name", "Not provided."))
                        st.markdown("**Root causes and underlying factors:**")
                        st.write(diagnostic.get("root_causes", "Not provided."))
                        st.markdown("**Actionable solutions and follow-ups:**")
                        st.write(
                            diagnostic.get("actionable_solutions", "Not provided.")
                        )
                elif endpoint == "/comprehensive-analysis":
                    try:
                        comparison_bytes = base64.b64decode(
                            result["comparison_image"], validate=True
                        )
                    except (KeyError, TypeError, binascii.Error) as exc:
                        st.error(f"The backend returned an invalid comparison image: {exc}")
                    else:
                        with result_column:
                            st.subheader("Comparison and findings")
                            st.image(
                                comparison_bytes,
                                alt="Side-by-side scan and AI findings panel",
                                width="stretch",
                            )
                        st.subheader("Detailed findings")
                        st.json(result["diagnostics"])
                        st.caption(result.get("status", ""))
                else:
                    st.subheader("Analysis result")
                    st.json(result)