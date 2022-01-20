import stripe
from django import http
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from rest_framework import filters
from rest_framework import generics
from rest_framework import views

from api import models
from api import serializers
from api import utils


class CemeteryRegisterListCreateView(generics.ListCreateAPIView):
    queryset = models.CemeteryRegister.objects.all()
    serializer_class = serializers.CemeteryRegisterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['title', 'description']


class CemeteryRegisterRetrieveView(generics.RetrieveAPIView):
    queryset = models.CemeteryRegister.objects.all()
    serializer_class = serializers.CemeteryRegisterSerializer
    lookup_field = 'slug'


class ObituaryNoticeListCreateView(generics.ListCreateAPIView):
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
    def get_slugs(self):
        cemetery_register_slug = self.kwargs['cemetery_register_slug']
        obituary_notice_slug = self.kwargs['obituary_notice_slug']

        cemetery_register = get_object_or_404(models.CemeteryRegister, slug=cemetery_register_slug)
        cemetery_register_id = cemetery_register.id
        obituary_notice = get_object_or_404(models.ObituaryNotice,
                                            cemetery_register=cemetery_register_id,
                                            slug=obituary_notice_slug)

        return cemetery_register_slug, obituary_notice_slug, cemetery_register, obituary_notice


class ObituaryNoticeTemplateView(SlugsMixin, generic.TemplateView):
    template_name = 'obituary_notice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        cemetery_register_slug, _, cemetery_register, obituary_notice = self.get_slugs()

        context.update({
            'page_root': settings.PAGE_ROOT,
            'title': obituary_notice.clean_name(),
            'cemetery_register_slug': cemetery_register_slug,
            'obituary_notice': obituary_notice,
            'BODY': models.ObituaryNotice.BodyOrAshes.BODY,
            'ASHES': models.ObituaryNotice.BodyOrAshes.ASHES,
        })

        return context


class ObituaryNoticePaymentView(SlugsMixin, views.APIView):
    def get(self, request, *args, **kwargs):
        cemetery_register_slug, obituary_notice_slug, _, _ = self.get_slugs()

        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'pln',
                    'product_data': {
                        'name': 'obituary notice',
                    },
                    'unit_amount': 500,  # See Stripe spreadsheet
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=(f'{settings.API_ROOT}/'
                         f'cemetery-registers/{cemetery_register_slug}/'
                         f'obituary-notices/{obituary_notice_slug}/'
                         f'payments/success/'),
            cancel_url=f'{settings.PAGE_ROOT}#/stripe/cancel',
        )

        return redirect(session.url, code=303)


class ObituaryNoticePaymentSuccessView(SlugsMixin, views.APIView):
    def get(self, request, *args, **kwargs):
        cemetery_register_slug, obituary_notice_slug, _, obituary_notice = self.get_slugs()
        obituary_notice.mark_paid()
        return http.HttpResponseRedirect(f'{settings.PAGE_ROOT}#/stripe/success/'
                                         f'{cemetery_register_slug}/{obituary_notice_slug}/')
