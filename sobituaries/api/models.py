from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db import fields
from django_extensions.db import models as django_extensions_models


class CemeteryRegister(django_extensions_models.TimeStampedModel,
                       models.Model):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    slug = fields.AutoSlugField(_('slug'), populate_from='title', blank=False)

    def __str__(self):
        return self.title
