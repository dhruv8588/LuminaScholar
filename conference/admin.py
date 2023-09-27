from django.contrib import admin

from .models import Attribute, Editor
 
class EditorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

# Register your models here.
admin.site.register(Editor, EditorAdmin)
admin.site.register(Attribute)
