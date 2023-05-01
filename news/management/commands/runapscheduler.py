import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import send_mail

from django_apscheduler import util

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import datetime
from django.utils import timezone
from news.models import Post, Category, PostCategory


logger = logging.getLogger(__name__)

def get_subscriber(category):
    user_email = []
    for user in category.subscribers.all():
        user_email.append(user.email)
    return user_email

def notify_subscribers_weekly():
    template = 'weekly_mail.html'

    # date = datetime.datetime.today()  # фильтрует по номеру недели, т.е. нельзя в понедельник в 9-00 присылать,
    # week = date.strftime("%V")          # т.к. только будут посты прошедшие 9 часов недели
    # posts = Post.objects.filter(dataCreation__week=week) # поэтому рассылка в воскресенье 23-59 должна быть

    week = timezone.now() - datetime.timedelta(days=7) # здесь за прошедшие 7 дней, в любое время
    posts = Post.objects.filter(dataCreation__gte=week)

    for post in posts:
        categories = post.category.all()
        for category in categories:
            email_subject = f'News week in category: "{category}"'
            user_email = get_subscriber(category)
            # user_email = category.subscribers.values_list('email', flat=True)  # можно и так без функции

            html = render_to_string(
                template_name=template,
                context={
                    'category': category,
                    'post': post,
                },
            )
            msg = EmailMultiAlternatives(
                subject=email_subject,
                body='',
                from_email='newspaperss@yandex.ru',
                to=user_email,
            )

            msg.attach_alternative(html, 'text/html', )
            msg.send()


# функция которая будет удалять неактуальные задачи
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            notify_subscribers_weekly,
            trigger=CronTrigger(second="*/10"),   # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            # trigger=CronTrigger(
            #     day_of_week="mon", hour="10", minute="00"
            # ),
            id="notify_subscribers_weekly",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_digest'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
