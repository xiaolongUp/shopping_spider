import logging
import os
import sys

from django.apps import AppConfig

'''定时爬取国外的各个电商平台的数据'''


class TaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task'

    def ready(self):
        logger = logging.getLogger('apscheduler')
        # 如果是在 celery worker 或 beat 模式下启动，直接跳过
        if any(cmd in sys.argv[0] for cmd in ['celery']) or 'celery' in ' '.join(sys.argv):
            logger.info("Detected celery/beat process, skip APScheduler init.")
            return

        # 在这里启动调度器
        from .scheduler import start_scheduler
        start_scheduler()
