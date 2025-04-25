from django.apps import AppConfig

'''定时爬取国外的各个电商平台的数据'''


class TaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task'

    def ready(self):
        # 在这里启动调度器
        from .scheduler import start_scheduler
        start_scheduler()
