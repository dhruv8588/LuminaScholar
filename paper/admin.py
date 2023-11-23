from django.contrib import admin

from .models import Author, PreferencePaper_Reviewer, ReviewFile, additionalAttribute, Paper, Paper_Author, Paper_Reviewer, Review, Reviewer, File

# Register your models here.
class additionalAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper']

class additionalAttributeInline(admin.TabularInline):
    model = additionalAttribute

class ReviewerInline(admin.TabularInline):
    model = Paper.reviewers.through

class PaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'submitter', 'written_by', 'reviewed_by', 'paper_attributes', 'associate_editor']
    inlines = [ReviewerInline, additionalAttributeInline]
    
    
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['paper_reviewer']   

class Paper_ReviewerAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'reviewer', 'status', 'order']
    list_editable = ['status']

class Paper_AuthorAdmin(admin.ModelAdmin):
    list_display = ['paper', 'author', 'order']    

class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'order']

class RevFileAdmin(admin.ModelAdmin):
    list_display = ['review', 'file', 'view']    

class PreferencePaper_ReviewerAdmin(admin.ModelAdmin):
    list_display = ['paper', 'reviewer', 'preference', 'reason']

admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(Paper_Reviewer, Paper_ReviewerAdmin)
admin.site.register(additionalAttribute, additionalAttributeAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Paper_Author, Paper_AuthorAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(ReviewFile, RevFileAdmin)
admin.site.register(PreferencePaper_Reviewer, PreferencePaper_ReviewerAdmin)
