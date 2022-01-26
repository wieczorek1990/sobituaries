from datetime import date, datetime, time

import stripe
from braces.views import CsrfExemptMixin
from django import http
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from rest_framework import filters
from rest_framework import generics
from rest_framework import views

from api import constants
from api import models
from api import serializers
from api import utils


class CemeteryRegisterListCreateView(CsrfExemptMixin, generics.ListCreateAPIView):
    authentication_classes = []
    queryset = models.CemeteryRegister.objects.all()
    serializer_class = serializers.CemeteryRegisterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['title', 'description']


class CemeteryRegisterRetrieveView(generics.RetrieveAPIView):
    queryset = models.CemeteryRegister.objects.all()
    serializer_class = serializers.CemeteryRegisterSerializer
    lookup_field = 'slug'


class ObituaryNoticeListCreateView(CsrfExemptMixin, generics.ListCreateAPIView):
    authentication_classes = []
    serializer_class = serializers.ObituaryNoticeSerializer

    def __init__(self, **kwargs):
        super().__init__()
        self.cemetery_register_id = None

    def get_cemetery_register_id(self):
        cemetery_register_slug = self.kwargs['slug']
        cemetery_register = get_object_or_404(models.CemeteryRegister, slug=cemetery_register_slug)
        cemetery_register_id = cemetery_register.id
        return cemetery_register_id

    def dispatch(self, request, *args, **kwargs):
        self.cemetery_register_id = self.get_cemetery_register_id()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        def add_cemetery_register():
            request.data['cemetery_register'] = self.cemetery_register_id

        utils.access_mutable(request, add_cemetery_register)

        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        now = timezone.now()
        queryset = models.ObituaryNotice.paid.filter(cemetery_register=self.cemetery_register_id,
                                                     holy_mass_datetime__gte=now)
        return queryset


class SlugsMixin:
    @staticmethod
    def get_additional_context_data():
        return {'SAMPLE': False}

    def get_slugs(self):
        cemetery_register_slug = self.kwargs['cemetery_register_slug']
        obituary_notice_slug = self.kwargs['obituary_notice_slug']
        return cemetery_register_slug, obituary_notice_slug

    def get_objects(self):
        cemetery_register_slug, obituary_notice_slug = self.get_slugs()

        cemetery_register = get_object_or_404(models.CemeteryRegister, slug=cemetery_register_slug)
        cemetery_register_id = cemetery_register.id
        obituary_notice = get_object_or_404(models.ObituaryNotice,
                                            cemetery_register=cemetery_register_id,
                                            slug=obituary_notice_slug)

        return cemetery_register, obituary_notice


class SampleSlugsMixin:
    @staticmethod
    def get_additional_context_data():
        return {'SAMPLE': True}

    def get_objects(self):
        cemetery_register_slug, obituary_notice_slug = self.get_slugs()

        cemetery_register = models.CemeteryRegister(
            title='Przykładowy rejestr nekrologów',
            description='To jest przykładowy rejestr nekrologów.',
            slug=cemetery_register_slug
        )
        obituary_notice = models.ObituaryNotice(
            death_date=date(2022, 1, 24),
            titles='Mąż, Ojciec, Dziadek',
            first_name='Adam',
            last_name='Nowak',
            years_lived=85,
            holy_mass_datetime=datetime(2022, 1, 24, 12, 0, 0, 0),
            holy_mass_place='w kościele Św. Wawrzyńca w Pniewach',
            rosary_time=time(11, 30, 0, 0),
            rosary_place='w kościele',
            body_or_ashes='body',
            funeral_place='na cmentarzu parafialnym',
            paid_on=datetime(2022, 1, 24, 0, 0, 0, 0),
            slug=obituary_notice_slug,
        )

        return cemetery_register, obituary_notice


class ObituaryNoticeTemplateView(SlugsMixin, generic.TemplateView):
    template_name = 'obituary_notice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        cemetery_register, obituary_notice = self.get_objects()

        context.update({
            'API_ROOT': settings.API_ROOT,
            'PAGE_ROOT': settings.PAGE_ROOT,
            'title': obituary_notice.clean_name(),
            'cemetery_register': cemetery_register,
            'obituary_notice': obituary_notice,
            'BODY': models.ObituaryNotice.BodyOrAshes.BODY,
            'ASHES': models.ObituaryNotice.BodyOrAshes.ASHES,
        })
        context.update(self.get_additional_context_data())

        return context


class ObituaryNoticeSampleTemplateView(SampleSlugsMixin, ObituaryNoticeTemplateView):
    pass


class ObituaryNoticePaymentView(SlugsMixin, views.APIView):
    def get(self, request, *args, **kwargs):
        cemetery_register, obituary_notice = self.get_objects()

        payment = models.ObituaryNoticePayment(obituary_notice=obituary_notice)
        payment.save()

        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'pln',
                    'product_data': {
                        'name': constants.SERVICE_NAME,
                    },
                    'unit_amount': constants.SERVICE_PRICE,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=(f'{settings.API_ROOT}/'
                         f'cemetery-registers/{cemetery_register.slug}/'
                         f'obituary-notices/{obituary_notice.slug}/'
                         f'payments/success/{payment.token}/'),
            cancel_url=f'{settings.PAGE_ROOT}#/stripe/cancel',
        )

        return redirect(session.url, code=303)


class ObituaryNoticePaymentSuccessView(SlugsMixin, views.APIView):
    def get(self, request, *args, **kwargs):
        _, obituary_notice = self.get_objects()

        token = self.kwargs['token']
        if obituary_notice.is_unpaid() and obituary_notice.token_matches(token):
            obituary_notice.mark_paid()
        else:
            return http.HttpResponseRedirect(f'{settings.PAGE_ROOT}#/stripe/cancel/')

        return http.HttpResponseRedirect(f'{settings.PAGE_ROOT}#/stripe/success/'
                                         f'{cemetery_register_slug}/{obituary_notice.slug}/')


class ReportCreateView(CsrfExemptMixin, generics.CreateAPIView):
    authentication_classes = []
    queryset = models.Report.objects.all()
    serializer_class = serializers.ReportSerializer
