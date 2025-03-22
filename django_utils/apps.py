from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoUtilsConfig(AppConfig):
    name = 'django_utils'
    verbose_name = _('Common utils and template tags')
