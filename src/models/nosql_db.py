from tinydb import TinyDB, Query
import os

# dossier data propre
os.makedirs("data", exist_ok=True)

db = TinyDB("data/user_preferences.json")
users_table = db.table("users")


def _get_user(email):
    User = Query()
    return users_table.get(User.email == email)


def _create_user_if_missing(email):
    User = Query()
    existing = users_table.get(User.email == email)

    if not existing:
        users_table.insert({
            "email": email,
            "last_page": "/home",
            "preferences": {}
        })


# ───────────────
# LAST PAGE
# ───────────────
def set_last_page(email, page_route):
    if not email:
        return

    _create_user_if_missing(email)
    User = Query()

    users_table.update(
        {"last_page": page_route},
        User.email == email
    )


def get_last_page(email):
    if not email:
        return "/home"

    user = _get_user(email)
    if user:
        return user.get("last_page", "/home")

    return "/home"


# ───────────────
# PREFERENCES
# ───────────────
def save_page_preferences(email, page_name, preferences):
    if not email:
        return

    _create_user_if_missing(email)
    User = Query()
    user = _get_user(email)

    all_prefs = user.get("preferences", {})
    all_prefs[page_name] = preferences

    users_table.update(
        {"preferences": all_prefs},
        User.email == email
    )


def get_page_preferences(email, page_name):
    if not email:
        return {}

    user = _get_user(email)
    if not user:
        return {}

    return user.get("preferences", {}).get(page_name, {})