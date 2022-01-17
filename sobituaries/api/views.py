from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import generic
from rest_framework import filters
from rest_framework import generics

from api import models
from api import serializers


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
        mutable = request.data._mutable
        request.data._mutable = True
        request.data['cemetery_register'] = self.cemetery_register_id
        request.data._mutable = mutable

        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        now = timezone.now()
        queryset = models.ObituaryNotice.objects.filter(cemetery_register=self.cemetery_register_id,
                                                        holy_mass_datetime__gte=now)
        return queryset


class ObituaryNoticeTemplateView(generic.TemplateView):
    template_name = 'obituary_notice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        cemetery_register_slug = self.kwargs['cemetery_register_slug']
        obituary_notice_slug = self.kwargs['obituary_notice_slug']

        cemetery_register = get_object_or_404(models.CemeteryRegister, slug=cemetery_register_slug)
        cemetery_register_id = cemetery_register.id
        obituary_notice = get_object_or_404(models.ObituaryNotice,
                                            cemetery_register=cemetery_register_id,
                                            slug=obituary_notice_slug)

        if not settings.DEBUG:
            page_root = self.request.META.get('HTTP_REFERER')
        else:
            page_root = settings.IJT_URL

        context.update({
            'page_root': page_root,
            'title': obituary_notice.clean_name(),
            'cemetery_register_slug': cemetery_register_slug,
            'obituary_notice': obituary_notice,
            'BODY': models.ObituaryNotice.BodyOrAshes.BODY,
            'ASHES': models.ObituaryNotice.BodyOrAshes.ASHES,
        })

        return context
