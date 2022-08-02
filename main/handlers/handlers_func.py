from main.create_bot import *
from main.users import *
from main.groups import *
from main.tasks import *
from main.config import *
from main.admins import *
from aiogram import types
from random import choice
from datetime import *
from main.keyboards import *

GAME_STATE = "not started"


# ------------------ уникальные задачи                  ------------------
def without_answer(user_id: int, task_id: int) -> int:
    group_id = get_group_id(user_id)
    points = get_points(task_id)
    add_points(group_id, points)
    activation_decriment(task_id)
    add_ready_group_tasks(task_id, group_id)
    return points


# ------------------ начало общения                     ------------------
@dp.message_handler(commands=["start"])
async def starting(message: types.Message):
    u_id = message.chat.id
    sticker = choice(STICKERS["start"])
    try:
        if check_id(u_id):
            username = get_uname(u_id)
            await bot.send_message(u_id, f"Приветствуем, {username}, "
                                         f"чтобы вывести список доступных команд, напишите /help")
            await bot.send_sticker(u_id, sticker)
        else:
            await bot.send_message(u_id, "Приветствуем, чтобы продолжить, введите /reg"
                                         " и через пробел имя и фамилию, для регистрации")
            await bot.send_sticker(u_id, sticker)
    except:
        await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------ регистрация пользователя           ------------------
@dp.message_handler(commands=["reg"])
async def register(message: types.Message):
    u_id = message.chat.id

    if GAME_STATE == "not started":
        try:
            if can_use(u_id, "/reg"):
                if len(message.text.split()) < 3:
                    await bot.send_message(u_id, "Введите /reg и через пробел имя и фамилию до 255 символов")
                else:
                    _, first_name, last_name = message.text.split()

                    if len(first_name) > 255 or len(last_name) > 255:
                        await bot.send_message(u_id, "Имя и фамилия должны быть не больше 255 символов")
                    else:
                        set_name(u_id, first_name, last_name)
                        await bot.send_message(u_id, "Регистрация прошла успешно")
            else:

                await bot.send_message(u_id, f"Вы уже зарегестрированны по именем {get_uname(u_id)}")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------ вывод списка доступных команд    ------------------
@dp.message_handler(commands=["help"])
async def print_help(message: types.Message):
    u_id = message.chat.id
    try:
        if check_id(u_id):
            if check_group(u_id):
                if check_role(u_id):
                    text = "Список доступных команд:\n" \
                           "/statistics - вывод статистики команды\n" \
                           "/admin - выводит контакт для связи с админом\n" \
                           "/task <task_id> - вывод задачи\n" \
                           "/profile - ваш профиль\n" \
                           "/leave - покинуть группу"
                else:
                    text = "Список доступных команд\n" \
                           "/statistics - вывод статистики команды\n" \
                           "/users - вывод участников группы\n" \
                           "/group_info - вывод информации о группе\n" \
                           "/kick <user_id> - убрать из группы пользователя\n" \
                           "/task <task_id> - вывод задачи\n" \
                           "/answer <answer> - ответ к задаче, отвечать могут только капитаны\n" \
                           "/exit - уйти с решения текущей задачи\n" \
                           "/admin - выводит контакт для связи с админом\n" \
                           "/profile - ваш профиль\n" \
                           "/leave - покинуть группу"
            else:
                text = "Список доступных команд:\n" \
                       f"/create <group_name> - создание команды (не более {MAX_GROUP_USERS}-ти человек)\n" \
                       "/invite <group_id> - войти в группу по id (id есть у капитана)\n" \
                       "/admin - выводит контакт для связи с админом\n" \
                       "/profile - ваш профиль"
        else:
            text = "Список доступных команд:\n" \
                   "/reg <Имя> <Фамилия> - регистрация пользователя в системе\n" \
                   "/admin - выводит контакт для связи с админом"

        await bot.send_message(u_id, text)
    except:
        await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------ связь с админом                  ------------------
