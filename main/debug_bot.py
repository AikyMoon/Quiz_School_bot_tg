# ------------------ импорт библиотек и файла настроек ------------------
from config import *
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from psycopg2 import connect
from random import choice


# ------------------ настройка кэширования      ------------------
cache = {}

# ------------------ подключение к СУБД                 ------------------
con = connect(
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)
cur = con.cursor()


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


# ------------------ состоит ли пользователь в группе   ------------------
def check_group(user_id: int) -> bool:
    cur.execute(f"SELECT group_id FROM users WHERE id = {user_id}")
    if not cur.fetchone()[0]:
        return False
    return True


# ------------------ генерация id группы                ------------------
def generate_group_id() -> int:

    free_ids = cache.get("cached_ids")

    if free_ids is None:
        cur.execute("SELECT group_id FROM users")
        all_ids = set(range(100_000, 1_000_000))
        brings_ids = set([i for i in cur.fetchall()])
        free_ids = all_ids - brings_ids

    new_id = choice(list(free_ids))
    free_ids.remove(new_id)
    cache["cached_ids"] = free_ids
    return new_id


# ------------------ создание группы в БД               ------------------
def new_group(group_id: int, group_name: str, user_id: int):
    cur.execute(f"INSERT INTO groups VALUES ({group_id}, '{group_name}', ARRAY[{user_id}])")
    con.commit()


# ------------------ смена роли с игрока на капитана    ------------------
def change_role(user_id: int):
    cur.execute(f"UPDATE users SET is_player = false WHERE id = {user_id}")
    con.commit()


# ------------------ получение id группы                ------------------
def get_group_id(user_id) -> int:
    cur.execute(f"SELECT group_id FROM users WHERE id = {user_id}")
    return cur.fetchone()[0]


# ------------------ получение имя группы                ------------------
def get_group_name(group_id: int) -> str:
    cur.execute(f"select group_name from groups where group_id = {group_id}")
    return cur.fetchone()[0]


# ------------------ установка id группы пользователю   ------------------
def set_group_id(user_id: int, group_id: int):
    cur.execute(f"UPDATE users SET group_id = {group_id} WHERE id = {user_id}")
    con.commit()


# ------------------ проверка роли                ------------------
def check_role(user_id: int) -> bool:
    cur.execute(f"SELECT is_player FROM users WHERE id = {user_id}")
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
        print(data)

    text = format_users_group(users_names, users_ids)
    return text


# ------------------ смена is_requested на true         ------------------
def set_wait_true(user_id: int):
    cur.execute(f"UPDATE users SET is_requested = true where id = {user_id}")
    con.commit()


# ------------------проверка ожидания                   ------------------
def check_wait(user_id: int) -> bool:
    cur.execute(f"SELECT is_requested FROM users where id = {user_id}")
    return cur.fetchone()[0]


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
    users = list(cur.fetchone()[0])
    text = "Список всех заявок:\n"

    for user in users:
        cur.execute(f"select first_name, last_name from users where id = {user}")
        data = cur.fetchone()
        text += f"id: {user} - {data[0]} {data[1]}\n"

    return text.strip()


# ------------------подтверждение запроса на вступление ------------------
def add_user_group(group_id: int, user_id: int):
    cur.execute(f"UPDATE users set group_id = {group_id} where id = {user_id}")
    con.commit()
    cur.execute(f"SELECT group_users_id from groups where group_id = {group_id}")
    data = list(cur.fetchone()[0])
    data.append(user_id)
    cur.execute(f"update groups set group_users_id = ARRAY{data} where group_id = {group_id}")
    con.commit()


# ------------------получение текста задачи            ------------------
def get_task(task_id: int) -> tuple[str, str]:
    cur.execute(f"select task, manual from questions where task_id = {task_id}")
    return cur.fetchone()


# ------------------привязка задачи к пользователю      ------------------
def task_bind(task_id: int, user_id: int):
    cur.execute(f"update users set task_id = {task_id} where id = {user_id}")
    con.commit()


# ------------------есть ли задача у участника          ------------------
def check_task(user_id: int) -> int:
    cur.execute(f"select task_id from users where id = {user_id}")
    result = cur.fetchone()[0]
    if not result:
        return 0
    return int(result)


# ------------------ проверка ответа                    ------------------
def check_answer(task_id: int, answer: str) -> bool:
    cur.execute(f"select answer from questions where task_id = {task_id}")
    correct = cur.fetchone()[0][0]
    return correct == answer


# ------------------ отвязка вопроса                    ------------------
def unbind_task(user_id):
    cur.execute(f"update users set task_id = null where id = {user_id}")
    con.commit()


# ------------------ получение количеста очков          ------------------
def get_points(task_id: int) -> int:
    cur.execute(f"select points from questions where task_id = {task_id}")
    return cur.fetchone()[0]


