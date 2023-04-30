from django.db.models.signals import post_save, m2m_changed

from django.dispatch import receiver
from .basic import new_post_subscription

from .models import Post, Category, PostCategory
from django.core.mail import EmailMultiAlternatives
from datetime import date
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.models import Site


@receiver(m2m_changed, sender=PostCategory)
def notify_subscribers(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        pass
        new_post_subscription(instance)

