from main.db_connect import *


# ------------------получение текста задачи            ------------------
def get_task(task_id: int) -> tuple[str, str]:
    cur.execute(f"select task, manual from questions where task_id = {task_id}")
    return cur.fetchone()


# ------------------привязка задачи к пользователю      ------------------
def task_bind(task_id: int, user_id: int):
    cur.execute(f"update users set task_id = {task_id} where id = {user_id}")
    con.commit()


# ------------------ проверка ответа                    ------------------
def check_answer(task_id: int, answer: str) -> bool:
    cur.execute(f"select answer from questions where task_id = {task_id}")
    correct = cur.fetchone()[0]
    return answer in correct


# ------------------ получение количеста очков          ------------------
def get_points(task_id: int) -> int:
    cur.execute(f"select points from questions where task_id = {task_id}")
    return cur.fetchone()[0]


# ------------------ декримент кол-ва активаций         ------------------
def activation_decriment(task_id: int):
    cur.execute(f"select act_counts from questions where task_id = {task_id}")
    act_counts = cur.fetchone()[0] - 1
    cur.execute(f"update questions set act_counts = {act_counts} where task_id = {task_id}")


# ------------------ доступна ли уже задача             ------------------
def check_task_act_counts(task_id: int) -> bool:
    cur.execute(f"select act_counts from questions where task_id = {task_id}")
    if cur.fetchone()[0] == 0:
        return False
    return True


# ------------------ проверка типа задач                ------------------
def check_task_type(task_id: int) -> bool:
    cur.execute(f"select task from questions where task_id = {task_id}")
    if cur.fetchone()[0] == "nan":
        return False
    return True


# ------------------ есть ли такой id задачи                 ------------------
def check_task_id(task_id: int) -> bool:
    cur.execute(f"select task_id from questions where task_id = {task_id}")
    if cur.fetchone():
        return True
    return False
