from django.contrib import admin
from user.models import TestDrive, UserImage

# Register your models here.

class TestDriveAdmin(admin.ModelAdmin):

    search_fields = ['username']

class UserImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(model_or_iterable=TestDrive, admin_class=TestDriveAdmin)
admin.site.register(model_or_iterable=UserImage, admin_class=UserImageAdmin)