# ------------------ добавление очков                   ------------------
def add_points(group_id: int, points: int):
    cur.execute(f"select points from groups where group_id = {group_id}")
    data = cur.fetchone()[0] + points

    cur.execute(f"update groups set points = {data} where group_id = {group_id}")
    con.commit()


# ------------------ декримент кол-ва активаций         ------------------
def activation_decriment(task_id: int):
    cur.execute(f"select act_counts from questions where task_id = {task_id}")
    act_counts = cur.fetchone()[0] - 1
    cur.execute(f"update questions set act_counts = {act_counts} where task_id = {task_id}")


# ------------------ добавление решенных задач          ------------------
def add_ready_group_tasks(task_id: int, group_id: int):
    cur.execute(f"select ready_qs_id from groups where group_id = {group_id}")
    data = [i for i in cur.fetchone()[0] if i]
    data.append(task_id)
    cur.execute(f"update groups set ready_qs_id = ARRAY{data} where group_id = {group_id}")
    con.commit()


# ------------------ решила ли группа уже задачу         ------------------
def check_group_task(task_id: str, group_id: int) -> bool:
    cur.execute(f"select ready_qs_id from groups where group_id = {group_id}")
    data = [i for i in cur.fetchone()[0] if i]
    return int(task_id) in data


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


# ------------------ уникальные задачи                  ------------------
def without_answer(user_id: int, task_id: int) -> int:
    group_id = get_group_id(user_id)
    points = get_points(task_id)
    add_points(group_id, points)
    activation_decriment(task_id)
    add_ready_group_tasks(task_id, group_id)
    return points


# ------------------ количесто очков группы            ------------------
def get_group_points(group_id: int) -> int:
    cur.execute(f"select points from groups where group_id = {group_id}")
    points = cur.fetchone()[0]
    return points


# ------------------ кол-во решенных задач              ------------------
def get_task_count(group_id: int) -> int:
    cur.execute(f"select ready_qs_id from groups where group_id = {group_id}")
    return len(cur.fetchone()[0])

# ------------------ создание бота и диспетчера         ------------------
bot = Bot(TOKEN)
dp = Dispatcher(bot)


# ------------------ начало общения                     ------------------
@dp.message_handler(commands=["start"])
async def starting(message: types.Message):
    u_id = message.chat.id
    if check_id(u_id):
        username = get_uname(u_id)
        print(username)
        await bot.send_message(u_id, f"Приветствуем, {username}, чтобы вывести список доступных команд, напишите /help")
    else:
        await bot.send_message(u_id, "Приветствуем, чтобы продолжить, введите /reg"
                                     " и через пробел имя и фамилию, для регистрации")


# ------------------ регистрация пользователя           ------------------
@dp.message_handler(commands=["reg"])
async def register(message: types.Message):
    u_id = message.chat.id
    if check_id(u_id):
        await bot.send_message(u_id, f"Вы уже зарегестрированны по именем {get_uname(u_id)}")
    else:
        if len(message.text.split()) != 3:
            await bot.send_message(u_id, "Введите /reg и через пробел имя до 255 символов")
        _, first_name, last_name = message.text.split()

        if len(first_name) > 255 or len(last_name) > 255:
            await bot.send_message(u_id, "Имя и фамилия должны быть не больше 255 символов")
        else:
            set_name(u_id, first_name, last_name)
            await bot.send_message(u_id, "Регистрация прошла успешно")


# ------------------ вывод списка доступных команд    ------------------
@dp.message_handler(commands=["help"])
async def print_help(message: types.Message):
    u_id = message.chat.id
    if check_id(u_id):
        if check_group(u_id):
            if check_role(u_id):
                text = "Список доступных команд:\n" \
                       "/statistics - вывод статистики команды\n" \
                       "/admin - выводит контакт для связи с админом\n" \
                       "/task <task_id> - вывод задачи\n" \
                       "/answer <answer> - ответ к задаче, отвечать могут только капитаны\n"
            else:
                text = "Список доступных команд\n" \
                       "/statistics - вывод статистики команды\n" \
                       "/users - вывод участников группы\n" \
                       "/group_settings - вывод информации о группе\n" \
                       "/mail - вывод запросов на вступление\n" \
                       "/ok <user_id> - подтверждение запроса на вступление\n" \
                       "/no <user_id> - отклонение запроса на вступление\n" \
                       "/kick <user_id> - убрать из группы пользователя\n" \
                       "/task <task_id> - вывод задачи\n" \
                       "/answer <answer> - ответ к задаче, отвечать могут только капитаны\n" \
                       "/exit - уйти с решения текущей задачи\n" \
                       "/admin - выводит контакт для связи с админом"
        else:
            text = "Список доступных команд:\n" \
                   f"/create <group_name> - создание команды (не более {MAX_GROUP_USERS}-ти человек)\n" \
                   "/entry <group_id> - войти в группу по id (id есть у капитана)\n" \
                   "/admin - выводит контакт для связи с админом"
    else:
        text = "Список доступных команд:\n" \
               "/reg <Имя> <Фамилия> - регистрация пользователя в системе\n" \
               "/admin - выводит контакт для связи с админом"

    await bot.send_message(u_id, text)


