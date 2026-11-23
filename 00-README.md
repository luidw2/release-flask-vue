# 安全电子商务系统 III · 第五组 · 发布包

> 课程：电子科技大学 · 进阶式挑战性综合项目 III
> 组号：第 5 组
> 说明：本包用于课程验收与本地复现；`demo.env` / `bank.env` / `app/certs` 内是**仅课程演示**用的密钥/证书，禁止用于生产。

## 1. 环境要求

- Windows 10/11
- Python 3.13
- Node.js 20+ / npm 10+
- MySQL 8.0
- OpenSSL（需要支持 SM2 的版本，例如 OpenSSL 3.x）

## 2. 目录结构

```text
发布包-第5组/
  00-README.md
  01-源代码/
    backend/                   ← 电商后端（Flask，:5000）
    bank/                      ← 模拟银行（Flask，:8080）
    frontend/                  ← Vue3 前端（:5173）
  02-数据库/
    schema.sql / seed.sql      ← 电商库 test
    bank-schema.sql / bank-seed.sql  ← 银行库 fake_bank
  03-配置/
    demo.env                   ← 电商后端配置（复制成 backend/.env）
    bank.env                   ← 模拟银行配置（复制成 bank/.env）
    .env.example               ← 配置模板
  04-启动/
    start-bank.bat
    start-backend.bat
    start-frontend.bat
    start-all.bat
  05-演示/
    演示账号.md
    演示脚本.md
  06-备份恢复/
    backup.bat / restore.bat / 演练记录.md
  07-manifest/
    SHA256SUMS.txt
```

## 3. 初始化数据库

电商库：

```bat
mysql -u root -p < 02-数据库/schema.sql
mysql -u root -p < 02-数据库/seed.sql
```

银行库：

```bat
mysql -u root -p < 02-数据库/bank-schema.sql
mysql -u root -p < 02-数据库/bank-seed.sql
```

默认电商库 `test`，银行库 `fake_bank`。如果本机数据库名/账号不同，请修改 `demo.env` 和 `bank.env` 的 `DB_*`。

## 4. 配置

```bat
copy /Y 03-配置\demo.env 01-源代码\backend\.env
copy /Y 03-配置\bank.env 01-源代码\bank\.env
```

- 如果 `openssl` 不在 PATH，编辑两个 `.env`，设置：
  ```ini
  OPENSSL_PATH=你的openssl.exe绝对路径
  ```
- 前端地址默认 `http://127.0.0.1:5173`；生产改成 `https://你的域名`。

## 5. 启动顺序

```bat
04-启动\start-all.bat
```

或手动依次：

```bat
:: 1. 模拟银行 :8080
cd 01-源代码\bank
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py

:: 2. 电商后端 :5000
cd ..\backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python seed_staff.py
.venv\Scripts\python run.py

:: 3. 前端 :5173
cd ..\frontend
npm ci
npm run dev
```

- 银行：`http://127.0.0.1:8080`
- 后端：`http://127.0.0.1:5000`
- 前端：`http://127.0.0.1:5173`

## 6. 演示账号

- 管理员：`admin1 / Admin@123456`（首次登录需绑定 TOTP）
- 审计员：`audit1 / Audit@123456`（首次登录需绑定 TOTP）
- 普通用户/卖家：通过注册页注册

银行侧商户与演示余额已由 `bank-seed.sql` 初始化。

## 7. 支付流程依赖

支付是电商后端和模拟银行两个服务的联动：

```text
前端 → 电商后端 /api/pay/prepare（SM2 签名）
     → 浏览器跳转 模拟银行 :8080/pay
     → 银行确认支付，异步回调 电商后端 :5000/api/pay/callback
     → 银行把浏览器重定向回 电商后端 /pay/return
     → 渲染支付成功页
```

所以必须 **银行 :8080、电商后端 :5000、前端 :5173 同时启动**，缺一个支付流程就不完整。

## 8. 常见问题

| 现象 | 处理 |
|---|---|
| `Access denied` / 数据库连不上 | 检查 `.env` 的 `DB_*`，确认 MySQL 已启动 |
| `Unknown database 'test'/'fake_bank'` | 先执行对应的 schema.sql |
| 支付跳转 8080 失败 | 确认 `start-bank.bat` 已启动、端口 8080 未被占用 |
| 支付回调失败 | 检查 `bank` 库 merchant 表的 `callback_url`/`return_url` 是否为 `http://localhost:5000/...` |
| 登录 401 | 确认后端 5000 已启动、前端 5173 代理正常 |
| `OpenSSL` 找不到 | 两个 `.env` 都设置 `OPENSSL_PATH` |
| 商品图片不显示 | 确认 `app/static/uploads` 完整 |

## 9. 限制与说明

- 本包是课程演示版本，不是生产部署包；
- 银行与电商都使用 Flask 开发服务器，生产应使用 Nginx + WSGI/HTTPS；
- `demo.env`、`bank.env`、`app/certs` 内是演示密钥/证书，答辩后请轮换；
- 支付回调/回跳地址目前是 `localhost:5000`，换机器/端口时需同步修改银行库 merchant 表。
