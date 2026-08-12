"""订单查询接口测试：鉴权链路（登录后携 token 查询 / 无 token / 伪造 token / 数据隔离）

设计说明：
- 场景法：基本流（登录 → 携 token → 查到自己的订单）+ 多条备选流（无 token / 伪造 / 格式错）
- 数据隔离校验：alice 只能看到 alice 的订单，bob 只能看到 bob 的——接口测试中常见的业务缺陷场景
"""
import requests


def _login(base_url, username, password):
    resp = requests.post(f"{base_url}/api/login",
                         json={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["token"]


def _auth_headers(token=None):
    """token 为 None 时不带 Authorization 头（模拟未登录）"""
    return {} if token is None else {"Authorization": f"Bearer {token}"}


def test_正向_登录后携带token可查询到自己的订单(base_url):
    """基本流：登录拿到 token → 查订单 → 返回 alice 的 2 条订单"""
    token = _login(base_url, "alice", "123456")
    resp = requests.get(f"{base_url}/api/orders", headers=_auth_headers(token))

    assert resp.status_code == 200
    orders = resp.json()["orders"]
    assert len(orders) == 2                       # alice 有 2 条订单
    assert all(o["user"] == "alice" for o in orders)  # 且全部是自己的


def test_备选流_未携带token被拒绝(base_url):
    """备选流 1：完全没带 Authorization 头 → 401"""
    resp = requests.get(f"{base_url}/api/orders")
    assert resp.status_code == 401


def test_备选流_伪造token被拒绝(base_url):
    """备选流 2：token 格式合法但用户不存在（伪造）→ 401"""
    resp = requests.get(f"{base_url}/api/orders",
                        headers=_auth_headers("token-ghost-6"))
    assert resp.status_code == 401


def test_备选流_token格式非法被拒绝(base_url):
    """备选流 3：token 乱写 → 401"""
    resp = requests.get(f"{base_url}/api/orders", headers=_auth_headers("abc123"))
    assert resp.status_code == 401


def test_数据隔离_bob只能看到自己的订单(base_url):
    """业务校验：bob 登录后只能查到 bob 的 1 条订单，看不到 alice 的"""
    token = _login(base_url, "bob", "abcdef")
    resp = requests.get(f"{base_url}/api/orders", headers=_auth_headers(token))

    assert resp.status_code == 200
    orders = resp.json()["orders"]
    assert len(orders) == 1
    assert orders[0]["user"] == "bob"
