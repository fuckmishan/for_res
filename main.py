import asyncio
import sqlite3
from typing import List

class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    async def connect(self):
        # Изменено: использование метода row_factory для возвращения словаря, что упрощает получение данных
        self.connection = sqlite3.connect('notes.db')
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT)
        ''')

    async def disconnect(self):
        self.connection.close()

    async def add_note_to_db(self, note):
        self.cursor.execute('INSERT INTO notes(title, content) VALUES (?, ?)', (note.title, note.content))
        self.connection.commit()

    async def get_all_notes(self) -> List[Note]:
        self.cursor.execute('SELECT * FROM notes')
        notes_data = self.cursor.fetchall()
        return [Note(title, content) for title, content in zip(notes_data['title'], notes_data['content'])]

    async def search_notes_by_keyword(self, keyword) -> List[Note]:
        # Изменено: использование параметризованного запроса для предотвращения SQL-инъекций
        self.cursor.execute('SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?', ('%' + keyword + '%', '%' + keyword + '%'))
        notes_data = self.cursor.fetchall()
        return [Note(title, content) for title, content in zip(notes_data['title'], notes_data['content'])]

    async def delete_note_from_db(self, note):
        self.cursor.execute('DELETE FROM notes WHERE title = ? AND content = ?', (note.title, note.content))
        self.connection.commit()

class NoteApp:
    def __init__(self):
        self.database = Database()

    async def start(self):
        await self.database.connect()

        while True:
            print('1 - Добавить заметку')
            print('2 - Посмотреть все заметки')
            print('3 - Найти заметку')
            print('4 - Удалить заметку')
            print('5 - Выйти')

            choice = input('Выберите ваш вариант: ')

            # Изменено: использование словаря для связи выбора пользователя с соответствующей функцией
            actions = {
                '1': self.add_new_note,
                '2': self.view_all_notes,
                '3': self.search_notes,
                '4': self.delete_note,
                '5': self.exit_app
            }

            action = actions.get(choice)
            if action:
                await action()
            else:
                print('Неверный выбор!')

        await self.database.disconnect()

    async def add_new_note(self):
        title = input('Введите заголовок заметки: ')
        content = input('Введите содержание заметки: ')

        note = Note(title, content)
        await self.database.add_note_to_db(note)

        print('Заметка добавлена!')

    async def view_all_notes(self):
        notes = await self.database.get_all_notes()
        # Изменено: вынесение вывода списка заметок в отдельный метод
        self.print_notes(notes)

    async def search_notes(self):
        keyword = input('Введите ключевое слово для поиска: ')
        notes = await self.database.search_notes_by_keyword(keyword)
        # Изменено: вынесение вывода списка заметок в отдельный метод
        self.print_notes(notes)

    async def delete_note(self):
        keyword = input('Введите ключевое слово для удаления заметки ')
        notes = await self.database.search_notes_by_keyword(keyword)

        if not notes:
            print('Заметок не найдено')
        else:
            # Изменено: вынесение вывода списка заметок с индексами в отдельный метод
            self.print_notes_with_index(notes)
            choice = input('Введите ID заметки: ')
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(notes):
                    await self.database.delete_note_from_db(notes[idx])
                    print('Заметка удалена!')
                else:
                    print('Неверный выбор')
            except ValueError:
                print('Неверный выбор!')

    def print_notes(self, notes):
        if not notes:
            print('Заметок не найдено!')
        else:
            for note in notes:
                print(f'Заголовок: {note.title}\nСодержание: {note.content}\n')

    def print_notes_with_index(self, notes):
        for idx, note in enumerate(notes):
            print(f'[{idx + 1}] Заголовок: {note.title}\nСодержание: {note.content}\n')

    async def exit_app(self):
        # Изменено: добавлен метод выхода из приложения
        print('Выход из приложения')
        return

async def main():
    app = NoteApp()
    await app.start()

if __name__ == '__main__':
    asyncio.run(main())
