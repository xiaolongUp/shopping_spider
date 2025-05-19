# myapp/tasks.py
import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from task.bol_spider import spider_data as bol_spider_data

_scheduler_running = False  # 模块级全局变量
logger = logging.getLogger(__name__)

BASE_URl = 'https://www.fruugo.co.uk'

level_1_classify = {
    'Clothing & Accessories': '/clothing-accessories/d-ws90377710',
    'Health & Beauty': '/health-beauty/d-ws48843298',
    'Home & Garden': '/home-garden/d-ws69316386',
    'Home Decor & Furnishings': '/home-decor-furnishings/d-ws56158702',
    'Furniture': '/furniture/d-ws43285794',
    'Electronics & Electrical': '/electronics-electrical/d-ws42066773',
    'Media, Art & Entertainment': '/media-art-entertainment/d-ws53591381',
    'Sports Equipment': '/sports-equipment/d-ws82029960',
    'Games & Puzzles': '/games-puzzles/d-ws26870613',
    'Toys & Play Equipment': '/toys-play-equipment/d-ws97071086',
    'Pet Supplies': '/pet-supplies/d-ws60530363',
    'Business, Tools & Supplies': '/business-tools-supplies/d-ws40717704',
}


# 每个周期自动爬取数据
def start_scheduler():
    # identifier = level_1_classify['Home Decor & Furnishings']
    # Schedule the check_and_process_data to run every 30 minutes
    # scheduler.add_job(
    #     fruugo_spider_data,
    #     args=[level_1_classify['Home Decor & Furnishings'], 'uk'],  # 参数通过args传递
    #     trigger=IntervalTrigger(days=30),
    #     next_run_time=datetime.now()  # Run immediately on startup
    # )
    global _scheduler_running
    if _scheduler_running:
        logger.info(f"[PID:{os.getpid()}] Scheduler already running, skipping.")
        return

    _scheduler_running = True
    logger.info(f"[PID:{os.getpid()}] Initializing scheduler...")

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        bol_spider_data,
        args=['Speelgoed, Hobby & Feest', 'Speelgoed', 'Alles in Speelgoed', 'nl'],
        trigger=IntervalTrigger(days=30),
        next_run_time=datetime.now()
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        _scheduler_running = False
        scheduler.shutdown()
