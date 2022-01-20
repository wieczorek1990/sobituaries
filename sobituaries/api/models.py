from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db import fields
from django_extensions.db import models as django_extensions_models

from api import constants
from api import utils


class CemeteryRegister(django_extensions_models.TimeStampedModel):
    class Meta:
        ordering = ('-id',)

    title = models.CharField(_('title'), max_length=constants.CHAR_FIELD_MAX_LENGTH)
    description = models.TextField(_('description'), blank=True)

    slug = fields.AutoSlugField(_('slug'), populate_from='title', blank=False, unique=True)

    def __str__(self):
        return self.title


class ObituaryNoticeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(paid_on__isnull=False)


class ObituaryNotice(django_extensions_models.TimeStampedModel):
    class Meta:
        ordering = ('-id',)
        unique_together = (('cemetery_register', 'slug'),)

    class BodyOrAshes(models.TextChoices):
        BODY = 'body', _('Body')
        ASHES = 'ashes', _('Ashes')

    cemetery_register = models.ForeignKey(CemeteryRegister, on_delete=models.CASCADE, related_name='obituary_notices')

    death_date = models.DateField(_('death date'))
    titles = models.CharField(_('titles'), max_length=constants.CHAR_FIELD_MAX_LENGTH)
    first_name = models.CharField(_('first name'), max_length=constants.CHAR_FIELD_MAX_LENGTH)
    last_name = models.CharField(_('last name'), max_length=constants.CHAR_FIELD_MAX_LENGTH)
    years_lived = models.PositiveIntegerField(_('years lived'))
    holy_mass_datetime = models.DateTimeField(_('holy mass datetime'))
    holy_mass_place = models.CharField(_('holy mass place'), max_length=constants.CHAR_FIELD_MAX_LENGTH)
    rosary_time = models.TimeField(_('rosary time'))
    rosary_place = models.CharField(_('rosary place'), max_length=constants.CHAR_FIELD_MAX_LENGTH)
    body_or_ashes = models.CharField(_('body or ashes'), max_length=constants.CHAR_FIELD_MAX_LENGTH,
                                     choices=BodyOrAshes.choices)
    funeral_place = models.CharField(_('funeral place'), max_length=constants.CHAR_FIELD_MAX_LENGTH)

    paid_on = models.DateTimeField(default=None, null=True)
    slug = fields.AutoSlugField(_('slug'), populate_from='name', blank=False)

    objects = models.Manager()
    paid = ObituaryNoticeManager()

    def __str__(self):
        return f'{self.clean_name()} {self.slug}'

    def name(self):
        return f'{self.clean_name()} {utils.random_ascii_lowercase()}'

    def clean_name(self):
        return f'{self.first_name} {self.last_name}'

    def is_unpaid(self):
        return self.paid_on is None

    def token_matches(self, token):
        return self.payment.token == token

    def mark_paid(self):
        self.paid_on = timezone.now()
        self.save()


class CemeteryRegisterCleanup(django_extensions_models.TimeStampedModel):
    deleted = models.PositiveIntegerField()

    def save(self, **kwargs):
        queryset = (CemeteryRegister.objects
                                    .annotate(obituary_notices_count=models.Count('obituary_notices'))
                                    .filter(obituary_notices_count=0))
        self.deleted = queryset.count()
        queryset.delete()
        return super().save(**kwargs)


class ObituaryNoticePayment(django_extensions_models.TimeStampedModel):
    obituary_notice = models.OneToOneField(ObituaryNotice, on_delete=models.CASCADE, related_name='payment')

    token = models.CharField(_('token'), max_length=constants.PAYMENTS_TOKEN_LENGTH)

    def save(self, **kwargs):
        self.token = utils.random_ascii_lowercase(length=constants.PAYMENTS_TOKEN_LENGTH)
        super().save(**kwargs)
