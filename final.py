from collections import UserDict
import re
from datetime import datetime, timedelta
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

# Список доступних команд
COMMANDS = ['hello', 'add', 'change', 'phone', 'email', 'all', 'add-birthday', 'show-birthday', 'birthdays', 'add-email', 'show-email', 'change-email', 'close', 'exit']

# Автозаповнення команд
command_completer = WordCompleter(COMMANDS, ignore_case=True)

# Базовий клас для полів запису
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для зберігання імені контакту
class Name(Field):
    pass

# Клас для зберігання номера телефону з валідацією формату (10 цифр)
class Phone(Field):
    def __init__(self, value):
        if self._validate(value):
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number format. It should be 10 digits.")

    def _validate(self, value):
        return re.fullmatch(r"\d{10}", value) is not None

# Клас Email для зберігання та валідації електронної адреси
class Email(Field):
    def __init__(self, value):
        if self._validate(value):
            super().__init__(value)
        else:
            raise ValueError("Invalid email format.")

    def _validate(self, value):
        # Простий регулярний вираз для валідації email
        return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value) is not None
    
# Клас для зберігання дати народження з валідацією формату дати (DD.MM.YYYY)
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для зберігання інформації про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)  
        self.phones = []
        self.emails = []   
        self.birthday = None  

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.phones.remove(phone_to_edit)
            self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_email(self, email):
        self.emails.append(Email(email))

    def remove_email(self, email):
        email_to_remove = self.find_email(email)
        if email_to_remove:
            self.emails.remove(email_to_remove)

    def edit_email(self, old_email, new_email):
        email_to_edit = self.find_email(old_email)
        if email_to_edit:
            self.emails.remove(email_to_edit)
            self.add_email(new_email)

    def find_email(self, email):
        for e in self.emails:
            if e.value == email:
                return e
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        emails = '; '.join(e.value for e in self.emails)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, emails: {emails}, birthday: {birthday}"
    
# Клас для управління та зберігання записів адресної книги
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if today <= next_birthday <= (today + timedelta(days=days)):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

def input_error(func):
    def wrapper(args, book):
        try:
            return func(args, book)
        except ValueError as e:
            return str(e)
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number updated for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"
    else:
        return f"Contact {name} not found."

@input_error
def list_contacts(args, book: AddressBook):
    if not book.data:
        return "Address book is empty."
    result = ["Contacts in address book:"]
    for name, record in book.data.items():
        result.append(str(record))
    return "\n".join(result)

@input_error
def add_email(args, book: AddressBook):
    name, email, *_ = args
    record = book.find(name)
    if record:
        record.add_email(email)
        return f"Email {email} added for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def change_email(args, book: AddressBook):
    name, old_email, new_email = args
    record = book.find(name)
    if record:
        record.edit_email(old_email, new_email)
        return f"Email updated for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_email(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s emails: {', '.join(e.value for e in record.emails)}"
    else:
        return f"Contact {name} not found."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
        else:
            return f"Birthday not set for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7
    upcoming_birthdays = book.get_upcoming_birthdays(days)
    if not upcoming_birthdays:
        return "No upcoming birthdays within the next week."
    result = ["Upcoming birthdays:"]
    for record in upcoming_birthdays:
        result.append(f"{record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}")
    return "\n".join(result)

def parse_input(user_input):
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = AddressBook()
    session = PromptSession(completer=command_completer)

    print("Welcome to the assistant bot!")
    while True:
        user_input = session.prompt("Enter a command: ")
        
        if not user_input.strip():  
            print("No command entered. Please enter a command.")  
            continue  
        
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "add-email":
            print(add_email(args, book))

        elif command == "change-email":
            print(change_email(args, book))

        elif command == "show-email":
            print(show_email(args, book))

        elif command == "all":
            print(list_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()