import parser
import the_parsing_script
import json
import threading

from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDSeparator

from plyer import notification
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Example(MDApp):
    def __init__(self):
        super().__init__()
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
            self.monitor_json_changes()
        except FileNotFoundError:
            # print("Ошибка при загрузке данных...")
            self.run_parser_in_background()

    def run_parser_in_background(self):
        """Запуск основного парсера в фоновом потоке"""
        self.show_loading_message()
        parser_thread = threading.Thread(target=self.run_parser)
        parser_thread.daemon = True
        parser_thread.start()

    def run_parser(self):
        """Запуск парсера"""
        parser.run_parser()
        self.load_data()
        self.hide_loading_message()

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
                if self.search_query.lower() in item['id'].lower() or self.search_query.lower() in item['text'].lower():
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
                        adaptive_height=True,
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

    def reload_data_and_notify(self):
        self.load_data()
        self.send_notification("Изменения в расписании")

    def send_notification(self, message):
        notification_title = "Расписание НФ УУНиТ"
        notification_text = message
        notification.notify(title=notification_title, message=notification_text)


if __name__ == "__main__":
    background_parser = threading.Thread(target=the_parsing_script.main_0)
    background_parser.daemon = True
    background_parser.start()
    Example().run()

