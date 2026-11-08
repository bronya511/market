import os
import re
import secrets
from contextlib import contextmanager

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config.update(SESSION_PERMANENT=False, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "campus_market"),
        charset="utf8mb4",
    )


@contextmanager
def database():
    connection = connect_db()
    try:
        yield connection
    finally:
        connection.close()


def valid_account(account):
    return bool(re.fullmatch(r"[0-9]+", account or ""))


def valid_password(password):
    return bool(
        password
        and 8 <= len(password) <= 20
        and re.search(r"[a-z]", password)
        and re.search(r"[A-Z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r"[^A-Za-z0-9]", password)
    )


def make_captcha():
    left, right = secrets.randbelow(9) + 1, secrets.randbelow(9) + 1
    session["captcha_answer"] = str(left + right)
    return f"{left} + {right} = ?"


@app.get("/")
def home():
    if session.get("user_id"):
        return render_template("home.html", account=session.get("account"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        account = request.form.get("account", "").strip()
        password = request.form.get("password", "")
        if not valid_account(account):
            flash("账号只能由数字组成。", "error")
        elif not valid_password(password):
            flash("密码需为8～20位，并包含大小写字母、数字和特殊标点符号。", "error")
        else:
            try:
                with database() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO users (account, password_hash) VALUES (%s, %s)",
                        (account, generate_password_hash(password)),
                    )
                    conn.commit()
                flash("注册成功，请登录。", "success")
                return redirect(url_for("login"))
            except mysql.connector.IntegrityError:
                flash("该账号已注册。", "error")
            except mysql.connector.Error:
                app.logger.exception("Registration database operation failed")
                flash("系统暂时无法完成注册，请稍后重试。", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    captcha_required = False
    captcha_question = None
    if request.method == "POST":
        account = request.form.get("account", "").strip()
        password = request.form.get("password", "")
        try:
            with database() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id, account, password_hash, failed_attempts FROM users WHERE account = %s", (account,))
                user = cursor.fetchone()
                captcha_required = bool(user and user["failed_attempts"] >= 3)
                if captcha_required:
                    expected = session.pop("captcha_answer", None)
                    provided = request.form.get("captcha", "").strip()
                    if expected is None or not secrets.compare_digest(expected, provided):
                        flash("验证码错误或已过期，请重新计算。", "error")
                        captcha_question = make_captcha()
                        return render_template("login.html", captcha_required=True, captcha_question=captcha_question)

                if user and check_password_hash(user["password_hash"], password):
                    cursor.execute("UPDATE users SET failed_attempts = 0 WHERE id = %s", (user["id"],))
                    conn.commit()
                    session.clear()
                    session["user_id"] = user["id"]
                    session["account"] = user["account"]
                    return redirect(url_for("home"))

                if user:
                    cursor.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE id = %s", (user["id"],))
                    conn.commit()
                    captcha_required = user["failed_attempts"] + 1 >= 3
                flash("账号或密码错误。", "error")
                if captcha_required:
                    captcha_question = make_captcha()
        except mysql.connector.Error:
            app.logger.exception("Login database operation failed")
            flash("系统暂时无法完成登录，请稍后重试。", "error")
        return render_template("login.html", captcha_required=captcha_required, captcha_question=captcha_question)
    return render_template("login.html", captcha_required=False, captcha_question=None)


@app.post("/logout")
def logout():
    session.clear()
    flash("已安全退出。", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
