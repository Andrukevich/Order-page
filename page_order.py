from tkinter import *
import tkinter.messagebox
import re
import yaml, mysql
import mysql.connector
from mysql.connector import errorcode
from random import randrange
from string import ascii_letters, digits
import hashlib
from random import shuffle


with open ('config.yaml') as config:
    y = yaml.load(config)


class Registration:
    """Registration and input of users"""
    def __init__(self):
        self.__con = mysql.connector.connect(user=y['mysql']['login'], password=y['mysql']['password'], \
                                             host=y['mysql']['host'],  port=y['mysql']['port'], autocommit=True)
        self.__cur = self.__con.cursor()
        self.root = Tk()
        self.root.title('Login')
        self.root.grid(100, 100, 200, 200)
        lab1 = Label(self.root, text="Login", font="Arial 18")
        self.__ent1 = Entry(self.root,width=20,bd=5)
        lab2 = Label(self.root, text="Password", font="Arial 18")
        self.__ent2 = Entry(self.root,width=20,bd=5, show = '*')
        self.but1 = Button(self.root,text="Sign up", command = self.sign_up)
        self.but2 = Button(self.root,text="Sign in", command = self.sign_in)
        lab3 = Label(self.root, text="", font="Arial 18")
        lab1.grid(row = 1, column = 2)
        self.__ent1.grid(row = 2, column = 2)
        lab2.grid(row = 3, column = 2)
        self.__ent2.grid(row = 4, column = 2)
        lab3.grid(row = 5, column = 1)
        self.but1.grid(row = 6, column = 1)
        self.but2.grid(row = 6, column = 3)
        self.root.mainloop()

    def sign_up(self):
        login = self.__ent1.get()
        password = self.__ent2.get()
        self.check_password(login, password)

    def check_password(self, log, pas):
        if len(pas) > 20 or self.check_login(log) == 'Login isn\'t correct':
            tkinter.messagebox.showerror('ERROR', 'Login or password isn\'t correct. In your password there should be \
minimum one capital letter and small  letter and one number, length of the password from 8 up to 20 symbols. \
Login is your email with domain com, org or net')
        else:
            pattern = re.compile("((?=\w*\d)(?=\w*[a-z])(?=\w*[A-Z])((?!_)\w){8,20})")
            res = pattern.findall(pas)
            if len(res) > 0 and res[0][0] == pas and self.check_login(log) == 'Login is correct':
                self.__cur.execute('use my_project;')
                self.__cur.execute('SELECT * FROM users;')
                note = self.__cur.fetchall()
                check_log = 'No'
                for i in note:
                    if log in i:
                        tkinter.messagebox.showwarning('Warning', 'User with this login already exists!!!')
                        check_log = 'yes'
                if check_log == 'No':
                    salt = self.salt()
                    self.__cur.execute('insert into users(login, password, salt, cash) values("{}", "{}", "{}", 30.0);'\
                                       .format(log, self.cipher(salt,pas), salt))
                    self.root.withdraw()
                    OrderPage(self.__ent1.get(), self.__cur, self.root)
            else:
                tkinter.messagebox.showerror('ERROR', 'Login or password isn\'t correct. In your password there should \
be minimum one capital letter and small  letter and one number, length of the password from 8 up to 20 symbols. \
Login is your email with domain com, org or net')

    def check_login(self, log):
        pattern_mail = re.compile("(\w{2,64}\@[a-z]{3,8}\.(com|org|net))")
        res_mail = pattern_mail.findall(log)
        if len(res_mail) > 0 and res_mail[0][0] == log:
            return 'Login is correct'
        else:
            return 'Login isn\'t correct'

    def salt(self):
        st = ascii_letters+digits
        salt = ''
        for i in range(3):
            r = randrange(0, 62)
            salt += st[r]
        return salt

    def cipher(self, salt, password):
        return hashlib.sha1(hashlib.sha1(password.encode()+salt.encode()).hexdigest().encode()+\
                            hashlib.sha1(salt.encode()).hexdigest().encode()).hexdigest()

    def sign_in(self):
        login = self.__ent1.get()
        password = self.__ent2.get()
        self.check_user(login, password)

    def check_user(self, log, pas):
        self.__cur.execute('use my_project;')
        self.__cur.execute('SELECT * FROM users;')
        note = self.__cur.fetchall()
        check = 'No'
        for i in note:
            if log in i:
                if i[2] == self.cipher(i[3],pas):
                    check = 'Yes'
                    self.root.withdraw()
                    OrderPage(self.__ent1.get(), self.__cur, self.root)

        if check == 'No':
            tkinter.messagebox.showerror('Error', 'Such user does not exist. Check the username and password!!!')


