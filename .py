from collections import UserDict
from curses.ascii import isdigit
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Имя контакта не может буть пустым")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ("Введите дату в формате: День.Месяц.Год")
        

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("номер долже состоять из 10 цифр!")
        
class Record:
    def __init__(self, name_value):
        self.name = Name(name_value)      
        self.phones = []  
        self.birthday = None
    
    def __str__(self):
        res = f"{self.name.value} {';'.join(p.value for p in self.phones)}"
        if self.birthday:
            res += f",день рождения:{self.birthday}"
        return res
            
    def add_phone(self, number):
        new_phone = Phone(number)
        self.phones.append(new_phone)
        print(f'номер {number} добавлен для {self.name.value}')

    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None
    
    def remove_phone(self, number):
        phone = self.find_phone(number)
        if phone: 
            self.phones.remove(phone)
            print(f"Номер {number} удалён")
        else:
            print(f"Номер {number} не найден")
    
    def add_birthday(self, b_day_str):
        self.birthday = Birthday(b_day_str)



class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record
        print(f"Контакт {record.name.value} добавлен в книгу")
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Контакт {name} удалён.")
        else:
            print(f"Контакт {name} не найден.")

    def upcoming_b_day(self):
        ubd = []
        today = datetime.today().date()

        for rec in self.data.values():
            if rec.birthday is None:
                continue 
            
            bd_this_year = rec.birthday.value.replace(year=today.year)

            if bd_this_year < today:
                bd_this_year = bd_this_year.replace(year=today.year + 1)
            
            if 0 <= (bd_this_year - today).days <= 7:
                congrat_date = bd_this_year
            
            if congrat_date.weekday() == 5:
                congrat_date += timedelta(days=2)
            
            elif congrat_date.weekday() == 6:
                congrat_date += timedelta(days=1)
            
            ubd.append({
                "name":rec.name.value,
                "congrat_date": congrat_date.strftime("%d.%m.%Y")
            })
        
        return ubd




def input_error(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found"
        except ValueError:
            return "Give me name and phone."
        except IndexError:
            return "Enter user name"
        except Exception as e: 
            return f"An unexpected error occurred: {e}"
    
    return inner


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args   


@input_error
def add_contacts(args, book:AddressBook):
    name, phone, *_ = args 
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт добавлен"
    else:
        message = "Контакт обновлен"
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book:AddressBook):
    name, old_phone, new_phone = args 
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Номер изменён."
    raise KeyError

@input_error
def show_all(book:AddressBook):
    if not book.data:
        return "Книга записей пустая."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book:AddressBook):
    name, birhthday = args 
    record = book.find(name)
    if record:
        record.add_birthday(birhthday)
        return "Добавлена дата дня рождения."
    raise KeyError

@input_error
def show_birthday(args, book:AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"У {name} день рождения :{record.birthday}"
    return "Запись ДР отсутствует."

@input_error 
def birthdays(args, book:AddressBook):
    upcoming = book.upcoming_b_day()
    if not upcoming:
        return "В ближайшие 7 дне нет ДР"
    return "\n".join(f"{item["имя"]}: {item["день_рождения"]}" for item in upcoming)


def main():
    book = AddressBook()
    print("Добро пожаловать!")

    while True:
        user_input = input("Введите комманду:")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye")
            break
        elif command == "hello":
            print("How can i help you?")
        elif command == "add":
            print(add_contacts(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))


if __name__ == "__main__":
    main()