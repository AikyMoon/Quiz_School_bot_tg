from main.db_connect import *
from main.config import COMMANDS
from main.groups import check_group

# ------------------ проверка роли                ------------------
def check_role(user_id: int) -> bool:
    cur.execute(f"SELECT is_player FROM users WHERE id = {user_id}")
    return cur.fetchone()[0]


# ------------------ есть ли уже такой пользователь      ------------------
def check_id(user_id: int) -> bool:
    cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
    if not cur.fetchone():
        return False
    return True


# ------------------ получение имя пользователя         ------------------
def get_uname(user_id: int) -> str:
    cur.execute(f"SELECT first_name, last_name FROM users WHERE id = {user_id}")
    return " ".join(cur.fetchone())


# ------------------ установка имени пользователя       ------------------
def set_name(user_id: int, first_name: str, last_name: str) -> None:
    cur.execute(f"INSERT INTO users (id, first_name, last_name) VALUES ({user_id}, '{first_name}', '{last_name}')")
    con.commit()


# ------------------ смена роли с игрока на капитана    ------------------
def change_role(user_id: int):
    cur.execute(f"UPDATE users SET is_player = false WHERE id = {user_id}")
    con.commit()


# ------------------ смена is_requested на true         ------------------
def set_wait_true(user_id: int):
    cur.execute(f"UPDATE users SET is_requested = true where id = {user_id}")
    con.commit()


# ------------------проверка ожидания                   ------------------
def check_wait(user_id: int) -> bool:
    cur.execute(f"SELECT is_requested FROM users where id = {user_id}")
    return cur.fetchone()[0]


# ------------------ установка id группы пользователю   ------------------
def set_group_id(user_id: int, group_id: int):
    cur.execute(f"UPDATE users SET group_id = {group_id} WHERE id = {user_id}")
    con.commit()


# ------------------есть ли задача у участника          ------------------
def check_task(user_id: int) -> int:
    cur.execute(f"select task_id from users where id = {user_id}")
    result = cur.fetchone()[0]
    if not result:
        return 0
    return int(result)


# ------------------ отвязка вопроса                    ------------------
def unbind_task(user_id):
    cur.execute(f"update users set task_id = null where id = {user_id}")
    con.commit()


# ------------------ проверка возможности использования команды------------------
def can_use(user_id: int, command: str) -> bool:
    if check_id(user_id):
        if check_group(user_id):
            if not check_role(user_id):
                return command in COMMANDS["master"]
            else:
                return command in COMMANDS["player"]
        else:
            return command in COMMANDS["without_group"]
    else:
        return command in COMMANDS["non_register"]
