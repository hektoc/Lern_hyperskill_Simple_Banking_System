# Write your code here
import random
import sqlite3


class Card:

    def __init__(self, db):
        self.db = db
        self.cur = self.db.cursor()
        self.loged_in = False
        self.number = ''
        self.pin = 0
        self.balance = 0
        self.loged_in = False

    def logon2account(self, number='', pin=''):
        self.number = number
        self.pin = pin
        self.check_pin()

    def create_account(self):
        return self.create_card()

    def check_pin(self) -> bool:
        """
        Check if card with self.number and self.pin exist. Return True if exist.
        Set self.loged_in flag to True, update balance from base to self.balance
        """
        self.cur.execute("SELECT * FROM card WHERE number = '" + str(self.number) + "' AND pin = '" +
                         str(int(self.pin)) + "';")
        # print("SELECT balance FROM card WHERE number = '" + str(self.number) + "' AND pin = '" + str(self.pin) + "';")
        answer = self.cur.fetchone()
        if answer is None:
            self.loged_in = False
            return False
        else:
            self.loged_in = True
            self.balance = answer[0]
            self.loged_in = True
            return True

    def gen_card_number(self) -> str:
        card = "".join(map(str, [4, 0, 0, 0, 0, 0] + [random.randint(0, 9) for _ in range(0, 9)]))
        card += str(self.gen_loun_checksum(card))
        return card

    @staticmethod
    def gen_loun_checksum(card: str) -> int:
        tmp = 0
        for num, i in enumerate(card, start=1):
            if num % 2 == 1:
                m = int(i) * 2
            else:
                m = int(i)
            tmp += m if m <= 9 else m - 9
        return int((10 - tmp % 10) % 10)

    def generate_number(self) -> str:
        self.number = self.gen_card_number()
        # if card exist, generate new and check again
        while self.check_exist():
            self.number = self.gen_card_number()
        return self.number

    @staticmethod
    def generate_pin() -> int:
        return random.randint(0, 9999)

    def create_card(self):
        self.generate_number()
        self.pin = self.generate_pin()
        self.cur.execute("INSERT INTO card (id, number, pin) VALUES (NULL, '" + str(self.number) + "', '"
                         + str(self.pin) + "') ;")
        self.db.commit()

    def check_exist(self, number: str = 0) -> bool:
        """ Return True if exist in base """
        check_number = number if number != 0 else self.number
        self.cur.execute("SELECT number FROM card WHERE number = '" + check_number + "';")
        if self.cur.fetchone() is None:
            return False
        return True

    def get_balance(self) -> int:
        self.cur.execute("SELECT number, balance FROM card WHERE number = '" + self.number + "';")
        result = self.cur.fetchone()
        if result is None:
            raise Exception('No such card number')
        else:
            self.balance = int(result[1])
            return self.balance

    def add_income(self, income: int) -> int:
        self.get_balance()
        self.balance += income
        self.cur.execute("UPDATE card SET balance=" + str(self.balance) + " WHERE number ='" + str(self.number) + "';")
        self.db.commit()
        return self.balance

    def logout(self):
        self.loged_in = False

    def close_account(self):
        self.cur.execute("DELETE FROM card WHERE number = '" + self.number + "';")
        self.db.commit()
        self.logout()

    def transfer2card(self, card2transfer: str, money_amount: int):
        self.cur.execute("UPDATE card SET balance = balance + " + str(money_amount) + " WHERE number ='"
                         + card2transfer + "';")
        self.db.commit()

        self.cur.execute("UPDATE card SET balance = balance - " + str(money_amount) + " WHERE number ='"
                         + self.number + "';")
        self.db.commit()


class SBS:

    def __init__(self):
        self.db = sqlite3.connect('card.s3db')
        self.cur = self.db.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS card "
                         "(id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")
        self.db.commit()
        self.card_number = ''
        self.current_card = Card(self.db)

    def __del__(self):
        self.db.close()

    def log_to_account(self):
        self.card_number = input('Enter your card number:')
        pin = input('Enter your PIN:')
        self.current_card.logon2account(self.card_number, pin)

        if self.current_card.loged_in:
            print('\nYou have successfully logged in!')
            self.show_card_menu()
        else:
            print('\nWrong card number or PIN!')  # Wrong Card number
            self.show_main_menu()

    def show_card_menu(self):
        print('\n1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')

        user_input = input()
        if user_input == '1':  # 2. Balance
            print(f'Balance: {self.current_card.get_balance()}')
            self.show_card_menu()
        elif user_input == '2':  # 2. Add income
            self.add_income()
        elif user_input == '3':  # 3. Do transfer
            self.do_transfer()
        elif user_input == '4':  # 4. Close account
            self.current_card.close_account()
            self.show_main_menu()
        elif user_input == '5':
            print('\bYou have successfully logged out!')
            self.current_card.logout()
            self.show_main_menu()
        elif user_input == '0':
            print('Bye!')
            exit()

    def add_income(self):
        income = int(input('Enter income:'))
        self.current_card.add_income(income)
        self.show_card_menu()

    def do_transfer(self):
        print('Transfer')
        card_to_transfer = input('Enter card number:')
        if self.current_card.gen_loun_checksum(card_to_transfer[:-1]) == int(card_to_transfer[-1:]):
            if self.current_card.check_exist(card_to_transfer):
                money = int(input('Enter how much money you want to transfer:'))
                if money < self.current_card.get_balance():
                    self.current_card.transfer2card(card_to_transfer, money)
                else:
                    print('Not enough money!')
            else:
                print('Such a card does not exist.')
        else:
            print('Probably you made a mistake in the card number. Please try again!')
        self.show_card_menu()

    def show_main_menu(self):
        print('\n1. Create an account')
        print('2. Log into account')
        print('0. Exit')

        user_input = input()
        if user_input == '1':
            self.current_card.create_card()
            self.show_new_card()
            self.show_main_menu()

        elif user_input == '2':
            self.log_to_account()
        elif user_input == '0':
            print('Bye!')
            exit()
        elif user_input == 'debug':
            self.debug()
            self.show_main_menu()

    def show_new_card(self):
        print('\nYour card has been created')
        print('Your card number:')
        print(f'{self.current_card.number}')
        print('Your card PIN:')
        print(f'{self.current_card.pin:04d}')

    def debug(self):
        self.cur.execute("SELECT * FROM card;")
        result = self.cur.fetchall()
        for i in result:
            print(i)


sbs = SBS()
sbs.show_main_menu()
