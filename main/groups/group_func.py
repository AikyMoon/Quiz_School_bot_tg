from main.db_connect import *
from main.config import CACHE
from random import choice


# ------------------ состоит ли пользователь в группе   ------------------
def check_group(user_id: int) -> bool:
    cur.execute(f"SELECT group_id FROM users WHERE id = {user_id}")
    if not cur.fetchone()[0]:
        return False
    return True


# ------------------ генерация id группы                ------------------
def generate_group_id() -> int:

    free_ids = CACHE.get("cached_ids")

    if free_ids is None:
        cur.execute("SELECT group_id FROM users")
        all_ids = set(range(100_000, 1_000_000))
        brings_ids = set([i for i in cur.fetchall()])
        free_ids = all_ids - brings_ids

    new_id = choice(list(free_ids))
    free_ids.remove(new_id)
    CACHE["cached_ids"] = free_ids
    return new_id


# ------------------ создание группы в БД               ------------------
def new_group(group_id: int, group_name: str, user_id: int):
    cur.execute(f"INSERT INTO groups VALUES ({group_id}, '{group_name}', ARRAY[{user_id}])")
    con.commit()


# ------------------ получение id группы                ------------------
def get_group_id(user_id) -> int:
    cur.execute(f"SELECT group_id FROM users WHERE id = {user_id}")
    return cur.fetchone()[0]


# ------------------ получение имя группы                ------------------
def get_group_name(group_id: int) -> str:
    cur.execute(f"select group_name from groups where group_id = {group_id}")
    return cur.fetchone()[0]


# ------------------ получение количества пользователей в группе------------------
def get_users_count(group_id: int):
    cur.execute(f"SELECT COUNT(*) FROM users WHERE group_id = {group_id}")
    return cur.fetchone()[0]


# ------------------  форматирование участников            ------------------
def format_users_group(users: list[tuple], ids: list[int]) -> str:
    text = "Список участников группы:\n"
    for i, user in enumerate(users):
        role = "участник" if user[2] else "капитан"
        text += f"id: {ids[i]} - {user[0]} {user[1]} - {role}\n"

    return text.strip()


# ------------------  получение списка id участников группы------------------
def get_users_id(group_id: int) -> list[int]:
    cur.execute(f"SELECT group_users_id from groups where group_id = {group_id}")
    users_ids = cur.fetchone()[0]
    return users_ids


# ------------------  получение списка участников группы------------------
def get_users(group_id: int) -> str:
    users_ids = get_users_id(group_id)
    users_names = []
    for cur_id in users_ids:
        cur.execute(f"SELECT first_name, last_name, is_player FROM users where id = {cur_id}")
        data = cur.fetchone()
        users_names.append(data)

    text = format_users_group(users_names, users_ids)
    return text


# ------------------добавление запроса на вступление    ------------------
def new_group_requests(group_id: int, user_id: int):
    cur.execute(f"SELECT requests from groups where group_id = {group_id}")

    all_requests = list(cur.fetchone())
    all_requests.append(user_id)
    all_requests = [i for i in all_requests if i]

    cur.execute(f"UPDATE groups SET requests = ARRAY{all_requests} where group_id = {group_id}")


# ------------------проверка количества участников     ------------------
def check_users_count(group_id: int) -> int:
    cur.execute(f"SELECT COUNT(*) from users where group_id = {group_id}")
    return cur.fetchone()[0]


# ------------------ получение списка заявок            ------------------
def get_users_from_requests(group_id: int) -> str:
    cur.execute(f"select requests from groups where group_id = {group_id}")
    res = cur.fetchone()[0]
    if res:
        users = [i for i in res if i]
        text = "Список всех заявок:\n"

        for user in users:
            cur.execute(f"select first_name, last_name from users where id = {user}")
            data = cur.fetchone()
            text += f"id: {user} - {data[0]} {data[1]}\n"

        return text.strip()
    else:
        return "Заявок нет"


# ------------------подтверждение запроса на вступление ------------------
def add_user_group(group_id: int, user_id: int):
    cur.execute(f"UPDATE users set group_id = {group_id} where id = {user_id}")
    con.commit()
    cur.execute(f"SELECT group_users_id from groups where group_id = {group_id}")
    data = list(cur.fetchone()[0])
    data.append(user_id)
    cur.execute(f"update groups set group_users_id = ARRAY{data} where group_id = {group_id}")
    con.commit()


# ------------------ добавление очков                   ------------------
def add_points(group_id: int, points: int):
    cur.execute(f"select points from groups where group_id = {group_id}")
    data = cur.fetchone()[0] + points

    cur.execute(f"update groups set points = {data} where group_id = {group_id}")
    con.commit()


# ------------------ добавление решенных задач          ------------------
def add_ready_group_tasks(task_id: int, group_id: int):
    cur.execute(f"select ready_qs_id from groups where group_id = {group_id}")
    res = cur.fetchone()[0]
    if res:
        data = [i for i in res if i]
        data.append(task_id)
    else:
        data = [task_id]
    cur.execute(f"update groups set ready_qs_id = ARRAY{data} where group_id = {group_id}")
    con.commit()


# ------------------ решила ли группа уже задачу         ------------------
def check_group_task(task_id: str, group_id: int) -> bool:
    cur.execute(f"select ready_qs_id from groups where group_id = {group_id}")
    res = cur.fetchone()[0]
    if res:
        data = [i for i in res if i]
        return int(task_id) in data
    else:
        return False


# ------------------ количесто очков группы            ------------------
def get_group_points(group_id: int) -> int:
    cur.execute(f"select points from groups where group_id = {group_id}")
    points = cur.fetchone()[0]
    return points


# ------------------ кол-во решенных задач              ------------------
def get_task_count(group_id: int) -> int:
    cur.execute(f"select ready_qs_id from groups where group_id = {group_id}")
    try:
        return len(cur.fetchone()[0])
    except:
        return 0


# ------------------ получение капитана                    ------------------
def get_capitan(group_id: int) -> int:
    cur.execute(f"select id from users where group_id = {group_id} and is_player = false")
    return cur.fetchone()[0]


# ------------------ отвязка группы                         ------------------
def unbind_group(user_id: int, group_id: int):
    cur.execute(f"select group_users_id from groups where group_id = {group_id}")
    res = cur.fetchone()[0]
    if res:
        data = [i for i in res if i]
        data.remove(user_id)
    else:
        data = []

    cur.execute(f"update groups set group_users_id = ARRAY{data}::integer[] where group_id = {group_id}")
    con.commit()

    cur.execute(f"update users set group_id = null where id = {user_id}")
    con.commit()

    cur.execute(f"update users set is_player = true where id = {user_id}")
    con.commit()


# ------------------ получение списка заявок                  ------------------
def disagree_requests(group_id: int) -> list[int]:
    cur.execute(f"select requests from groups where group_id = {group_id}")
    res = cur.fetchone()[0]
    if res:
        data = [i for i in res if i]
        return data
    return []


# ------------------ получение списка пользователей в группе   ------------------
def send_warnings(group_id: int) -> list[int]:
    cur.execute(f"select group_users_id from groups where group_id = {group_id}")
    res = cur.fetchone()[0]
    if res:
        data = [i for i in res if i]
        return data
    return []


# ------------------ удаление группы из бд                    ------------------
def delete_group(group_id: int):
    cur.execute(f"delete from groups where group_id = {group_id}")
    con.commit()


# ------------------ есть ли такой id группы                  ------------------
def check_group_id(group_id: int) -> bool:
    cur.execute(f"select group_id from groups where group_id = {group_id}")
    if cur.fetchone():
        return True
    return False
