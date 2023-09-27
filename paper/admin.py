from django.contrib import admin

from .models import Author, additional_Attribute, Paper, Paper_Author, Paper_Reviewer, Review, Reviewer, File

# Register your models here.
class additional_AttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper']

class additional_AttributeInline(admin.TabularInline):
    model = additional_Attribute

class ReviewerInline(admin.TabularInline):
    model = Paper.reviewers.through

class PaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'submitter', 'written_by', 'reviewed_by', 'paper_attributes',]
    inlines = [ReviewerInline, additional_AttributeInline]
    
    
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'user', 'email']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['paper', 'reviewer', 'date_reviewed']   

class Paper_ReviewerAdmin(admin.ModelAdmin):
    list_display = ['paper', 'reviewer', 'status']

class Paper_AuthorAdmin(admin.ModelAdmin):
    list_display = ['paper', 'author', 'order']    

class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'order']

# class OptionAdmin(admin.ModelAdmin):
#     list_display = ['text']

# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ['text']

# class AnswerAdmin(admin.ModelAdmin):
#     list_display = ['text']

admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(Paper_Reviewer, Paper_ReviewerAdmin)
admin.site.register(additional_Attribute, additional_AttributeAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Paper_Author, Paper_AuthorAdmin)
admin.site.register(File, FileAdmin)
# admin.site.register(Option, OptionAdmin)
# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Answer, AnswerAdmin)

