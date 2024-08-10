import re
from datetime import datetime, timedelta
from collections import UserDict

class Field:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value=None):
        super().__init__(value)
        
    def validate_phone(self):
        normalized_value = re.sub(r'\D', '', self.value)
        if re.fullmatch(r"\d{10}", normalized_value):
            self.value = normalized_value
            return True
        else:
            raise ValueError("Phone number must be exactly 10 digits")

class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    def validate_birthday(self, fmt='%d.%m.%Y'):
        try:
            self.date = datetime.strptime(self.value, fmt)
            return self.date
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value if self.value else "No birthday"

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones) if self.phones else "No phones"
        birthday_str = str(self.birthday) if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

    def add_birthday(self, birthday):
        birthday_field = Birthday(birthday)
        try:
            birthday_field.validate_birthday()
            self.birthday = birthday_field
        except ValueError as e:
            print(e)
    
    def add_phone(self, phone):
        phone_field = Phone(phone)
        try:
            phone_field.validate_phone()
            self.phones.append(phone_field)
        except ValueError as e:
            print(e)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if str(phone) == old_phone:
                phone_field = Phone(new_phone)
                try:
                    phone_field.validate_phone()
                    self.phones[idx] = phone_field
                except ValueError as e:
                    print(e)
                break

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

class AddressBook(UserDict):
    def add_record(self, record):
        if not isinstance(record, Record):
            raise ValueError("Value must be an instance of Record")
        self.data[record.name.value] = record
        
    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        now = datetime.now()
        upcoming_birthdays_list = []

        for record in self.data.values():
            if record.birthday:
                try:
                    birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=now.year)
                except ValueError:
                    continue
                
                upcoming_date = now + timedelta(days=days)

                if now <= birthday_date <= upcoming_date:
                    if birthday_date.weekday() in [5, 6]:
                        days_to_monday = (7 - birthday_date.weekday()) % 7
                        birthday_date += timedelta(days=days_to_monday)

                    upcoming_birthdays_list.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_date.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays_list

def parse_input(user_input):
    cmd, *args = user_input.split(maxsplit=1)
    cmd = cmd.strip().lower()
    args = args[0].split() if args else []
    return cmd, args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError:
            return "Enter the argument for the command"
        except IndexError:
            return "Enter user name."
    return inner

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
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise ValueError("Enter name, old phone, and new phone.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for {name} updated."
    else:
        raise ValueError(f"Contact {name} not found.")

@input_error
def show_phone(name, book: AddressBook):
    record = book.find(name)
    if record:
        phones = '; '.join(str(phone) for phone in record.phones)
        return f"{name}: {phones}"
    else:
        return f"Contact {name} not found."

@input_error
def show_all(book: AddressBook):
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Enter name and birthday.")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        raise ValueError("Enter name.")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    else:
        return f"Contact {name} not found or no birthday set."

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(f"{entry['name']}: {entry['congratulation_date']}" for entry in upcoming_birthdays)
    else:
        return "No upcoming birthdays in the next week."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args[0], book))

        elif command == "all":
            print(show_all(book))

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