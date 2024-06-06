import requests
from bs4 import BeautifulSoup
import json


# функция находит ссылки на файлы, используя исходный URL.
def find_files_links(source_url):
    response = requests.get(source_url)  # получает HTTP-ответ от сервера
    soup = BeautifulSoup(response.text, 'html.parser')  # анализирует полученный HTML-код с помощью библиотеки BeautifulSoup

    # извлекает ссылки на файлы из найденных элементов <a>
    files_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('files/')]

    # возвращает список найденных ссылок на файлы
    return files_links


# объединяет базовый URL с каждой ссылкой на файл из списка files_links
def combine_base_url_with_files_links(base_url, files_links):
    combined_links = [base_url + link for link in files_links]
    return combined_links


# функция обрабатывает объединённые URL и извлекает данные из HTML-кода
def parse_combined_links(links):
    data = []
    # перебирает каждый URL из списка links
    for link in links:
        response = requests.get(link)  # получает HTTP-ответ от сервера для каждого URL
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


def run_parser():
    source_url = 'https://nfuunit.ru/timetable/fulltime/'
    files_links = find_files_links(source_url)
    combined_links = combine_base_url_with_files_links(source_url, files_links)
    parse_combined_links(combined_links)


if __name__ == "__main__":
    run_parser()