import streamlit as st
from src.models.session import Session
from datetime import datetime


def load_view():
    st.title("Profil utilisateur")

    email = Session.get_current_user_email()

    if not email:
        st.warning("Aucun utilisateur connecté.")
        return

    st.subheader("Informations")
    st.write(f"**E-mail connecté :** {email}")

    st.subheader("Historique des actions")
    logs = Session.get_user_logs(email)

    if not logs:
        st.info("Aucune action enregistrée.")
        return

    for action, timestamp in logs:
        try:
            readable_date = datetime.fromtimestamp(int(timestamp)).strftime("%d/%m/%Y %H:%M:%S")
        except:
            readable_date = timestamp

        st.write(f"- **{action}** : {readable_date}")