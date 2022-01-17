from django.contrib import admin

from api import models


for model, admin_model in (
  (models.CemeteryRegister, admin.ModelAdmin),
  (models.ObituaryNotice, admin.ModelAdmin),
  (models.CemeteryRegisterCleanup, admin.ModelAdmin),
):
    admin.site.register(model, admin_model)