class OrderPage:
    """Creating the order page."""
    def __init__(self, log, cur, root):
        self.__cur = cur
        self.__root = Toplevel()
        self.__root_registration = root
        self.__goods = Goods(self.__cur, self.__root)
        self.__user = User(self.__cur, log)
        self.__root.title('OrderPage')
        self.__root.grid(100, 100, 800, 500)
        self.__name_user = Label(self.__root,text='Hello "{}"'.format(self.__user.get_login()), font="Arial 15", \
                                 bg='red', bd=1)
        self.__balance = Label(self.__root,text='You cash {} $'.format(self.__user.get_money()), font="Arial 15", \
                               bg='red', bd=1)
        self.__but_order = Button(self.__root, width = 11, height = 5, text='Order', command=self.order, bg='orange')
        self.__but_close = Button(self.__root, width = 11, height = 5, text='Close', command=self.exit, bg='orange')
        self.__but_show_orders = Button(self.__root, width = 11, height = 5, text='Show orders', \
                                        command=self.show_orders, bg='orange')
        self.__but_fill_up_balance = Button(self.__root, width = 11, height = 5, text='Fill up balance', \
                                            command=self.fill_up_balance, bg='orange')
        self.__name_user.grid(row=1, column=0, columnspan = 5)
        self.__balance.grid(row=2, column=2, columnspan = 5)
        self.__but_order.grid(row=3, column=0, columnspan = 5)
        self.__but_close.grid(row=3, column=1, columnspan = 5)
        self.__but_show_orders.grid(row=3, column=2, columnspan = 5)
        self.__but_fill_up_balance.grid(row=3, column=3, columnspan = 5)
        line = 4
        for i in self.__goods.get_goods():
            i[9].grid(row=line, column=1, columnspan=5)
            i[1].grid(row=line, column=1, rowspan=2)
            i[2].grid(row=line, column=2, rowspan=2)
            i[3].grid(row=line, column=3)
            i[4].grid(row=line+1, column=3)
            i[5].grid(row=line, column=4)
            i[6].grid(row=line+1, column=4)
            i[7].grid(row=line, column=5)
            i[8].grid(row=line+1, column=5)
            line += 2
        self.__root.mainloop()

    def order(self):
        total = 0.0
        for i in self.__goods.get_goods():
            if i[0].get() != 0  and float(i[8].get()) != 0:
                total += (i[0].get())*(float(i[8].get()))
        if total == 0.0:
            tkinter.messagebox.showwarning('Warning', 'You have not chosen the goods!!!')
        elif (self.__user.get_money() - total) >= 0:
            self.__user.get_minus_money(total)
            self.__order = Order(self.__user.get_id_user(), total, self.__cur)
            self.__balance.grid_remove()
            self.__balance = Label(self.__root,text='You cash {} $'.format(self.__user.get_money()), font="Arial 15", \
                                   bg='red', bd=1)
            self.__balance.grid(row=2, column=2, columnspan = 5)
            for i in self.__goods.get_goods():
                if i[0].get() != 0  and float(i[8].get()) != 0:
                    GoodsInOrder(self.__order.get_id_order(), float(i[8].get()), i[10], self.__cur)
        else:
            tkinter.messagebox.showwarning('Warning', 'You dont have money!!!\n Push Fill up balance')

    def exit(self):
        self.__root.destroy()
        self.__root_registration.destroy()

    def fill_up_balance(self):
        self.__root.iconify()
        cash = Accept(self.__user.get_login())
        self.__user.get_plus_money(cash.get_plus_cash())
        self.__balance.grid_remove()
        self.__balance = Label(self.__root,text='You cash {} $'.format(self.__user.get_money()), font="Arial 15", \
                               bg='red', bd=1)
        self.__balance.grid(row=2, column=2, columnspan = 5)
        self.__root.deiconify()

    def show_orders(self):
        ShowOrders(self.__cur, self.__user.get_id_user(), self.__user.get_login())


