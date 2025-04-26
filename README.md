### 1.安装项目所需依赖
pip install -r requirements.txt
### 2.启动项目
python manage.py runserver 0.0.0.0:8000
### 3.初始化项目下的sql
因为该项目使用的是低版本django框架，对应的mysql的版本也是低版本，所以如果想使用高版本
的django需要使用高版本的mysql

| Django 版本 | 推荐 MySQL 版本 | 最低 MySQL 版本 | 推荐 Python 版本 | 适配器推荐     | 支持结束时间       |
|------------|----------------|----------------|-----------------|---------------|-------------------|
| 5.0+       | 8.0+           | 8.0            | 3.10+           | mysqlclient   | 2025年12月        |
| 4.2 (LTS)  | 8.0            | 5.7            | 3.8+            | mysqlclient   | 2026年4月 (LTS)   |
| 4.1        | 8.0            | 5.7            | 3.8+            | mysqlclient   | 已停止支持        |
| 3.2 (LTS)  | 5.7            | 5.6            | 3.6+            | mysqlclient   | 2024年4月 (LTS)   |