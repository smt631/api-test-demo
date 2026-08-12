"""被测应用：简易订单查询 API（登录 → token 鉴权 → 查询订单）

业务链路：登录换取 token，携带 token 才能查询订单。
接口自动化测试覆盖正向（登录成功 → 查到数据）与异常（错密码 / 无 token / 伪造 token）两类场景。
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟用户表（真实项目中对应数据库表）
USERS = {
    "alice": "123456",
    "bob": "abcdef",
}

# 模拟订单数据（真实项目中对应订单表）
ORDERS = [
    {"id": 1001, "user": "alice", "item": "手机", "amount": 2999},
    {"id": 1002, "user": "alice", "item": "耳机", "amount": 599},
    {"id": 1003, "user": "bob", "item": "键盘", "amount": 199},
]


def _gen_token(username: str, password: str) -> str:
    """生成 token（简化版，仅用于演示鉴权逻辑）"""
    return f"token-{username}-{len(password)}"


@app.post("/api/login")
def login():
    """登录接口：POST /api/login  body: {username, password}"""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    # 异常分支 1：缺参数（对应边界值/必填校验）
    if not username or not password:
        return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400

    # 异常分支 2：账号或密码错误
    if USERS.get(username) != password:
        return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

    # 正向：登录成功，返回 token
    return jsonify({"code": 0, "token": _gen_token(username, password), "username": username}), 200


@app.get("/api/orders")
def get_orders():
    """订单查询接口：GET /api/orders  需携带 Authorization: Bearer <token>"""
    auth = request.headers.get("Authorization", "")

    # 异常分支 1：完全没带 token
    if not auth.startswith("Bearer "):
        return jsonify({"code": 401, "message": "未登录"}), 401

    token = auth[len("Bearer "):]

    # 异常分支 2：token 格式非法
    parts = token.split("-")
    if (len(parts) != 3 or parts[0] != "token"
            or not parts[1] or not parts[2].isdigit()
            or parts[1] not in USERS):
        return jsonify({"code": 401, "message": "无效 token"}), 401

    # 正向：返回该用户自己的订单（数据隔离：只能看到自己的）
    username = parts[1]
    return jsonify({"code": 0, "orders": [o for o in ORDERS if o["user"] == username]}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