class Goods:
    """Fills page order with the goods."""
    def __init__(self, cur, root):
        cur.execute('SELECT id_good, name, cost, description, img FROM goods;')
        note = cur.fetchall()
        self.__goods = []
        for i in range(len(note)):
            id_good = note[i][0]
            name = note[i][1]
            cost = note[i][2]
            description = note[i][3]
            img_b = note[i][4]
            if name == 'APPLE': colour = '#FE3100'
            elif name == 'LEMON': colour = '#FEFE00'
            elif name == 'PEAR': colour = '#0ACF00'
            elif name == 'ORANGE': colour = '#FF9900'
            elif name == 'PINEAPPLE': colour = '#B7F200'
            frame = Frame(root, width=800, heigh=100, bg=colour,bd=2)
            var = IntVar()
            che = Checkbutton(frame, text="", variable=var, onvalue=cost, offvalue=0, \
                                     bg=colour,bd=5)
            image = PhotoImage(file=img_b.decode())
            self.__img = Label(frame, image=image, bg='green', bd=5)
            label_title = Label(frame,text=name, font="Arial 15", bg=colour, bd=1)
            describe = Text(frame, width=65, height=5, font="Times 10", wrap=WORD)
            describe.insert(1.0, description)
            label_cost = Label(frame, text="cost,$/kg", width=15, font="Arial 15", bg=colour,bd=1)
            label_content_cost = Label(frame,text=cost, font="Arial 20", bg='gray', bd=1)
            label_title_order = Label(frame,text="how much,kg", width=15, font="Arial 15", bg=colour,bd=1)
            amount = Spinbox(frame, from_=0,to=5, increment=0.4)
            amount.delete(0)
            amount.insert(0, 0)
            self.__goods.append([var, che, self.__img, label_title, describe, label_cost, label_content_cost, \
                                 label_title_order,  amount, frame, id_good])

    def get_goods(self):
        return self.__goods


class User:
    """Data of the current user"""
    def __init__(self, cur, log):
        self.__cur = cur
        self.__login = log
        self.__cur.execute('SELECT id_user FROM users WHERE login="{}";'.format(self.__login))
        note = self.__cur.fetchone()
        self.__id_user = note[0]

    def get_login(self):
        return self.__login

    def get_id_user(self):
        return self.__id_user

    def get_money(self):
        self.__cur.execute('SELECT cash FROM users WHERE login="{}";'.format(self.__login))
        note = self.__cur.fetchone()
        self.__money = note[0]
        return self.__money

    def get_plus_money(self, plus_money):
        self.__cur.execute('UPDATE users SET cash={} WHERE login="{}";'.format(self.get_money()+plus_money, \
                                                                              self.__login))

    def get_minus_money(self, minus_money):
        self.__cur.execute('UPDATE users SET cash="{}" WHERE login="{}";'.format(self.get_money()-minus_money, \
                                                                                self.__login))


class Order:
    """Adds the order in the database"""
    def __init__(self, id_user, total_cost, cur):
        cur.execute('INSERT INTO orders(id_user, total_cost) VALUES ({}, {});'.format(id_user, total_cost))
        cur.execute('SELECT id_order FROM orders;')
        note = cur.fetchall()
        self.__id_order = note[-1][0]

    def get_id_order(self):
        return self.__id_order


class GoodsInOrder:
     """Adds the goods in order in the database"""
     def __init__(self, id_order, id_good_amount, id_good, cur):
         cur.execute('INSERT INTO goods_in_order(id_order, id_good, amount) VALUES ({}, {}, {});'.format(id_order, \
                    id_good, id_good_amount))


class ShowOrders:
    """Shows the orders current user"""
    def __init__(self, cur, id_user, log):
        self.__root = Toplevel()
        self.__user_orders = UserOrders(cur, self.__root, id_user)
        self.__root.title('Orders')
        self.__root.grid(100, 100, 500, 200)
        frame = Frame(self.__root, width=500, heigh=200, bg="yellow",bd=2)
        self.__name_user = Label(self.__root,text='Your orders "{}"'.format(log), font="Arial 15", bg='red', bd=1)
        self.__title_order = Label(frame,text='Number \norder', width=20, heigh=4, font="Arial 15", bg='yellow', bd=1)
        self.__title_name = Label(frame,text='Good', width=20, heigh=4, font="Arial 15", bg='yellow', bd=1)
        self.__title_amount = Label(frame,text='Amount, \nkg', width=20, heigh=4, font="Arial 15", bg='yellow', bd=1)
        self.__title_total_cost = Label(frame,text='Total \ncost, \n$', width=20, heigh=4, font="Arial 15", \
                                        bg='yellow', bd=1)
        self.__but_close = Button(self.__root, width = 20, height = 4, text='Close', command=self.exit, bg='orange')
        self.__name_user.grid(row=1, column=1, columnspan=4)
        self.__but_close.grid(row=2, column=1, columnspan=4)
        frame.grid(row=3, column=1,  columnspan=4)
        self.__title_order.grid(row=3, column=1)
        self.__title_name.grid(row=3, column=2)
        self.__title_amount.grid(row=3, column=3)
        self.__title_total_cost.grid(row=3, column=4)
        line = 4
        for i in self.__user_orders.get_user_orders():
            i[4].grid(row=line, column=1,  columnspan=4)
            i[0].grid(row=line, column=1)
            i[1].grid(row=line, column=2)
            i[2].grid(row=line, column=3)
            i[3].grid(row=line, column=4)
            line += 1
        self.__root.mainloop()

    def exit(self):
        return self.__root.destroy()


