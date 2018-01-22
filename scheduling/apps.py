# coding=utf-8
from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    name = 'scheduling'

    def ready(self):
        """from apscheduler.schedulers.background import BackgroundScheduler
        import time
        from polls.models import Question, Choice

        def some_job():
            print("Decorated job, {}".format(time.ctime()))
            q = Question.objects.all()
            print(q)

        scheduler = BackgroundScheduler()
        scheduler.add_job(some_job, 'interval', seconds=5)
        scheduler.start()
        """