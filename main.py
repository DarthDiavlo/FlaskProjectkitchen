from flask import Flask, flash, redirect, render_template, request, url_for
from flask import request,session
from BD_Connection import User_Repository,Recipe_Repository,Comment_Repository
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:GhBDtn123@127.0.0.1:5432/CookingNotes'
db = SQLAlchemy(app)

@app.route('/', methods=['GET','POST'])
def hello_world():
    if 'logout' in request.form:
        session.pop('username', None)
        return render_template('hello.html')
    else:
        return render_template('hello.html')

@app.route('/authtorization', methods=['POST'])
def authtorization():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if 'login' in request.form:
            if(user_repo.authorization((username,password))=='Вы авторизованы'):
                session['username'] = request.form['username']
                return redirect(url_for('main'))
            elif(user_repo.authorization((username,password))=='Неверный пароль'):
                flash('Неверный пароль')
                return redirect(url_for('hello_world'))
            else:
                flash('Неверный логин или пароль')
                return redirect(url_for('hello_world'))
        elif 'registration' in request.form:
            if (user_repo.registration((username, password)) == 'Аккаунт создан'):
                session['username'] = request.form['username']
                return redirect(url_for('main'))
            else:
                flash('Такой логин уже существует')
                return redirect(url_for('hello_world'))
    return redirect(url_for('hello_world'))

@app.route('/update_password', methods=['GET','POST'])
def update_password():
    password=request.form['password']
    new_password=request.form['new_password']
    user_repo.update_password((session['username'],password,new_password))

@app.route('/del_password', methods=['GET','POST'])
def del_user():
    password = request.form['password']
    user_repo.del_user((session['username'],password))

@app.route('/main', methods=['GET','POST'])
def main():
    if 'username' in session:
        recipes = recipe_repo.all_recipe()
        print(recipes)
        return render_template('main.html',username=session['username'], recipes=recipes)
    else:
        return redirect(url_for('hello_world'))

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    if 'add' in request.form:
        return render_template('add_recipe.html')
    else:
        name = request.form['name']
        tags = request.form['tags']
        ingredients = request.form['ingredients']
        description = request.form['description']
        print(Recipe_Repository().add_recipe((name, ingredients, description,session['username'],tags)))
        return redirect(url_for('main'))

@app.route('/my_recipe', methods=['POST'])
def my_recipe():
    recipes = recipe_repo.my_recipe(session['username'])
    print(recipes)
    return render_template('main.html',username=session['username'], recipes=recipes)

@app.route('/search_tag', methods=['POST'])
def search_tag():
    recipes=recipe_repo.search_tag(request.form['tag'])
    return render_template('main.html',username=session['username'], recipes=recipes)

@app.route('/del_recipe', methods=['POST'])
def del_recipe():
    if(session['username']==request.form['author']):
        name = request.form['name']
        tags = request.form['tags']
        ingredients = request.form['ingredients']
        description = request.form['description']
        recipes = recipe_repo.del_recipe((name, ingredients, description,session['username'],tags))
        return redirect(url_for('main'))
    else:
        return 'Вы не можете удалить не свой рецепт'

@app.route('/watch_recipe', methods=['POST'])
def watch_recipe():
    name = request.form['name']
    tags = request.form['tags']
    ingredients = request.form['ingredients']
    description = request.form['description']
    score= request.form['score']
    recipe=recipe_repo.one_recipe()
    return render_template('recipe.html', recipe,session['username'])

@app.route('/update_score_recipe', methods=['POST'])
def update_score_recipe():
    name = request.form['name']
    author = request.form['author']
    Recipe_Repository.update_score((name,author))
    return redirect(url_for('main'))

@app.route('/add_comment', methods=['POST'])
def add_comment():
    recipe_id = request.form['recipe_id']
    text = request.form['text']
    return comment_repo.add_comment((session['username'],recipe_id,text))

@app.route('/search_ingredients', methods=['POST'])
def search_ingredients():
    recipes=recipe_repo.search_tag(request.form['ingredient'])
    return render_template('main.html',username=session['username'], recipes=recipes)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('e404.html'), 404

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ingredients = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tags = Column(JSON)
    score_sum = Column(Float)
    score_count=Column(Float)
    user = db.relationship('User', back_populates='recipes')
    comments = db.relationship('Comment', back_populates='recipe')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    comment_text = Column(String)
    user = db.relationship('User', back_populates='comments')
    recipe = db.relationship('Recipe', back_populates='comments')

if __name__ == '__main__':
    user_repo=User_Repository()
    recipe_repo=Recipe_Repository()
    comment_repo=Comment_Repository()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

