from django.contrib import admin

from api import models


class CemeteryRegisterCleanupModelAdmin(admin.ModelAdmin):
    exclude = ('deleted',)


for model, admin_model in (
  (models.CemeteryRegister, admin.ModelAdmin),
  (models.ObituaryNotice, admin.ModelAdmin),
  (models.CemeteryRegisterCleanup, CemeteryRegisterCleanupModelAdmin),
  (models.ObituaryNoticePayment, admin.ModelAdmin),
  (models.Report, admin.ModelAdmin),
):
    admin.site.register(model, admin_model)
