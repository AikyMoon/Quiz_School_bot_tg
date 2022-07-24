# ------------------    конфиг для бота        ------------------
TOKEN = "5465391003:AAHCtgeHNUXJFuxqd9uqmU9W7RrbA32qwsU"

# ------------------    конфиг для бд           ------------------
USER = "postgres"
PASSWORD = "345msk00"
HOST = "127.0.0.1"
PORT = "5432"
DATABASE = "quiz_data"

# ------------------ имена админов в телеге   ------------------
admins = {
    "Захар": "@Aiky_Moon",
    "Александр": "@dark5160"
}

MAX_GROUP_USERS = 4

CACHE = {}

ADMINS_ID = {
    "ZAHAR": 1047354271
}

COMMANDS = {
    "non_register": ["/reg", "/admin", "/help"],
    "without_group": ["/create", "/invite", "/admin", "/help", "/profile"],
    "player": ["/statistics", "/task", "/admin", "/help", "/leave", "/profile"],
    "master": ["/statistics", "/users", "/group_info",
               "/ok", "/no", "/kick", "/task", "/answer",
               "/leave", "/exit", "/admin", "/help", "/profile"]
}
