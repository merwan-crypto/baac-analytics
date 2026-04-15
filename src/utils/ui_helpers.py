import streamlit as st

COLOR_INFO = "#1F4E79"
COLOR_DANGER = "#C0392B"
COLOR_WARN = "#E67E22"
COLOR_OK = "#2E8B57"
COLOR_LIGHT = "#EAF3FB"


def insight_box(emoji: str, texte: str, color: str = COLOR_INFO) -> None:
    st.markdown(
        f'<div style="background:{COLOR_LIGHT};border-left:5px solid {color};'
        f'border-radius:6px;padding:12px 18px;margin:8px 0 14px 0;'
        f'color:#1a1a2e;font-size:0.92rem;line-height:1.5;">'
        f'<span style="font-size:1.05rem;">{emoji}</span>&nbsp;&nbsp;{texte}</div>',
        unsafe_allow_html=True,
    )