# ------------------ связь с админом                  ------------------
@dp.message_handler(commands=["admin"])
async def admin_contact(message: types.Message):
    text = f"Контакты для связи с админами:\n" \
           f"{admins['Захар']} - Захар\n" \
           f"{admins['Александр']} - Александр"
    await bot.send_message(message.chat.id, text)


# ------------------ создание группы                  ------------------
@dp.message_handler(commands=["create"])
async def group_create(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):
        new_group_id = generate_group_id()
        _, group_name = message.text.split()
        new_group(new_group_id, group_name, u_id)
        change_role(u_id)
        set_group_id(u_id, new_group_id)
        await bot.send_message(u_id, f"Группа {group_name} успешно создана")
    else:
        await bot.send_message(u_id, "Команду могут использовать только игроки")


# ------------------  вывод настроек группы           ------------------
@dp.message_handler(commands=["group_settings"])
async def print_settings(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):
        await bot.send_message(u_id, "Команду может использовать только капитан")
    else:
        group_id = get_group_id(u_id)
        users_count = get_users_count(group_id)
        text = f"Настройки группы:\n" \
               f"id группы: {group_id}\n" \
               f"Количество пользователей {users_count} из {MAX_GROUP_USERS}"

        await bot.send_message(u_id, text)


# ------------------  вывод участников команды           ------------------
@dp.message_handler(commands=["users"])
async def print_users(message: types.Message):
    u_id = message.chat.id
    if check_role(u_id):
        await bot.send_message(u_id, "Команду может использовать только капитан")
    else:
        group_id = get_group_id(u_id)
        text = get_users(group_id)

        await bot.send_message(u_id, text)


# ------------------отправка заявки на вступление в группу------------------
@dp.message_handler(commands=["entry"])
async def entry(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):

        if check_group(u_id):
            await bot.send_message(u_id, "Вы уже в группе")
        else:
            _, group_id = message.text.split()
            if check_wait(u_id):
                await bot.send_message(u_id, "Ожидайте подтверждения запроса от группы")
            else:
                if check_users_count(group_id) < 4:
                    new_group_requests(group_id, u_id)
                    set_wait_true(u_id)
                    await bot.send_message(u_id, "Заявка отправлена, ожидайте подтверждения")
                else:
                    await bot.send_message(u_id, "Количество участников достигло лимита")
    else:
        await bot.send_message(u_id, "Команду могут использовать только игроки")


# ------------------вывод всех входящих заявок            ------------------
@dp.message_handler(commands=["mail"])
async def mail(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):
        await bot.send_message(u_id, "Команду может использовать только капитан")
    else:
        group_id = get_group_id(u_id)
        text = get_users_from_requests(group_id)
        await bot.send_message(u_id, text)


# ------------------добавление нового участника          ------------------
@dp.message_handler(commands=["ok"])
async def agree_request(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):
        await bot.send_message(u_id, "Команду может использовать только капитан")
    else:
        group_id = get_group_id(u_id)
        if check_users_count(group_id) == 4:
            await bot.send_message(u_id, "Число участников достигло лимита")
        else:
            _, new_u_id = message.text.split()
            add_user_group(group_id, new_u_id)

            user = get_uname(new_u_id)
            group_name = get_group_name(group_id)

            await bot.send_message(u_id, f"Теперь {''.join(user)} в вашей группе")
            await bot.send_message(new_u_id, f"Теперь вы в группе:\n id: {group_id}\n Имя: {group_name}")

            cur.execute(f"update users set is_requested = false where id = {new_u_id}")
            con.commit()
            cur.execute(f"select requests from groups where group_id = {group_id}")
            data = list(cur.fetchone()[0])
            data.remove(int(new_u_id))
            cur.execute(f"update groups set requests = ARRAY{data}::integer[] where group_id = {group_id}")
            con.commit()


# ------------------отклонение запроса на вступление     ------------------
@dp.message_handler(commands=["no"])
async def disagree_request(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):
        await bot.send_message(u_id, "Команду может использовать только капитан")
    else:
        group_id = get_group_id(u_id)

        _, new_u_id = message.text.split()

        cur.execute(f"select requests from groups where group_id = {group_id}")
        data = list(cur.fetchone()[0])
        data.remove(int(new_u_id))
        cur.execute(f"update groups set requests = ARRAY{data}::integer[] where group_id = {group_id}")
        con.commit()

        await bot.send_message(new_u_id, f"Ваш запрос на вступление в группу {group_id} отклонен")
        name = get_uname(new_u_id)
        await bot.send_message(u_id, f"Запрос на вступление для {name} отклонен")