class UserOrders:
    def __init__(self, cur, root, id_user):
        cur.execute('SELECT orders.id_order, goods.name, goods_in_order.amount, orders.total_cost FROM users \
                    LEFT OUTER JOIN orders ON users.id_user=orders.id_user \
                    LEFT OUTER JOIN goods_in_order ON orders.id_order=goods_in_order.id_order \
                    LEFT OUTER JOIN goods ON goods.id_good=goods_in_order.id_good WHERE users.id_user="{}" \
                    ORDER by orders.id_order;'.format(id_user))
        note = cur.fetchall()
        self.__user_orders = []
        for i in range(len(note)):
            id_order = note[i][0]
            name = note[i][1]
            amount = note[i][2]
            total_cost = note[i][3]
            colour = 'orange'
            if i != 0:
                if note[i][0] == note[i-1][0]:
                    total_cost = ''
                    id_order = ''
            frame = Frame(root, width=500, heigh=200, bg="red",bd=2)
            label_id_order = Label(frame,text="{}".format(id_order), width=20, font="Arial 15", bg=colour, bd=1)
            label_name = Label(frame,text="{}".format(name), width=20, font="Arial 15", bg=colour, bd=1)
            label_amount = Label(frame,text="{}".format(amount), width=20, font="Arial 15", bg=colour, bd=1)
            label_cost = Label(frame,text="{}".format(total_cost), width=20, font="Arial 15", bg=colour, bd=1)
            self.__user_orders.append([label_id_order, label_name, label_amount, label_cost, frame])

    def get_user_orders(self):
        return self.__user_orders


