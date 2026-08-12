"""pytest fixture：启动被测 Flask 服务，向测试提供 base_url

设计说明：
- 用 werkzeug.make_server 在后台线程启动真实 HTTP 服务，测试通过 requests 发起真实请求，
  区别于 Flask 单元测试（test_client）
- 端口使用 0（随机空闲端口），避免与本机其他服务冲突
"""
import threading

import pytest
from werkzeug.serving import make_server

from app import app


@pytest.fixture(scope="session")
def base_url():
    """启动被测服务（整个测试会话只起一次），返回 base URL"""
    server = make_server("127.0.0.1", 0, app)  # 端口 0 = 随机空闲端口
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_port
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
