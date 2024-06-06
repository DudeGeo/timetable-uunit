import schedule
from datetime import datetime
import parser
from kivy.clock import Clock


def run_other_script():
    # Код запуска скрипта
    # print('работа парсера')
    parser.run_parser()
    # print('работа парсера')


def check_time():
    # Получаем текущее время
    now = datetime.now()
    if now.minute % 5 == 0:
        run_other_script()


def main_0():
    # Вызываем run_other_script один раз сразу после запуска приложения
    # run_other_script()
    # Планирование задачи на каждые 10 секунд
    schedule.every(15).seconds.do(check_time)
    Clock.schedule_interval(lambda dt: schedule.run_pending(), 15)


if __name__ == "__main__":
    main_0()