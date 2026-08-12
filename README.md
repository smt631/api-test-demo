# API 接口自动化测试（pytest + requests）

对自研"订单查询 API"进行接口自动化测试，覆盖**登录鉴权正向链路与异常分支**，
体现等价类 / 边界值 / 场景法用例设计与数据驱动组织方式，并通过 GitHub Actions
实现 CI 质量门禁与测试报告自动化产出。

## 功能特性

- 自建 Flask 被测服务（登录 → token 鉴权 → 订单查询），测试基于真实 HTTP 链路
- 登录接口：等价类 / 边界值 / 异常分支用例，数据驱动（新增用例只加数据不改代码）
- 订单接口：场景法（基本流 + 备选流）+ 数据隔离校验
- pytest-html 自包含测试报告，可直接打开查看
- GitHub Actions：每次 push / PR 自动执行测试并上传报告（Artifact）

## 项目结构

```
api-test-demo/
├── app.py                    # 被测应用：Flask API（登录 → token 鉴权 → 订单查询）
├── requirements.txt          # 依赖：flask / requests / pytest / pytest-html
├── pytest.ini                # pytest 配置（testpaths + HTML 报告）
├── .github/workflows/test.yml  # CI：push/PR 触发，执行测试并上传报告
├── tests/
│   ├── conftest.py           # fixture：后台线程启动被测服务，提供 base_url
│   ├── test_login.py         # 登录接口：等价类 / 边界值 / 异常分支（数据驱动）
│   └── test_orders.py        # 订单接口：鉴权链路场景法 + 数据隔离校验
└── README.md
```

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖（Windows）
python -m venv .venv
.venv\Scripts\activate        # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 2. 运行测试（自动生成 HTML 报告）
pytest

# 3. 查看报告（单文件自包含，可直接打开）
reports/test_report.html
```

## 测试设计

| 测试点 | 用例设计方法 | 用例 |
|---|---|---|
| 登录成功 / 密码错误 / 用户不存在 | 等价类划分 | 正向 + 异常 |
| 用户名为空 / 密码为空 / 均为空 | 边界值（必填校验） | 3 条 |
| 登录 → 携 token → 查到订单 | 场景法·基本流 | 1 条 |
| 无 token / 伪造 token / 格式错误 | 场景法·备选流 | 3 条 |
| alice 只能看到自己的订单 | 业务规则（数据隔离） | 1 条 |

### 设计要点

1. **被测对象**：通过 `werkzeug.make_server` 在后台线程启动真实 HTTP 服务，
   测试使用 requests 发起真实请求，区别于 Flask 单元测试（test_client）。
2. **用例设计**：按接口文档将每个接口拆分为"正向 + 异常 + 边界"用例；
   订单查询重点验证**鉴权链路**与**数据隔离**（业务缺陷高发场景）。
3. **数据驱动**：登录用例集中管理在 `LOGIN_CASES` 中，通过 `parametrize` 参数化执行，
   新增用例只需补充数据，无需修改测试代码。
4. **可读性**：每条用例带业务化名称，pytest-html 报告单文件自包含，便于查阅与归档。

## CI 说明

GitHub Actions 工作流（`.github/workflows/test.yml`）：

- 触发条件：push 到 main/master、或提交 pull_request
- 执行流程：检出代码 → 配置 Python 3.12 → 安装依赖 → 运行 pytest → 上传测试报告
- 测试报告可在 Actions 运行结果的 Artifacts 中下载

## 常见问题

- **接口依赖登录态，token 如何管理？** conftest 提供 `base_url` fixture，
  每个用例自行走一遍"登录拿 token"（demo 规模足够）；大规模项目可做 session 级登录与 token 复用。
- **被测服务如何启停？** session 级 fixture 启动服务，测试结束自动 shutdown；
  CI 中可在测试前增加健康检查（GET /health）。
