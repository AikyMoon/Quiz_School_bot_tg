# ------------------    конфиг для бота        ------------------
TOKEN = "5465391003:AAHCtgeHNUXJFuxqd9uqmU9W7RrbA32qwsU"

# ------------------    конфиг для бд           ------------------
USER = "postgres"
PASSWORD = "345msk00"
HOST = "127.0.0.1"
PORT = "5432"
DATABASE = "quiz_data"
DATABASE_URL = "postgres://gdlwdfdygdqmmu:d748b3985fb8307c090a8af1067172b4777904bf5885ffec1c66e235b196d72f@ec2-3-248-121-12.eu-west-1.compute.amazonaws.com:5432/d7m109ll4k6t29"

# ------------------ имена админов в телеге   ------------------
admins = {
    "Захар": "@Aiky_Moon",
    "Александр": "@dark5160"
}

MAX_GROUP_USERS = 4

CACHE = {}

ADMINS_IDS = {
    1047354271: "ZAHAR",
    983933445: "ALEKSANDR"
}

COMMANDS = {
    "non_register": ["/reg", "/admin", "/help"],
    "without_group": ["/create", "/invite", "/admin", "/help", "/profile"],
    "player": ["/statistics", "/task", "/admin", "/help", "/leave", "/profile"],
    "master": ["/statistics", "/users", "/group_info",
               "/ok", "/no", "/kick", "/task", "/answer",
               "/leave", "/exit", "/admin", "/help", "/profile"]
}

