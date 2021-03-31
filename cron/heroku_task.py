import logging

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
logger = logging.getLogger(__name__)

@sched.scheduled_job('interval', minutes=3)
def timed_job():
    logger.info('This job is run every three minutes.')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def scheduled_job():
    logger.info('This job is run every weekday at 5pm.')

sched.start()