from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import os
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    access_level = db.Column(db.String(50))

    def __repr__(self):
        return f"<Agent {self.code_name}>"


with app.app_context():
    db.create_all()

@app.route("/")
def index():
    search = request.args.get("search")
    access_filter = request.args.get("access")

    query = Agent.query
    if search:
        query = query.filter(Agent.code_name.ilike(f"%{search}%"))
    if access_filter:
        query = query.filter_by(access_level=access_filter)
    agents = query.all()
    return render_template("index.html", agents=agents)

#
@app.route("/add", methods=["GET", "POST"])
def add_agent():
    if request.method == "POST":
        new_agent = Agent(
            code_name=request.form["code_name"],
            phone=request.form["phone"],
            email=request.form["email"],
            access_level=request.form["access_level"],
        )
        db.session.add(new_agent)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("add_agent.html")


@app.route("/agent/<int:id>")
def agent_detail(id):
    agent = Agent.query.get_or_404(id)
    return render_template("agent_detail.html", agent=agent)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_agent(id):
    agent = Agent.query.get_or_404(id)

    if request.method == "POST":
        agent.code_name = request.form["code_name"]
        agent.phone = request.form["phone"]
        agent.email = request.form["email"]
        agent.access_level = request.form["access_level"]
        db.session.commit()
        return redirect(url_for("agent_detail", id=id))

    return render_template("edit_agent.html", agent=agent)


@app.route("/delete/<int:id>")
def delete_agent(id):
    agent = Agent.query.get_or_404(id)
    db.session.delete(agent)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/generate_name")
def generate_name():
    try:
        with open("names.txt", "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return jsonify({"error": "Файл names.txt не найден"}), 500

    if not names:
        return jsonify({"error": "Файл пустой"}), 500

    existing_names = {agent.code_name for agent in Agent.query.all()}
    available_names = [name for name in names if name not in existing_names]

    if not available_names:
        return jsonify({"error": "Нет доступных имён"}), 400
    random_name = random.choice(available_names)
    return jsonify({"name": random_name})

@app.route("/nuclear", methods=["POST"])
def nuclear_mode():
    db.session.query(Agent).delete()
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)