@dp.message_handler(commands=["admin"])
async def admin_contact(message: types.Message):
    try:
        text = f"Контакты для связи с админами:\n" \
               f"{admins['Захар']} - Захар\n" \
               f"{admins['Александр']} - Александр"
        await bot.send_message(message.chat.id, text)
    except:
        await bot.send_message(message.chat.id,
                               "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------ создание группы                  ------------------
@dp.message_handler(commands=["create"])
async def group_create(message: types.Message):
    u_id = message.chat.id

    if GAME_STATE == "not started":

        try:
            if can_use(u_id, "/create"):
                new_group_id = generate_group_id()
                if len(message.text.split()) != 2:
                    await bot.send_message(u_id, "Напишите  /create и через пробел имя команды")
                else:
                    _, group_name = message.text.split()

                    new_group(new_group_id, group_name, u_id)
                    change_role(u_id)
                    set_group_id(u_id, new_group_id)
                    await bot.send_message(u_id, f"Группа {group_name} успешно создана")
            else:
                await bot.send_message(u_id, "Команду могут использовать только игроки")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------  вывод настроек группы           ------------------
@dp.message_handler(commands=["group_info"])
async def print_settings(message: types.Message):
    u_id = message.chat.id
    try:
        if can_use(u_id, "/group_info"):
            group_id = get_group_id(u_id)
            users_count = get_users_count(group_id)
            text = f"Информация о группе:\n" \
                   f"id группы: {group_id}\n" \
                   f"Количество пользователей {users_count} из {MAX_GROUP_USERS}"

            await bot.send_message(u_id, text)
        else:
            await bot.send_message(u_id, "Команду может использовать только капитан")
    except:
        await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------  вывод участников команды           ------------------
@dp.message_handler(commands=["users"])
async def print_users(message: types.Message):
    u_id = message.chat.id

    try:
        if can_use(u_id, "/users"):
            group_id = get_group_id(u_id)
            text = get_users(group_id)

            await bot.send_message(u_id, text)

        else:
            await bot.send_message(u_id, "Команду может использовать только капитан")
    except:
        await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------отправка заявки на вступление в группу------------------
@dp.message_handler(commands=["invite"])
async def entry(message: types.Message):
    u_id = message.chat.id

    if GAME_STATE == "not started":

        try:
            if can_use(u_id, "/invite"):
                if check_group(u_id):
                    await bot.send_message(u_id, "Вы уже в группе")
                else:
                    if len(message.text.split()) != 2:
                        await bot.send_message(u_id, "Напишите /invite и через пробел id команды")
                    else:
                        _, group_id = message.text.split()

                        if check_group_id(group_id):
                            if check_wait(u_id):
                                await bot.send_message(u_id, "Ожидайте подтверждения запроса от группы")
                            else:
                                if check_users_count(group_id) < 4:
                                    new_group_requests(group_id, u_id)
                                    set_wait_true(u_id)
                                    await bot.send_message(u_id, "Заявка отправлена, ожидайте подтверждения")

                                    capitan = get_capitan(group_id)
                                    await bot.send_message(capitan, f"id: {u_id}\n"
                                                                    f"Имя: {get_uname(u_id)}\n"
                                                                    f"Хочет вступить в вашу группу", reply_markup=ar_kb)

                                else:
                                    await bot.send_message(u_id, "Количество участников достигло лимита")
                        else:
                            await bot.send_message(u_id, "Убедитесь в правильности написания id группы")
            else:
                await bot.send_message(u_id, "Команду могут использовать только игроки")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------добавление нового участника          ------------------
@dp.message_handler(commands=["ok"])
async def agree_request(message: types.Message):
    u_id = message.chat.id
    if GAME_STATE == "not started":
        try:
            if not can_use(u_id, "/ok"):
                await bot.send_message(u_id, "Команду может использовать только капитан")
            else:
                group_id = get_group_id(u_id)
                if check_users_count(group_id) == 4:
                    await bot.send_message(u_id, "Число участников достигло лимита")
                else:
                    if len(message.text.split()) != 2:
                        await bot.send_message(u_id, "Напишите /ok и через пробел id участника")
                    else:
                        _, new_u_id = message.text.split()

                        if check_id(new_u_id):
                            if check_in_mail(group_id, new_u_id):
                                if not check_group(new_u_id):
                                    add_user_group(group_id, new_u_id)

                                    user = get_uname(new_u_id)
                                    group_name = get_group_name(group_id)

                                    await bot.send_message(u_id, f"Теперь {''.join(user)} в вашей группе")
                                    await bot.send_message(new_u_id, f"Теперь вы в группе:\n id: {group_id}\n Имя: {group_name}")

                                    set_wait_false(new_u_id)
                                    cur.execute(f"select requests from groups where group_id = {group_id}")
                                    data = list(cur.fetchone()[0])
                                    data.remove(int(new_u_id))
                                    cur.execute(f"update groups set requests = ARRAY{data}::integer[] where group_id = {group_id}")
                                    con.commit()
                                else:
                                    await bot.send_message(u_id, f"Данный участник находится в группе")
                            else:
                                await bot.send_message(u_id, "От данного участника нет запросов на вступление")
                        else:
                            await bot.send_message(u_id, "Убедитесь в правильности написания id участнкиа")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------отклонение запроса на вступление     ------------------
@dp.message_handler(commands=["no"])
async def disagree_request(message: types.Message):
    u_id = message.chat.id
    if GAME_STATE == "not started":
        try:
            if not can_use(u_id, "/no"):
                await bot.send_message(u_id, "Команду может использовать только капитан")
            else:
                group_id = get_group_id(u_id)
                if len(message.text.split()) != 2:
                    await bot.send_message(u_id, "Напишите /no и через пробел id участника")
                else:
                    _, new_u_id = message.text.split()
                    if not check_group(new_u_id):
                        if check_in_mail(group_id, new_u_id):
                            if check_id(new_u_id):
                                cur.execute(f"select requests from groups where group_id = {group_id}")
                                data = list(cur.fetchone()[0])
                                data.remove(int(new_u_id))
                                cur.execute(f"update groups set requests = ARRAY{data}::integer[] where group_id = {group_id}")
                                con.commit()

                                await bot.send_message(new_u_id, f"Ваш запрос на вступление в группу отклонен")
                                set_wait_false(new_u_id)
                                name = get_uname(new_u_id)
                                await bot.send_message(u_id, f"Запрос на вступление для {name} отклонен")
                            else:
                                await bot.send_message(u_id, "Убедитесь в правильности написания id участнкиа")
                        else:
                            await bot.send_message(u_id, "от данного участника нет запросов")
                    else:
                        await bot.send_message(u_id, "Данный участник находится в группе")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------выгон участника из группы            ------------------
@dp.message_handler(commands=["kick"])
async def kick_user(message: types.Message):
    u_id = message.chat.id
    if GAME_STATE == "not started":
        try:
            if not can_use(u_id, "/kick"):
                await bot.send_message(u_id, "Команду может использовать только капитан")
            else:
                if len(message.text.split()) != 2:
                    await bot.send_message(u_id, "Напишите /kick и через пробел id участнкиа")
                else:
                    _, target_u_id = message.text.split()
                    if check_group(target_u_id):
                        group_id = get_group_id(u_id)
                        if check_in_your_group(group_id, target_u_id):
                            if check_id(target_u_id):
                                group_id = get_group_id(u_id)

                                cur.execute(f"select group_users_id from groups where group_id = {group_id}")
                                data = list(cur.fetchone()[0])
                                data.remove(int(target_u_id))

                                cur.execute(
                                    f"update groups set group_users_id = ARRAY{data}::integer[] where group_id = {group_id}")
                                con.commit()

                                cur.execute(f"update users set group_id = null where id = {target_u_id}")
                                con.commit()

                                name = get_uname(target_u_id)

                                await bot.send_message(u_id, f"{name} был выгнан из группы")

                                change_role_true(target_u_id)

                                await bot.send_message(target_u_id, f"Вы были выгнаны из группы")
                            else:
                                await bot.send_message(u_id, "Убедитесь в правильности написания id участника")
                        else:
                            await bot.send_message(u_id, "Участник не в вашей группе")
                    else:
                        await bot.send_message(u_id, "Участника нет в группе")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------вывод текста задачи            ------------------
@dp.message_handler(commands=["task"])
async def print_task(message: types.Message):
    u_id = message.chat.id
    if GAME_STATE == "started":
        try:
            if can_use(u_id, "/task"):
                group_id = get_group_id(u_id)
                if check_cooldown(group_id):
                    if len(message.text.split()) != 2:
                        await bot.send_message(u_id, "Напишите /task и через пробел id задачи")
                    else:
                        _, task_id = message.text.split()

                        if check_task_id(task_id):

                            if check_task_type(int(task_id)):

                                if check_role(u_id):
                                    await bot.send_message(u_id, "Решать такие задачи может только капитан")
                                else:
                                    if check_task(u_id) != 0:
                                        await bot.send_message(u_id, f"Вы уже решаете задачу id: {check_task(u_id)}\n"
                                                                     f"ищите условие выше")
                                    else:
                                        group_id = get_group_id(u_id)
                                        if check_group_task(task_id, group_id):
                                            await bot.send_message(u_id, "Вы уже решали эту задачу")
                                        else:
                                            if check_task_act_counts(task_id):
                                                task_text, task_manual = get_task(int(task_id))
                                                task_bind(task_id, u_id)
                                                if task_manual != "nan":
                                                    await bot.send_message(u_id, "Текст задачи: \n" + task_text)
                                                    await bot.send_message(u_id, "Справочная информация: \n" + task_manual)
                                                else:
                                                    await bot.send_message(u_id, "Текст задачи: \n" + task_text)
                                                await bot.send_message(u_id, "Чтобы ответить напишите: \n"
                                                                             "/answer и через пробел ответ")
                                            else:
                                                await bot.send_message(u_id, "Эту задачу уже нельзя решить")
                            else:
                                if check_group_task(task_id, group_id):
                                    await bot.send_message(u_id, "Вы уже решали эту задачу")
                                else:
                                    if check_task_act_counts(task_id):
                                        points = without_answer(u_id, task_id)
                                        await bot.send_message(u_id, f"Вы нашли {points} баллов для команды")
                                    else:
                                        await bot.send_message(u_id, "Эту задачу уже нельзя решить")
                        else:
                            await bot.send_message(u_id, "Убедитесь в правильности написания id задачи")
                else:
                    await bot.send_message(u_id, "Подождите немного, чтобы решать дальше")
            else:
                await bot.send_message(u_id, "Команду могут использовать игроки или капитаны команд")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Команду можно использовать только во время игры")


# ------------------ ответ на задачу                ------------------
@dp.message_handler(commands=["answer"])
async def send_answer(message: types.Message):
    u_id = message.chat.id
    if GAME_STATE == "started":
        try:
            if can_use(u_id, "/answer"):
                if check_task(u_id) == 0:
                    await bot.send_message(u_id, "У вас нет текущей задачи")
                else:
                    if len(message.text.split()) < 2:
                        await bot.send_message(u_id, "Напишите /answer и через пробел ответ")
                    else:
                        answer = message.text.replace("/answer ", "").lower()
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

                            set_cooldown(group_id)
                        else:
                            await bot.send_message(u_id, "Неправильный ответ")
            else:
                await bot.send_message(u_id, "Команду могут использовать только капитаны")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Команду можно использовать только во время игры")


# ------------------ решать другие задачи           ------------------
@dp.message_handler(commands=["exit"])
async def task_exit(message: types.Message):
    u_id = message.chat.id

    if GAME_STATE == "started":
        try:
            if can_use(u_id, "/exit"):
                unbind_task(u_id)

                await bot.send_message(u_id, "Теперь вы можете решать другие задачи")
            else:
                await bot.send_message(u_id, "Команду могут использовать только капитаны")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Команду можно использовать только во время игры")


# ------------------ статистика команды             ------------------
@dp.message_handler(commands=["statistics"])
async def group_statistics(message: types.Message):
    u_id = message.chat.id

    try:
        if can_use(u_id, "/statistics"):
            group_id = get_group_id(u_id)
            users_count = get_users_count(group_id)
            group_points = get_group_points(group_id)
            task_count = get_task_count(group_id)
            group_name = get_group_name(group_id)

            sep = "-" * 40 + "\n"

            if check_role(u_id):
                pre_head = f"Название группы: {group_name}\n"
                head = "*** Статистика группы ***\n"
                part_1 = f"Количество пользователей: {users_count}/{MAX_GROUP_USERS}\n"
                part_3 = f"Количество очков: {group_points}\n"
                part_4 = f"Количество решенных задач: {task_count}\n"

                data_text = [head, pre_head, part_1, part_3, part_4]
                text = sep.join(data_text)

                await bot.send_message(u_id, text)

            else:

                pre_head = f"Название группы: {group_name}\n"
                head = "*** Статистика группы ***\n"
                part_1 = f"Количество пользователей: {users_count}/{MAX_GROUP_USERS}\n"
                part_2 = get_users(group_id) + "\n"
                part_3 = f"Количество очков: {group_points}\n"
                part_4 = f"Количество решенных задач: {task_count}\n"

                data_text = [head, pre_head, part_1, part_2, part_3, part_4]

                text = sep.join(data_text)

                await bot.send_message(u_id, text)
        else:
            await bot.send_message(u_id, "Команду могут использовать капитаны или участники команд")
    except:
        await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------ профиль игрока                   ------------------
@dp.message_handler(commands=["profile"])
async def user_profile(message: types.Message):
    u_id = message.chat.id

    try:
        if can_use(u_id, "/profile"):
            name = get_uname(u_id)
            group_id = get_group_id(u_id)
            group_id_text = "отсутствует" if group_id is None else group_id
            wait = "ожидание" if check_wait(u_id) else "нет запросов на вступление"

            text = "Ваш профиль: \n" \
                   f"id: {u_id}\n" \
                   f"Имя: {name}\n" \
                   f"Группа: {group_id_text}\n" \
                   f"Запросы на вступление: {wait}"

            await bot.send_message(u_id, text)

        else:
            await bot.send_message(u_id, "Команду могут использовать только зарегестрированные пользователи")
    except:
        await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")


# ------------------ покидание группы игроком          ------------------
@dp.message_handler(commands=["leave"])
async def leave_group(message: types.Message):
    u_id = message.chat.id
    if GAME_STATE == "not started":
        try:
            if can_use(u_id, "/leave"):

                group_id = get_group_id(u_id)
                if check_role(u_id):
                    unbind_group(u_id, group_id)
                    await bot.send_message("Вы успешно покинули группу")
                else:

                    for user in disagree_requests(group_id):
                        set_wait_false(user)
                        await bot.send_message(user, "Заявка отклонена, т.к. группа была удалена")

                    for cur_user in send_warnings(group_id):
                        unbind_group(cur_user, group_id)
                        await bot.send_message(cur_user, "Группа была удалена")

                    delete_group(group_id)

                    await bot.send_message(u_id, "Группа была успешно удалена")
            else:
                await bot.send_message(u_id, "Команду могут использовать участники или капитаны групп")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------ админские хэндлеры        ------------------
@dp.message_handler(commands=['start_game'])
async def start_game(message: types.Message):
    global GAME_STATE

    u_id = message.chat.id

    if is_admin(u_id):
        GAME_STATE = "started"
        await bot.send_message(u_id, "Игра началась)))")

        for user in get_ids():
            await bot.send_message(user, "Игра началась)))")

    else:
        await bot.send_message(message.chat.id, "Я не знаю, что делать :(\n"
                                                "напиши /help, чтобы узнать, что я могу")


@dp.message_handler(commands=['end_game'])
async def start_game(message: types.Message):
    global GAME_STATE

    u_id = message.chat.id

    if is_admin(u_id):
        GAME_STATE = "finished"
        await bot.send_message(u_id, "Игра закончена!!!")

        for user in get_ids():
            await bot.send_message(user, "Игра закончена!!!")
    else:
        await bot.send_message(message.chat.id, "Я не знаю, что делать :(\n"
                                                "напиши /help, чтобы узнать, что я могу")


@dp.message_handler(commands=['restart_game'])
async def start_game(message: types.Message):
    global GAME_STATE

    u_id = message.chat.id

    if is_admin(u_id):
        GAME_STATE = "not started"
        await bot.send_message(u_id, "Игра была перезагружена")
    else:
        await bot.send_message(message.chat.id, "Я не знаю, что делать :(\n"
                                                "напиши /help, чтобы узнать, что я могу")


@dp.message_handler(commands=["game_state"])
async def print_game_state(message: types.Message):
    u_id = message.chat.id

    if is_admin(u_id):
        await bot.send_message(u_id, f"Состояние игры: {GAME_STATE}")
    else:
        await bot.send_message(u_id, "Я не знаю, что делать :(\n"
                                                "напиши /help, чтобы узнать, что я могу")


# ------------------ inline кнопки       ------------------
@dp.callback_query_handler(text="agree")
async def agree_req(query: types.CallbackQuery):
    u_id = query.message.chat.id
    if GAME_STATE == "not started":
        try:
            msg_text = query.message.text.split("\n")
            id_line = msg_text[0]
            new_u_id = int(id_line.replace("id: ", ""))


            group_id = get_group_id(u_id)

            if check_in_mail(group_id, new_u_id):
                if not check_group(new_u_id):
                    add_user_group(group_id, new_u_id)

                    user = get_uname(new_u_id)
                    group_name = get_group_name(group_id)

                    await bot.send_message(u_id, f"Теперь {''.join(user)} в вашей группе")
                    await bot.send_message(new_u_id, f"Теперь вы в группе:\n id: {group_id}\n Имя: {group_name}")

                    set_wait_false(new_u_id)
                    cur.execute(f"select requests from groups where group_id = {group_id}")
                    data = list(cur.fetchone()[0])
                    data.remove(int(new_u_id))
                    cur.execute(f"update groups set requests = ARRAY{data}::integer[] where group_id = {group_id}")
                    con.commit()
                else:
                    await bot.send_message(u_id, f"Данный участник находится в группе")
            else:
                await bot.send_message(u_id, "От данного участника нет запросов на вступление")
        except:
            await bot.send_message(u_id, "Произошла непридвиденная ошибка, свяжитесь с админами, написав команду /admin")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


@dp.callback_query_handler(text="disagree")
async def disagree_req(query: types.CallbackQuery):
    u_id = query.message.chat.id

    if GAME_STATE == "not started":
        try:
            group_id = get_group_id(u_id)
            msg_text = query.message.text.split("\n")
            id_line = msg_text[0]
            new_u_id = int(id_line.replace("id: ", ""))

            if check_in_mail(group_id, new_u_id):
                if not check_group(new_u_id):
                    add_user_group(group_id, new_u_id)

                    user = get_uname(new_u_id)
                    group_name = get_group_name(group_id)

                    await bot.send_message(u_id, f"Теперь {''.join(user)} в вашей группе")
                    await bot.send_message(new_u_id, f"Теперь вы в группе:\n id: {group_id}\n Имя: {group_name}")

                    set_wait_false(new_u_id)
                    cur.execute(f"select requests from groups where group_id = {group_id}")
                    data = list(cur.fetchone()[0])
                    data.remove(int(new_u_id))
                    cur.execute(f"update groups set requests = ARRAY{data}::integer[] where group_id = {group_id}")
                    con.commit()
                else:
                    await bot.send_message(u_id, f"Данный участник находится в группе")
            else:
                await bot.send_message(u_id, "От данного участника нет запросов на вступление")
        except:
            await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")
    else:
        await bot.send_message(u_id, "Пока игра начата или закончена, нельзя использовать команду")


# ------------------ все кроме команд        ------------------
@dp.message_handler()
async def other(message: types.Message):
    await bot.send_message(message.chat.id, "Я не знаю, что делать :(\n"
                                            "напиши /help, чтобы узнать, что я могу")
