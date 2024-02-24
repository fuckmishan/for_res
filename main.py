import asyncio
import sqlite3


class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    async def connect(self):
        self.connection = sqlite3.connect('notes.db')
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

    async def get_all_notes(self):
        self.cursor.execute('SELECT * FROM notes')
        notes_data = self.cursor.fetchall()
        return [Note(title, content) for _, title, content in notes_data] # возвращаем список всех заголовков и содержимого

    async def search_notes_by_keyword(self, keyword):
        self.cursor.execute('SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?', ('%' + keyword + '%', '%' + keyword + '%')) # ищем по ключевому слову
        notes_data = self.cursor.fetchall()
        return [Note(title, content) for _, title, content in notes_data] # аналогично, как я комментировал выше, 36 строчка

    async def delete_note_from_db(self, note):
        self.cursor.execute('DELETE FROM notes WHERE title=? AND content=?', (note.title, note.content))
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
            print('5 - Выйтии')

            choice = input('Выберите ваш вариант: ')

            if choice == '1':
                await self.add_new_note()
            elif choice == '2':
                await self.view_all_notes()
            elif choice == '3':
                await self.search_notes()
            elif choice == '4':
                await self.delete_note()
            elif choice == '5':
                break
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

        if not notes:
            print('Заметок не найдено!')
        else:
            for note in notes:
                print(f'Заголовок: {note.title}\nСодержание: {note.content}\n')

    async def search_notes(self):
        keyword = input('Введите ключевое слово для поиска: ')
        notes = await self.database.search_notes_by_keyword(keyword)

        if not notes:
            print('Заметок не найдено!')
        else:
            for note in notes:
                print(f'Заголовок: {note.title}\nСодержание: {note.content}\n')

    async def delete_note(self):
        keyword = input('Введите ключевое слово для удаления заметки ')
        notes = await self.database.search_notes_by_keyword(keyword)

        if not notes:
            print('Заметок не найдено')
        else:
            for idx, note in enumerate(notes): # проходим через все заметки и получаем их id и саму заметку, enumerate возвращает кортеж
                print(f'[{idx + 1}] Заголовок: {note.title}\nСодержжание: {note.content}\n')
            choice = input('Введите ID заметки: ')
            try:
                idx = int(choice) - 1 # вычитаем 1 так как индексы начинаиются с нуля
                if 0 <= idx < len(notes): # проверем, есть ли такой ID вообще
                    await self.database.delete_note_from_db(notes[idx])
                    print('Заметка удалена!')
                else:
                    print('Неверный выбор')
            except ValueError:
                print('Неверный выбор!')

async def main():
    app = NoteApp()
    await app.start()

if __name__ == '__main__':
    asyncio.run(main())