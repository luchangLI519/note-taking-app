from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

# 创建 Flask 应用
app = Flask(__name__)

# 配置数据库（SQLite）
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
db = SQLAlchemy(app)

# 定义 Note 模型（数据库表）
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# 初始化数据库
with app.app_context():
    db.create_all()
# 根路径，提示用户使用 /api/notes
@app.route("/")
def index():
    return render_template("index.html")
# --- API 路由 ---

# 获取所有笔记
@app.route("/api/notes", methods=["GET"])
def get_notes():
    notes = Note.query.all()
    return jsonify([{"id": n.id, "title": n.title, "content": n.content} for n in notes])

# 创建新笔记
@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.json
    note = Note(title=data["title"], content=data["content"])
    db.session.add(note)
    db.session.commit()
    return jsonify({"id": note.id}), 201
# 获取单个笔记
@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return jsonify({"id": note.id, "title": note.title, "content": note.content})

# 更新笔记
@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.json
    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()
    return jsonify({"message": "Note updated"})

# 删除笔记
@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"})
# 运行应用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    