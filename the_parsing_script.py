import schedule
import time
from datetime import datetime
import parser


def run_other_script():
    # Код запуска скрипта
    # print('работа парсера')
    parser.run_parser()
    # print('работа парсера')


def check_time():
    # Получаем текущее время
    now = datetime.now()
    if now.hour % 2 == 0 and now.minute % 10 == 0:
        # Если да, запускаем другой скрипт
        run_other_script()


def main():
    # Вызываем run_other_script один раз сразу после запуска приложения
    run_other_script()
    # Планирование задачи на каждую минуту
    schedule.every(60).seconds.do(check_time)
    while True:
        # Запуск всех задач, запланированных в schedule
        schedule.run_pending()
        # Ждем 1 минуту перед следующей проверкой
        time.sleep(60)


if __name__ == "__main__":
    main()