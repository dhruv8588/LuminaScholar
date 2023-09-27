from django.contrib import admin
from .models import ResearchArea, Role, User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class ResearchAreaInline(admin.TabularInline):
    model = ResearchArea

class CustomUserAdmin(UserAdmin):
    inlines = [
        ResearchAreaInline,
    ]
    list_display = ('email', 'first_name', 'last_name', 'username', 'research_areas', 'acting_as')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def research_areas(self, obj):
        return ", ".join([k.name for k in obj.research_areas.all()])

class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(User, CustomUserAdmin)
admin.site.register(ResearchArea, ResearchAreaAdmin)

admin.site.register(Role)

