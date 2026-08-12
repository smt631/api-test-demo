"""登录接口测试：覆盖等价类、边界值（必填校验）、异常分支

设计说明：
- 用例设计：等价类（正确 / 错误密码、存在 / 不存在用户）+ 异常分支（缺参）
- 数据驱动：新增用例只需在 LOGIN_CASES 中增加一行，无需修改测试代码
"""
import pytest
import requests

# 数据驱动用例表：(用例名, 用户名, 密码, 期望状态码, 期望响应含关键字段)
LOGIN_CASES = [
    ("正向：正确账号密码登录成功", "alice", "123456", 200, "token"),
    ("异常：密码错误被拒绝",        "alice", "wrong", 401, "message"),
    ("异常：不存在的用户被拒绝",    "ghost", "123456", 401, "message"),
    ("边界：用户名为空",            "",     "123456", 400, "message"),
    ("边界：密码为空",              "alice", "",      400, "message"),
    ("边界：用户名密码均为空",      "",     "",      400, "message"),
]


@pytest.mark.parametrize(
    "name, username, password, expected_code, key",
    LOGIN_CASES,
    ids=[c[0] for c in LOGIN_CASES],  # 报告里显示用例名，可读性好
)
def test_login(base_url, name, username, password, expected_code, key):
    resp = requests.post(f"{base_url}/api/login",
                         json={"username": username, "password": password})
    # 断言 1：HTTP 状态码符合预期
    assert resp.status_code == expected_code
    # 断言 2：响应体包含关键字段（token 或错误信息）
    body = resp.json()
    assert key in body
    # 断言 3（仅正向）：token 不能为空
    if expected_code == 200:
        assert body["token"]
