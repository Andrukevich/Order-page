import yaml, mysql
import mysql.connector
from mysql.connector import errorcode

with open ('config.yaml') as config:
    y = yaml.load(config)


class CreateDB:
    """Creating the database."""
    def __init__(self):
        try:
            self.__con = mysql.connector.connect(user=y['mysql']['login'], password=y['mysql']['password'], host=y['mysql']['host'],\
                                                port=y['mysql']['port'], autocommit=True)
            cur = self.__con.cursor()
            cur.execute('drop database if exists my_project ;')
            cur.execute('create database my_project;')
            cur.execute('use my_project;')

            cur.execute('create table users (id_user int AUTO_INCREMENT, login varchar(50) NOT NULL, password \
                        varchar(200) NOT NULL, salt varchar(30) NOT NULL, cash float(5, 1), PRIMARY KEY (id_user));')
            cur.execute('create table goods (id_good int AUTO_INCREMENT, name varchar(50) NOT NULL, cost int, \
                        description text, img blob, PRIMARY KEY (id_good));')
            cur.execute('create table orders(id_order int AUTO_INCREMENT, id_user int NOT NULL, total_cost float(5, 1) \
                        NOT NULL, PRIMARY KEY (id_order), FOREIGN KEY (id_user) REFERENCES users(id_user));')
            cur.execute('create table goods_in_order(id_order int NOT NULL, id_good int NOT NULL, amount float(5, 1) \
                        NOT NULL, FOREIGN KEY (id_order) REFERENCES orders(id_order), FOREIGN KEY (id_good) \
                        REFERENCES goods(id_good));')

            cur.execute('INSERT INTO goods(name, cost, description, img) VALUES("APPLE", 1, "Apples from the \
ancient times were popular among the ancient healers. Used apples are not only as food but also as a means of \
preventing and treating diseases. Apples have a particular vitamin, which is called vitamin of youth. It helps to \
maintain a healthy liver, reduces cholesterol in the blood.", "images/apple.gif");')
            cur.execute('INSERT INTO goods(name, cost, description, img) VALUES("LEMON", 3, "Use lemons incredible \
it you can treat colds, flu, sore throat and pharyngitis. Potassium, magnesium and calcium, as well as carotene and \
organic substances contained in the lemon will help you to quickly cope with the symptoms of colds.", \
"images/lemon.gif");')
            cur.execute('INSERT INTO goods(name, cost, description, img) VALUES("PEAR", 2, "Pear is famous and \
useful in that it contains a large number of different antioxidants and vitamins (A, C, B1, E). However, its use does \
not end there, because, apart from them, pear rich very high in iron legkousvaemogo. Glutathione - one of the most \
useful vitamins that are contained in the pear.", "images/pear.gif");')
            cur.execute('INSERT INTO goods(name, cost, description, img) VALUES("ORANGE", 1.44, "Undoubtedly a huge \
benefit, Chinese apple, namely, the word translated as orange, in the content of a large number of vitamin C. The \
pulp contains ascorbic acid and citric acid to facilitate removal from the body of harmful substances, improve \
metabolism and strengthen immunity.", "images/orange.gif");')
#             cur.execute('INSERT INTO goods(name, cost, description, img) VALUES("PINEAPPLE", 4, "Pineapple is one of \
# the exotic fruit, which has almost no contraindications to the human body if it is not consumed in large quantities, \
# or from banks, stuffed with chemicals and sugar. Due to the high water content of 86% of its fruit is often used to \
# quench thirst. This fruit has become very popular because of the unique taste and aroma.", "images/pineapple.gif");')

        except mysql.connector.error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)
        else:
            self.__con.close()


CreateDB()