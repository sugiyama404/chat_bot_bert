from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# データベースの設定(sqliteファイルのパスを指定)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.sqlite'
db = SQLAlchemy(app)


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


flag = False
task_content = ''


@app.route('/', methods=['POST', 'GET'])
def index():
    global flag, task_content
    if request.method == 'POST':
        task_content = request.form['content']
        task_type = request.form['type']
        if request.form['flag'] == 'True':
            flag = True
        else:
            flag = False
        new_task = Chat(content=task_content, type=task_type)

        try:
            db.session.add(new_task)
            db.session.commit()
        except:
            return "Not seld message yet, try again."

        return redirect('/')
    else:
        tasks = Chat.query.order_by(Chat.date_created).all()
        return render_template('index.html', tasks=tasks, flag=flag, task_content=task_content)


@ app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Chat.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Ocurr to delete error'


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8080)
