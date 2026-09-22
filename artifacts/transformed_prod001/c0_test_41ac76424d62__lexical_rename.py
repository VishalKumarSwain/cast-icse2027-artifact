

from django.conf import settings
from django.contrib import admin
from .fields import BaseJSONWidget
from .models import ModelWithJSONField
from django.db import models

class ModelWithJSONFieldAdmin(admin.ModelAdmin):
    list_display_renamed = ('id', 'json_field')
    search_fields = ['json_field']
    formfield_overrides = {
        models.JSONField: {'widget': BaseJSONWidget},
    }

settings.register(ModelWithJSONFieldAdmin) # register admin class
admin.site.register(ModelWithJSONField, ModelWithJSONFieldAdmin) # register model with admin
