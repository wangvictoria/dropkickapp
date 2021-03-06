from django.contrib import admin
from .models import MyFile

# Register your models here.

class MyFileAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at', 'name')
    list_filter = ('uploaded_at', 'name')

admin.site.register(MyFile, MyFileAdmin)