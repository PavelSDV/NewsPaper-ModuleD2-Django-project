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
from news.models import Post, Category, PostCategory


logger = logging.getLogger(__name__)


# def notify_subscribers_weekly():
#     print("Notifier is running")
#     # categories = Category.objects.all()
#     posts = Post.objects.all()
#     # current_site = Site.objects.get_current()
#     # site_link = f"http://{current_site.name}"
#     date = datetime.datetime.today()
#     week = date.strftime("%V")
#     for category in categories:
#         subscribers_list = PostCategory.objects.filter(categoryThrough=category)
#         # posts = Post.objects.filter(category=category).filter(dataCreation__week=date.today().isocalendar()[1]-1)
#         posts = Post.objects.filter(category=category).filter(dataCreation__week=week)
#         if posts.count()>0:
#             for each in subscribers_list:
#                 hello_text = f'Здравствуй, {each.user}. Подборка статей за неделю в твоём любимом разделе {category}!\n'
#                 header = 'Подборка статей за неделю'
#                 html_content = render_to_string('weekly_mail.html',
#                                                 # {'header': header, 'hello_text': hello_text, 'posts': posts, 'category': category, 'site_link': site_link})
#                                                 {'header': header, 'hello_text': hello_text, 'posts': posts, 'site_link': site_link})
#                 msg = EmailMultiAlternatives(
#                 subject=email_subject,
#                 body='',
#                 from_email='newspaperss@yandex.ru',
#                 to=[each.user.email],
#                 )
#                 msg.attach_alternative(html_content, "text/html") # добавляем html
#                 msg.send()


def get_subscriber(category):
    user_email = []
    for user in category.subscribers.all():
        user_email.append(user.email)
    return user_email # список эл.адресов подписчиков категории


def notify_subscribers_weekly():
    template = 'weekly_mail.html'

    date = datetime.datetime.today()
    week = date.strftime("%V")

    posts = Post.objects.all().filter(dataCreation__week=week)

    for post in posts:
        for category in Category.objects.all():
            email_subject = f'News week in category: "{category}"'
            user_email = get_subscriber(category)

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


# наша задача по выводу текста на экран
# def send_digest():
#     send_mail(
#         'Job mail',
#         'hello from job!',
#         from_email='newspaperss@yandex.ru',
#         recipient_list=['sdpv@mail.ru'],
#     )


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
