# 校园二手交易系统：注册与登录

本项目实现专项作业中的账号注册、账号登录、密码安全存储、失败次数与验证码，以及浏览器会话管理。

注册与登录页面已实现的无障碍措施见 [ACCESSIBILITY.md](ACCESSIBILITY.md)。

## 环境准备

- Python 3.10 或更高版本
- MySQL 8.0 或更高版本

在项目根目录运行：

```powershell

pip install -r requirements.txt
Get-Content -Raw schema.sql | mysql -u root -p
```

如果提示找不到 `mysql` 命令，说明 MySQL 命令行客户端未安装或未加入 `PATH`。也可以在 MySQL Workbench 连接本机 MySQL 后，选择 **File → Open SQL Script** 打开 `schema.sql`，再点击闪电按钮执行。若已安装 MySQL Server 但命令不在 `PATH`，可用客户端完整路径执行，例如：

```powershell
Get-Content -Raw schema.sql | & "D:\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

按本机 MySQL 配置设置环境变量后启动：

```powershell
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
$env:DB_USER = "root"
$env:DB_PASSWORD = "你的MySQL密码"
$env:DB_NAME = "campus_market"
$env:SECRET_KEY = "自己设置一段随机且保密的字符串"
py app.py
```

打开 `http://127.0.0.1:5000/register` 注册。默认使用 Flask 自带的本地开发服务器；部署到真实环境时应使用生产级 WSGI 服务器，并通过 HTTPS 提供服务。

## 当前行为

- 账号只允许数字；数据库唯一索引处理并发重复注册。
- 密码长度为8～20位，必须包含大小写字母、数字和特殊字符，并使用 Werkzeug 安全哈希存储。
- 登录错误统一显示“账号或密码错误”；连续错误3次后，后续登录需要先完成算术验证码。
- 登录成功会清零失败次数；服务端 session cookie 不设持久期限，浏览器关闭后失效。
- 当前只实现注册与登录，商品浏览和交易功能不在专项范围内。