class Card:
    """Description of a current card."""
    def __init__(self, name, value):
        self.__name = name
        self.__value = value

    def __str__(self):
       return '{}: {}'.format(self.__name, self.__value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return self.__value

    def set_value(self, number):
        self.__value = number


class Deck:
    """Creation of a deck"""
    __massive_element = ['6', '7', '8', '9', 'Korol', 'Valet', 'Dama', '10', 'Tyz']
    __massive_value = [6, 7, 8, 9, 4, 2, 3, 10, 11]
    __massive_color = ['\u2660', '\u2665', '\u2663', '\u2666']
    def __init__(self):
        self.__array_cards = []
        for i in range(len(self.__class__.__massive_element)):
            for j in range(len(self.__class__.__massive_color)):
                self.__array_cards.append(Card((self.__class__.__massive_element[i] + \
                                                self.__class__.__massive_color[j]), self.__class__.__massive_value[i]))

    def shuffle_deck(self):
        shuffle(self.__array_cards)
        return self.__array_cards

    def add_card(self):
        return self.__array_cards.pop()

    def get_deck(self):
        return self.__array_cards


class Hand:
    """Availability of cards in hand and points"""
    def __init__(self):
        self._current_sum = 0
        self.__array_cards = []
        self.__count_tyz = 0
        self._allow = True

    def __contains__(self, verify):
        for i in  self.__array_cards:
            value = i.get_name()
            if value[0:3] == verify:
                return True
            else:
                continue
        return False

    def add_card_hand(self, take_cards):
        if self._current_sum < 21:
            self.__array_cards.append(take_cards)
            self._current_sum = self.get_sum()
        if  self._current_sum > 21 and 'Tyz' in self:
            for i in self.__array_cards:
                name = i.get_name()
                if name[0:3] == 'Tyz':
                    i.set_value(1)
                    break
            return self.get_sum()

    def get_sum(self):
        self._current_sum = 0
        for i in self.__array_cards:
            self._current_sum += i.get_value()
        return self._current_sum

    def your_cards(self):
        for i in self.__array_cards:
            print (i.get_name())

    def count_tyz(self):
        self.__count_tyz = 0
        for i in self.__array_cards:
            check = i.get_name()
            if check[0:3] == 'Tyz':
                self.__count_tyz += 1
        return self.__count_tyz

    def your_sum(self):
        return self._current_sum


class Player(Hand):
    """Availability of cards at the player and points"""
    def __init__(self, name):
        super().__init__()
        self.__name = name

    def get_name(self):
        return self.__name

    def your_cards(self):
        print ('Your cards, ', self.__name, ':')
        super().your_cards()

    def get_allow(self):
        if self._current_sum < 21 and self._allow:
            return True
        else:
            return False

    def set_allow(self):
        self._allow = False
        return self._allow


class Bot(Hand):
    """Availability of cards at a computer and points"""
    def __init__(self):
        super().__init__()
        self.__limit = 15

    def your_cards(self):
        print ('Computer cards:')
        super().your_cards()

    def get_allow(self):
        if self._current_sum <= self.__limit:
            return True
        else:
            return False

class Accept:
    """The logic of the game"""
    def __init__(self, log):
        self.__plus = 0
        accept = input('You are playing versus computer.  Cards deal from the end of the deck. Every card gives you \n\
points: Ace – 11, King – 4, Queen – 3, Jack – 2, Ten – 10, Nine – 9, Eight – 8, Seven – 7, Six – 6. The aim of this \n\
game is a getting 21 points at the final stage or a getting score as close as possible to 21. In order to be the \n\
winner you must have more points than your opponent, but your score must be no more than 21. Two cards are available \n\
for each player (you and computer) after the first deal. If you and your opponent don’t have enough points to achieve \n\
21 after the first deal you and your opponent can ask one more card. In this case the next deal starts from you. If \n\
you have Two Aces after the first deal you score 21 automatically. If you get more than 21 but you have the one Ace, \n\
the points of Ace decrease to 1 point (it works one time only). If you have the same points with computer at the end \n\
of the game, your opponent becomes the winner.\nYOU RECEIVE 50 DOLLARS FOR A VICTORY.\nDo you want to play? yes\\no ')
        if accept == 'yes':
            deck = Deck()
            deck.shuffle_deck()
            check_deck = []
            for i in deck.get_deck():
                check_deck.append(i)
            player_name = log
            player = Player(player_name)
            bot = Bot()
            for i in range(2):
                player.add_card_hand(deck.add_card())
                bot.add_card_hand(deck.add_card())
            player.your_cards()
            print (player.your_sum(), '\n')
            if player.count_tyz() == 2 or bot.count_tyz() == 2:
                pass
            else:
                while bot.get_allow() or player.get_allow():
                    if player.get_allow() == True:
                        next_card_for_player = input('Take one more card? yes/no ')
                        if next_card_for_player == 'yes':
                            player.add_card_hand(deck.add_card())
                            player.your_cards()
                            print (player.your_sum(), '\n')
                        else:
                            player.set_allow()
                    if bot.get_allow() == True:
                        bot.add_card_hand(deck.add_card())
            if player.your_sum() > 21 and bot.your_sum() > 21:
                print ('\n!!!!!No winner!!!!!!\n')
            elif (player.your_sum() <= 21 and player.your_sum() > bot.your_sum()) or \
                (player.your_sum() <= 21 and bot.your_sum() > 21) or (player.count_tyz() == 2 and bot.your_sum() != 21):
                print ('\n!!!Winner: "{}"!!!\n Congratulate! You win 50 $'.format(player.get_name()))
                self.__plus += 50
            elif (player.count_tyz() == 2 and bot.count_tyz() == 2) or (player.your_sum() == 21 and \
                bot.count_tyz() == 2) or (bot.your_sum() and player.count_tyz() == 2) or (player.count_tyz() == 2 and \
                bot.your_sum() == 21):
                print ('\n!!!!!Winner: Computer!!!!!\n')
            else:
                print ('\n!!!!!Winner: Computer!!!!!\n')

            player.your_cards()
            print (player.your_sum(), '\n')
            bot.your_cards()
            print (bot.your_sum(), '\n')
            last_step = input('The game was fair! Do you want check deck? yes/no ')
            if last_step == 'yes':
                for i in check_deck:
                    print (i)
                print ('Come still if will be necessary money.')
            else:
                print ('Come still if will be necessary money.')
        else:
            print ('Come still if will be necessary money.')

    def get_plus_cash(self):
        return self.__plus


Registration()