from main.config import ADMINS_IDS


# ------------------- проверка на админа -------------------
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS_IDS