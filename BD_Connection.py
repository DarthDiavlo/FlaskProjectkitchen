import psycopg2
from psycopg2 import OperationalError
from recipe import Recipe
from comment import Comment
import json

class Repository:
    def __init__(self):
        try:
            connection = psycopg2.connect(
                database="CookingNotes",
                user="postgres",
                password="GhBDtn123",
                host="127.0.0.1",
                port="5432",
            )
            connection.autocommit = True
            self.cursor = connection.cursor()
        except OperationalError as e:
            print(f"The error '{e}' occurred")

    def close(self):
        # Закрытие соединения
        self.connection.close()

class User_Repository(Repository):
    key = 42

    def check_user(self, username):
        exists_query = '''SELECT * FROM users WHERE username=%s;'''
        self.cursor.execute(exists_query, (username,))
        return self.cursor.rowcount > 0

    def registration(self, values):
        if not self.check_user(values[0]):
            values = list(values)
            print(values)
            values[1] = self.encode_password(values[1], self.key)
            self.cursor.execute("INSERT INTO users VALUES(%s,%s)", values)
            return 'Аккаунт создан'
        else:
            return 'Такой логин уже существует'

    def authorization(self, values):
        if self.check_user(values[0]):
            user = self.cursor.execute('''SELECT * FROM users WHERE username=%s;''', (values[0],))
            result = self.cursor.fetchall()
            decodepassword = self.decode_password(result[0][1], self.key)
            if decodepassword == values[1]:
                return 'Вы авторизованы'
            else:
                return 'Неверный пароль'
        else:
            return 'Неверный логин или пароль'

    def encode_password(self,password, key):
        encoded = []
        for char in password:
            encoded_char = ord(char) ^ key
            encoded.append(encoded_char)
        return bytes(encoded)

    def decode_password(self,encoded_password, key):
        decoded = []
        for encoded_char in encoded_password:
            decoded_char = encoded_char ^ key
            decoded.append(chr(decoded_char))
        return ''.join(decoded)

    def close(self):
        # Закрытие соединения
        self.connection.close()

    def update_password(self,values):
        user = self.cursor.execute('''SELECT * FROM users WHERE username=%s;''', (values[0],))
        result = self.cursor.fetchall()
        decodepassword = self.decode_password(result[0][1], self.key)
        if decodepassword == values[1]:
            request="UPDATE users SET password = %s WHERE username=%s;"
            self.cursor.execute(request, (values[2],values[0]))
            return 'Успешно'
        else:
            return 'Неверный пароль'

    def del_user(self,values):
        user = self.cursor.execute('''SELECT * FROM users WHERE username=%s;''', (values[0],))
        result = self.cursor.fetchall()
        decodepassword = self.decode_password(result[0][1], self.key)
        if decodepassword == values[1]:
            self.cursor.execute('''DELETE FROM users WHERE username=%s;''', values)
            return 'Успешно'
        else:
            return 'Неверный пароль'


class Recipe_Repository(Repository):
    def add_recipe(self, values):
        values = list(values)
        values[4] = json.dumps(values[4].split(','))
        self.cursor.execute("INSERT INTO recipes VALUES(%s,%s,%s,%s,%s)", values)
        return 'Успешно'

    def all_recipe(self):
        self.cursor.execute('''SELECT * FROM recipes;''')
        mas = []
        for recipe in self.cursor.fetchall():
            rec = Recipe(recipe[0], recipe[1], recipe[2], recipe[3], ', '.join(recipe[4]),recipe[5],recipe[6])
            mas.append(rec)
        return mas

    def my_recipe(self,username):
        self.cursor.execute('''SELECT * FROM recipes WHERE authors=%s;''', (username,))
        print(username)
        mas = []
        for recipe in self.cursor.fetchall():
            rec = Recipe(recipe[0], recipe[1], recipe[2], recipe[3], ', '.join(recipe[4]),recipe[5],recipe[6])
            mas.append(rec)
        return mas

    def search_tag(self,values):
        values = values.replace(', ', '|')
        self.cursor.execute("SELECT * FROM recipes WHERE to_tsvector('russian', tags::text) @@ to_tsquery('russian', %s)",(values,))
        result=self.cursor.fetchall()
        print(result)
        mas = []
        if(result ==[]):
            rec = Recipe('По вашему запросу результатов не найдено',None,None,None,None)
            mas.append(rec)
            return mas
        else:
            for recipe in result:
                rec = Recipe(result[0], result[1], result[2], result[3], ', '.join(result[4]),result[5],result[6])
                mas.append(rec)
            return mas

    def del_recipe(self,values):
        values = list(values)
        values[3] = json.dumps(values[3].split(','))
        self.cursor.execute('''DELETE FROM recipes WHERE name=%s AND ingredients=%s AND description=%s AND tags=%S;''', values)
        return 'Успешно'

    def update_recipe(self,values):
        values = list(values)
        values[3] = json.dumps(values[3].split(','))
        self.cursor.execute('''DELETE FROM recipes WHERE name=%s AND ingredients=%s AND description=%s AND tags=%S;''', values)
        return 'Успешно'

    def search_ingredients(self,values):
        values= '%'+values+'%'
        self.cursor.execute("SELECT * FROM recipes WHERE ingredients LIKE '%s'",(values,))
        result=self.cursor.fetchall()
        mas = []
        if(result ==[]):
            rec = Recipe('По вашему запросу результатов не найдено',None,None,None,None)
            mas.append(rec)
            return mas
        else:
            for recipe in result:
                rec = Recipe(result[0], result[1], result[2], result[3], ', '.join(result[4]),result[5],result[6])
                mas.append(rec)
            return mas

    def watch_recipe(self,values):
        self.cursor.execute("SELECT * FROM recipes WHERE recipe_id = '%s' AND author=%s ", (values))
        result= self.cursor.fetchall()
        comment_recipe=Comment_Repository.search(values[0],values[3])
        mas = []
        rec = Recipe(result[0], result[1], result[2], result[3], ', '.join(result[4]),result[5],result[6])
        mas.append(rec)
        mas.append(comment_recipe)
        return mas

    def update_score(self,values):
        self.cursor.execute("SELECT * FROM recipes WHERE recipe_id = '%s' AND author=%s ", (values))
        result = self.cursor.fetchall()
        rec = Recipe(result[0], result[1], result[2], result[3], ', '.join(result[4]),result[5],result[6])
        rec.score_count += values[2]
        rec.score_summ += values[3]
        request = "UPDATE recipes SET score_count = %s, score_summ = %s WHERE recipe_id = '%s' AND author=%s;"
        self.cursor.execute(request, (rec.score_count,rec.score_summ,values[0],[1]))
        return 'Успешно'

class Comment_Repository(Repository):
    def search(self,values):
        self.cursor.execute('''SELECT * FROM comments WHERE username_id=%s AND recipe_id=%s;''', (values))
        result = self.cursor.fetchall()
        if (result == []):
            return None
        else:
            mas = []
            for comment in result:
                rec = Comment(comment[0], comment[1], comment[2])
                mas.append(rec)
            return mas

    def add_comment(self,values):
        self.cursor.execute("INSERT INTO comments VALUES(%s,%s,%s)", values)
        return 'Успешно'


