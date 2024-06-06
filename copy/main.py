import httpx
import schedule
from datetime import datetime
from bs4 import BeautifulSoup
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from kivy.lang import Builder
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDSeparator

from plyer import notification
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Example(MDApp):
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.screen = Builder.load_file('interface_app.kv')
        self.observer = None
        self.search_query = ""
        self.load_data()

    def build(self):
        self.theme_cls.theme_style = "Light"
        return self.screen

    def handle_search(self, query):
        """Обработка нажатия кнопки поиска"""
        self.search_query = query
        self.search_data()

    def load_data(self):
        """Загрузка данных из файла JSON"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.run_parser_script()
        except FileNotFoundError:
            # print("Ошибка при загрузке данных...")
            self.run_parser_in_background()

    def second_load_data(self):
        """Загрузка данных из файла JSON"""
        with open('data.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    async def run_other_script(self):
        # Код запуска скрипта
        print('работа парсера')
        await self.run_parser()
        print('работа парсера')
        self.second_load_data()
        print('загрузка данных')

    def check_time(self):
        # Получаем текущее время
        now = datetime.now()
        if now.minute % 5 == 0:
            # Если да, запускаем другой скрипт
            asyncio.run(self.run_other_script())

    def run_parser_script(self):
        # Вызываем run_other_script один раз сразу после запуска приложения
        # asyncio.run(self.run_other_script())
        # Планирование задачи на каждую минуту
        schedule.every(10).seconds.do(self.check_time)
        Clock.schedule_interval(lambda dt: schedule.run_pending(), 10)

    async def run_parser_in_background(self):
        """Запуск парсера в фоновом потоке"""
        self.show_loading_message()
        asyncio.run(self.run_parser())
        self.load_data()
        self.hide_loading_message()

    async def find_files_links(self, source_url):
        # функция находит ссылки на файлы, используя исходный URL.
        async with httpx.AsyncClient() as client:
            response = await client.get(source_url)  # получает HTTP-ответ от сервера
            soup = BeautifulSoup(response.text,
                                 'html.parser')  # анализирует полученный HTML-код с помощью библиотеки BeautifulSoup
            files_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('files/')]  # извлекает ссылки на файлы из найденных элементов <a>
        return files_links  # возвращает список найденных ссылок на файлы

    async def combine_base_url_with_files_links(self, base_url, files_links):
        # объединяет базовый URL с каждой ссылкой на файл из списка files_links
        combined_links = [base_url + link for link in files_links]
        return combined_links

    async def parse_combined_links(self, links):
        # функция обрабатывает объединённые URL и извлекает данные из HTML-кода
        data = []
        # перебирает каждый URL из списка links
        async with httpx.AsyncClient() as client:
            for link in links:
                response = await client.get(link)  # получает HTTP-ответ от сервера для каждого URL
                soup = BeautifulSoup(response.text, 'html.parser')  # анализирует полученный HTML-код.
                rows = soup.find_all('tr')  # находит все строки таблицы

                # перебирает каждую строку таблицы
                for row in rows:
                    cols = row.find_all('td')  # находит все столбцы таблицы
                    cell_data = {}
                    for col in cols:
                        if col.text != '':
                            # Проверяем наличие и значение интересующих атрибутов
                            if 'id' in col.attrs:
                                col_id = col['id']
                                col_id = col_id.rstrip()[:-1]
                                cell_data['id'] = col_id
                            if 'para' in col.attrs:
                                cell_data['para'] = col['para']
                            if 'day' in col.attrs:
                                cell_data['day'] = col['day']
                            if 'data' in col.attrs:
                                cell_data['data'] = col['data']
                            # Добавляем текст ячейки, если все интересующие атрибуты присутствуют
                            if all(key in cell_data for key in ['id', 'day', 'data', 'para']):
                                cell_data['text'] = col.text
                                data.append(cell_data)
                                cell_data = {}

        # Сохраняем данные
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        # print(f"Данные успешно сохранены в файл")
        return data

    async def run_parser(self):
        source_url = 'https://nfuunit.ru/timetable/fulltime/'
        files_links = await self.find_files_links(source_url)
        combined_links = await self.combine_base_url_with_files_links(source_url, files_links)
        await self.parse_combined_links(combined_links)

    def show_loading_message(self):
        """Отображение сообщения о загрузке данных"""
        self.loading_label = MDLabel(
            text="Подождите пока данные загружаются...",
            halign="center",
            size_hint_y=None
        )
        self.screen.ids.list_result.add_widget(self.loading_label)

    def hide_loading_message(self):
        """Скрытие сообщения о загрузке данных"""
        if self.loading_label:
            self.screen.ids.list_result.remove_widget(self.loading_label)

    def search_data(self):
        """Поиск данных по запросу"""
        grouped_results = {}
        for item in self.data:
            if self.search_query == "":
                error_label = MDLabel(
                    text="Введите данные для поиска",
                    size_hint_y=None,
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
                self.screen.ids.list_result.add_widget(error_label)
            else:
                if self.search_query.lower() == item['id'].lower() or self.search_query.lower() in item['id'].lower() or self.search_query.lower() in item['text'].lower():
                    id_item = item['id']
                    day = item['day']
                    data = item['data']
                    para = item['para']
                    text = item['text']

                    if day.strip():
                        # Группируем занятия по дню и дате
                        key = f"{day} - {data}"  # Используем день и дату в качестве ключа
                        if key not in grouped_results:
                            grouped_results[key] = []  # Инициализируем список занятий для этой даты и дня
                        grouped_results[key].append({
                            "day": day,
                            "data": data,
                            "para": para,
                            "class": id_item,
                            "text": text
                        })

            self.screen.ids.list_result.clear_widgets()  # Очищаем список перед показом расписания

        if not grouped_results:
            message_label = MDLabel(
                text="Ничего не найдено",
                size_hint_y=None,
                halign='center',
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1)
            )
            self.screen.ids.list_result.add_widget(message_label)
        else:
            # Отображаем дату и день, а затем занятия
            for (date_day, classes) in grouped_results.items():
                label_date_day = MDLabel(
                    text=date_day,
                    size_hint_y=None,
                    halign='center',
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)  # Цвет для даты и дня
                )
                self.screen.ids.list_result.add_widget(label_date_day)

                separator_day = MDSeparator(height="10dp")
                self.screen.ids.list_result.add_widget(separator_day)

                for class_ in classes:
                    label_class = MDLabel(
                        text=f"{class_['para']} : {class_['class']}",
                        adaptive_height=True,
                        theme_text_color="Custom",
                        text_color=(0, 0, 1, 1)  # Цвет для занятий
                    )
                    self.screen.ids.list_result.add_widget(label_class)

                    label_text = MDLabel(
                        text=f"{class_['text']}",
                        size_hint_y=None,
                        theme_text_color="Custom",
                        text_color=(0, 0, 0, 1)  # Цвет для занятий
                    )
                    self.screen.ids.list_result.add_widget(label_text)

                    separator = MDSeparator(height="10dp")
                    self.screen.ids.list_result.add_widget(separator)

    def monitor_json_changes(self, filepath='data.json'):
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = lambda event: self.reload_data_and_notify(event.src_path)
        if self.observer:
            self.observer.stop()
            self.observer.join()
        observer = Observer()
        observer.schedule(event_handler, filepath, recursive=False)
        observer.start()

    def reload_data_and_notify(self, filepath):
        self.load_data(filepath)
        self.send_notification("Изменения в расписании")

    def send_notification(self, message):
        notification_title = "Расписание НФ УУНиТ"
        notification_text = message
        notification.notify(title=notification_title, message=notification_text)


if __name__ == "__main__":
    Example().run()