from django.contrib import admin
from .models import additionalResearchArea, Role, User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class additionalResearchAreaInline(admin.TabularInline):
    model = additionalResearchArea

class CustomUserAdmin(UserAdmin):
    inlines = [
        additionalResearchAreaInline,
    ]
    list_display = ('email', 'first_name', 'last_name', 'username', 'research_areas', 'acting_as')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def research_areas(self, obj):
        return ", ".join([k.name for k in obj.researchAreas.all()])

class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(User, CustomUserAdmin)
admin.site.register(additionalResearchArea, ResearchAreaAdmin)

admin.site.register(Role)

