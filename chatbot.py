import ollama
import streamlit as st
from ollama import Message

from i18n import t
from llm import SCAN_MODEL


SUGGESTED_QUESTIONS = ("suggest_balanced", "suggest_lab")


def _queue_suggested_question(question: str) -> None:
    st.session_state["pending_chat_prompt"] = question


def _language_instruction(language: str) -> str:
    return {
        "Hindi": "Respond in Hindi.",
        "Marathi": "Respond in Marathi.",
    }.get(language, "Respond in English.")


def render_chatbot_ui() -> None:
    st.title(t("chat_title"))
    st.write(t("chat_intro"))
    st.info(t("chat_safety"))
    st.caption(t("disclaimer"))

    st.session_state.setdefault("chat_history", [])

    if st.button(t("clear_conversation"), key="clear_chat"):
        st.session_state["chat_history"] = []
        st.session_state.pop("pending_chat_prompt", None)

    if not st.session_state["chat_history"]:
        st.markdown(f"**{t('suggested_questions')}:**")
        first, second = st.columns(2)
        for column, question_key in zip(
            (first, second), SUGGESTED_QUESTIONS
        ):
            question = t(question_key)
            column.button(
                question,
                key=f"suggest_{question_key}",
                on_click=_queue_suggested_question,
                args=(question,),
            )

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_question = st.chat_input(t("chat_input"))
    user_query = st.session_state.pop("pending_chat_prompt", None) or typed_question
    if not user_query:
        return

    st.session_state["chat_history"].append(
        {"role": "user", "content": user_query}
    )
    with st.chat_message("user"):
        st.markdown(user_query)

    language = st.session_state.get("selected_language", "English")
    messages: list[Message] = [
        {
            "role": "system",
            "content": (
                "You are a safe, helpful wellness and project assistant. "
                "Give general educational information, not diagnoses or "
                "personalized treatment. Encourage a qualified clinician for "
                "medical decisions and urgent services for emergencies. "
                "Do not claim to have access to reports unless the user shares "
                "their contents in this conversation. "
                + _language_instruction(language)
            ),
        },
        *st.session_state["chat_history"][-20:],
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = ollama.chat(model=SCAN_MODEL, messages=messages)
            except (ollama.RequestError, ollama.ResponseError) as exc:
                st.error(t("chat_error", error=str(exc)))
                return

        try:
            reply = response["message"]["content"]
        except (KeyError, TypeError) as exc:
            st.error(t("chat_invalid"))
            raise ValueError("The local AI model returned an invalid response.") from exc
        if not isinstance(reply, str) or not reply.strip():
            st.error(t("chat_invalid"))
            raise ValueError("The local AI model returned an empty response.")

        st.markdown(reply)
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": reply}
        )
