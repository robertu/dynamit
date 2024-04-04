from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _
from dynamit.utils import define_other_perms

class SklepConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sklep'

    def ready(self):
        try:
            from . import signals  # noqa F401
        except ImportError:
            pass
        post_migrate.connect(define_other_perms, sender=self)

