import threading
import time
from datetime import datetime
import json
import os
from pynput import keyboard, mouse
import getpass

# Глобальные переменные
key_count = 0
mouse_count = 0
username = ""
is_running = True
license_start_time = time.time()
license_duration = 30 * 60  # 30 минут в секундах
license_valid = True

# Пути к файлам
DATA_FILE = "key_press_data.json"
LOG_FILE = "user_actions.log"

# Авторизация
def register():
    username = input("Введите новое имя пользователя: ")
    password = getpass.getpass("Введите новый пароль: ")
    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    users[username] = password
    with open("users.json", "w") as f:
        json.dump(users, f)
    print("Регистрация успешна!")
    return username

def login():
    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    while True:
        username = input("Введите имя пользователя: ")
        password = getpass.getpass("Введите пароль: ")
        if username in users and users[username] == password:
            print("Вход выполнен успешно!")
            return username
        print("Неверные данные. Попробуйте еще раз.")

# Функция логирования
def log_action(action, is_error=False):
    log_type = "ERROR" if is_error else "INFO"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{log_type}] [{timestamp}] [{username}] {action}\n")

# Поток автосохранения данных
def autosave_data():
    global key_count, mouse_count
    while is_running:
        try:
            data = {"username": username, "key_count": key_count, "mouse_count": mouse_count}
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
            log_action("Данные сохранены в файл")
        except Exception as e:
            log_action(f"Ошибка при сохранении данных: {str(e)}", is_error=True)
        time.sleep(5)  # Сохранение каждые 5 секунд

# Поток проверки лицензии
def check_license():
    global is_running, license_valid
    while is_running:
        elapsed = time.time() - license_start_time
        if elapsed > license_duration:
            license_valid = False
            print("Пробная лицензия истекла! Приобретите лицензионный ключ.")
            is_running = False
        time.sleep(1)

# Обработчик клавиатуры
def on_key_press(key):
    global key_count, is_running
    if not is_running:
        return False
    try:
        key_count += 1
        log_action(f"Нажата клавиша: {str(key)}")
        print(f"Нажатий клавиш: {key_count}, Кликов мыши: {mouse_count}")
    except Exception as e:
        log_action(f"Ошибка при обработке нажатия клавиши: {str(e)}", is_error=True)

# Обработчик мыши
def on_click(x, y, button, pressed):
    global mouse_count, is_running
    if not is_running:
        return False
    if pressed:
        mouse_count += 1
        log_action(f"Клик мыши: {str(button)}")
        print(f"Нажатий клавиш: {key_count}, Кликов мыши: {mouse_count}")

# Основная функция
def main():
    global username, is_running
    print("1. Регистрация\n2. Вход")
    choice = input("Выберите опцию (1/2): ")
    if choice == "1":
        username = register()
    else:
        username = login()

    # Запуск фоновых потоков
    threading.Thread(target=autosave_data, daemon=True).start()
    threading.Thread(target=check_license, daemon=True).start()

    # Запуск слушателей ввода
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

    log_action("Программа запущена")
    try:
        while is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        log_action("Программа завершена пользователем")
        is_running = False
    finally:
        keyboard_listener.stop()
        mouse_listener.stop()

if __name__ == "__main__":
    main()