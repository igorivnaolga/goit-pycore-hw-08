from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle 


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
           if not re.fullmatch(r"\d{10}", value):
                  raise ValueError("Phone number must contain 10 digits")
           super().__init__(value)


class Birthday(Field):
      def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return True
        return False

    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
          if name in self.data:
                del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.replace(year=today.year)
                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)
                
                days_until_birthday = (birthday - today).days
                
                if 0 <= days_until_birthday <= 7:
                    if birthday.weekday() in (5, 6):
                        birthday += timedelta(days=(7 - birthday.weekday()))

                    upcoming.append({"name": record.name.value, "congratulation_date": birthday.strftime("%d.%m.%Y")})
        
        return upcoming


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Invalid input format."
        except IndexError:
            return "Not enough arguments for command."
        except KeyError:
            return "Contact not found."
    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return f"Added phone {phone} to {name}."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.edit_phone(old_phone, new_phone):
        return f"Changed {name}'s phone from {old_phone} to {new_phone}."
    return "Phone number not found."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    return "Contact not found."


def show_all(book):
    return "\n".join(str(record) for record in book.data.values()) if book.data else "No contacts available."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Added birthday {birthday} to {name}."
    return "Contact not found."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}"
    return "Birthday not found."


def upcoming_birthdays(book):
    birthdays = book.get_upcoming_birthdays()
    return birthdays if birthdays else "No upcoming birthdays."

@input_error
def delete_contact(args, book):
    if not args:
        return "Please provide a name to delete."
    name = args[0]
    record = book.find(name)
    if record:
        book.delete(name)
        return f"Contact {name} has been deleted."
    return "Contact not found."
    


def main():
    book = load_data()

    print("Welcome to the assistant bot!")


    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(upcoming_birthdays(book))
        elif command == "delete":
            print(delete_contact(args, book))
        else:
            print("Invalid command.")


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


if __name__ == "__main__":
    main()