# ------------------выгон участника из группы            ------------------
@dp.message_handler(commands=["kick"])
async def kick_user(message: types.Message):
    u_id = message.chat.id

    if check_role(u_id):
        await bot.send_message(u_id, "Команду может использовать только капитан")
    else:
        _, target_u_id = message.text.split()
        group_id = get_group_id(u_id)

        cur.execute(f"select group_users_id from groups where group_id = {group_id}")
        data = list(cur.fetchone()[0])
        data.remove(int(target_u_id))

        cur.execute(f"update groups set group_users_id = ARRAY{data}::integer[] where group_id = {group_id}")
        con.commit()

        cur.execute(f"update users set group_id = null where id = {target_u_id}")
        con.commit()

        name = get_uname(target_u_id)

        await bot.send_message(u_id, f"{name} был выгнан из группы")
        await bot.send_message(target_u_id, f"Вы были выгнаны из группы\n"
                                            f"id: {group_id}\n"
                                            f"Имя: {get_group_name(group_id)}")


# ------------------вывод текста задачи            ------------------
@dp.message_handler(commands=["task"])
async def print_task(message: types.Message):
    u_id = message.chat.id
    _, task_id = message.text.split()

    if check_task_type(task_id):
        if check_task(u_id) != 0:
            await bot.send_message(u_id, f"Вы уже решаете задачу id: {check_task(u_id)}")
            task_text, task_manual = get_task(check_task(u_id))
            if task_manual != "nan":
                await bot.send_message(u_id, "Текст задачи: \n" + task_text)
                await bot.send_message(u_id, "Справочная информация: \n" + task_manual)
            else:
                await bot.send_message(u_id, "Текст задачи: \n" + task_text)
        else:

            group_id = get_group_id(u_id)
            if check_group_task(task_id, group_id):
                await bot.send_message(u_id, "Вы уже решали эту задачу")
            else:
                if check_task_act_counts(task_id):
                    task_text, task_manual = get_task(int(task_id))
                    task_bind(task_id, u_id)
                    print(task_text, task_manual)
                    if task_manual != "nan":
                        await bot.send_message(u_id, "Текст задачи: \n" + task_text)
                        await bot.send_message(u_id, "Справочная информация: \n" + task_manual)
                    else:
                        await bot.send_message(u_id, "Текст задачи: \n" + task_text)
                else:
                    await bot.send_message(u_id, "Эту задачу уже нельзя решить")
    else:
        points = without_answer(u_id, task_id)
        await bot.send_message(u_id, f"Вы нашли {points} баллов для команды")


# ------------------ ответ на задачу                ------------------
@dp.message_handler(commands=["answer"])
async def send_answer(message: types.Message):
    u_id = message.chat.id

    if check_task(u_id) == 0:
        await bot.send_message(u_id, "У вас нет текущей задачи")
    else:
        _, answer = message.text.split()
        task_id = check_task(u_id)
        if check_answer(task_id, answer.lower()):
            group_id = get_group_id(u_id)

            points = get_points(task_id)
            add_points(group_id, points)
            activation_decriment(task_id)
            add_ready_group_tasks(task_id, group_id)
            unbind_task(u_id)

            await bot.send_message(u_id, f"Правильный ответ, вы получили {points} баллов\n"
                                         f"Теперь вы можете решать другие задачи")
        else:
            await bot.send_message(u_id, "Неправильный ответ")


# ------------------ решать другие задачи           ------------------
@dp.message_handler(commands=["exit"])
async def task_exit(message: types.Message):
    u_id = message.chat.id
    _, task_id = message.text.split()

    unbind_task(u_id)

    await bot.send_message(u_id, "Теперь вы можете решать другие задачи")


# ------------------ статистика команды             ------------------
@dp.message_handler(commands=["statistics"])
async def group_statistics(message: types.Message):
    u_id = message.chat.id
    group_id = get_group_id(u_id)
    users_count = get_users_count(group_id)
    group_points = get_group_points(group_id)
    task_count = get_task_count(group_id)
    group_name = get_group_name(group_id)

    sep = "-" * 40 + "\n"
    pre_head = f"Название группы: {group_name}\n"
    head = "*** Статистика группы ***\n"
    part_1 = f"Количество пользователей: {users_count}/{MAX_GROUP_USERS}\n"
    part_2 = get_users(group_id) + "\n"
    part_3 = f"Количество очков: {group_points}\n"
    part_4 = f"Количество решенных задач: {task_count}\n"

    data_text = [head, pre_head, part_1, part_2, part_3, part_4]

    text = sep.join(data_text)

    await bot.send_message(u_id, text)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=print("все готово"))
