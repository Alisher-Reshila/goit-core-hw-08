from datetime import datetime, timedelta
from collections import UserDict
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Имя не может быть пустым.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Номер должен содержать 10 цифр.")
 
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Формат даты должен быть: ДД.ММ.ГГГГ")

class Record:
    def __init__(self, name):
        self.name = Name(name)      
        self.phones = []  
        self.birthday = None
    
    def add_phone(self, number):
        self.phones.append(Phone(number))

    def remove_phone(self, number):
        phone = self.find_phone(number)
        if not phone:
            raise ValueError(f"Номер {number} не найден.")
        self.phones.remove(phone)
   
    def edit_phone(self, old_number, new_number):
        new_phone = Phone(new_number)
        old_phone = self.find_phone(old_number)
        if not old_phone:
            raise ValueError(f"Номер {old_number} не найден")
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None
    
    def add_birthday(self, b_day):
        self.birthday = Birthday(b_day)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        bd = f", день рождения: {self.birthday}" if self.birthday else ""
        return f"Контакт: {self.name.value}, телефоны: {phones}{bd}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError

    def __str__(self):
        if not self.data:
            return "Адресная книга пуста."
        return "\n".join(str(record) for record in self.data.values())

    def get_upcoming_birthdays(self):
        ubd = []
        today = datetime.today().date()
        for rec in self.data.values():
            if not rec.birthday: continue
            b_date = datetime.strptime(rec.birthday.value, "%d.%m.%Y").date()
            bd_this_year = b_date.replace(year=today.year)
            if bd_this_year < today: bd_this_year = bd_this_year.replace(year=today.year + 1)
            if 0 <= (bd_this_year - today).days <= 7:
                congrat = bd_this_year
                if congrat.weekday() >= 5: congrat += timedelta(days=(7 - congrat.weekday()))
                ubd.append({"name": rec.name.value, "congratulation_date": congrat.strftime("%d.%m.%Y")})
        return ubd


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                return "Ошибка: Недостаточно данных. Укажите имя и номер/дату."
            return str(e)
        except KeyError:
            return "Ошибка: Контакт не найден."
        except IndexError:
            return "Ошибка: Укажите имя контакта."
    return inner

@input_error
def add_contact(args, book):
    name, phone = args
    rec = book.find(name) or Record(name)
    rec.add_phone(phone)
    book.add_record(rec)
    return f"Контакт {name} обновлен/добавлен."

@input_error
def change_contact(args, book): 
    name, old_p, new_p = args
    rec = book.find(name)
    if not rec: 
        raise KeyError
    rec.edit_phone(old_p, new_p)
    return f"Номер для {name} успешно изменен."

@input_error
def show_phone(args, book): 
    name = args[0]
    rec = book.find(name)
    if not rec: 
        raise KeyError
    phones = "; ".join(p.value for p in rec.phones)
    return f"Номера {name}: {phones}" if phones else f"У {name} нет сохраненных номеров."

@input_error
def add_birthday(args, book):
    name, bday = args
    rec = book.find(name)
    if not rec: 
        raise KeyError
    rec.add_birthday(bday)
    return f"День рождения для {name} добавлен."

@input_error
def show_birthday(args, book): 
    name = args[0]
    rec = book.find(name)
    if not rec: raise KeyError
    return f"День рождения {name}: {rec.birthday}" if rec.birthday else f"Для {name} дата рождения не установлена."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming: return "На ближайшую неделю именинников нет."
    return "\n".join(f"{i['name']}: поздравить {i['congratulation_date']}" for i in upcoming)

@input_error  
def show_all(args, book):
    return str(book)

def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook


def main():
    book =  load_data()
    print("Добро пожаловать в бот-ассистент!")
    while True:
        user_input = input("Введите команду: ").strip()
        if not user_input: continue
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("До свидания!"); 
            break
        elif command == "hello":
            print("Чем я могу помочь?")
        elif command == "add": 
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all": 
            print(show_all(args, book))
        elif command == "add-birthday": 
            print(add_birthday(args, book))
        elif command == "show-birthday": 
            print(show_birthday(args, book))
        elif command == "birthdays": 
            print(birthdays(args, book))
        else: 
            print("Неизвестная команда.")

if __name__ == "__main__":
    main()