from django.db import models
from django.db.models.fields.related import OneToOneField
from django.db.models.functions import Lower

from accounts.models import User
from conference.models import Attribute

# Create your models here.

class Author(models.Model):
    user = OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + " " + self.last_name
    
    class Meta:
        ordering = [Lower('first_name'), Lower('last_name')]


class Reviewer(models.Model):
    user = OneToOneField(User, on_delete=models.SET_NULL, related_name='reviewer', blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Paper(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='submitted_papers', blank=True, null=True)
    reviewers = models.ManyToManyField(Reviewer, related_name='papers', through='Paper_Reviewer', blank=True)

    associate_editor = models.OneToOneField(User, on_delete=models.SET_NULL, related_name="papers", blank=True, null=True)
    journal_id = models.CharField(max_length=50, blank=True)

    type = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, blank=True)
    abstract = models.TextField(max_length=300, blank=True)

    authors = models.ManyToManyField(Author, related_name='papers', through='Paper_Author', blank=True)

    attributes = models.ManyToManyField(Attribute, blank=True)

    is_submitted = models.BooleanField(default=False)

    cover_letter = models.TextField(blank=True, null=True)
    cover_letter_file = models.FileField(upload_to='conference/papers', blank=True, null=True)
    number_of_figures = models.PositiveSmallIntegerField(blank=True, null=True)
    number_of_tables = models.PositiveSmallIntegerField(blank=True, null=True)
    word_count = models.PositiveSmallIntegerField(blank=True, null=True)
    MSWord_file = models.CharField(max_length=10, blank=True, null=True)
    certification_form = models.CharField(max_length=10, blank=True, null=True)
    publish_elsewhere = models.CharField(max_length=10, blank=True, null=True)
    approval = models.CharField(max_length=10, blank=True, null=True)
    appropriate_statement = models.CharField(max_length=10, blank=True, null=True) 
    figures_tables_published_elsewhere = models.CharField(max_length=10, blank=True, null=True)
    figures_tables_published_elsewhere_desc = models.TextField(blank=True, null=True)
    
    date_submitted = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    associate_editor = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_papers', blank=True, null=True)

    required_reviews = models.PositiveSmallIntegerField(default=2, blank=True, null=True)

    def written_by(self):
        return ", ".join([str(i) for i in self.authors.all()])
    
    def reviewed_by(self):
        return ", ".join([str(i) for i in self.reviewers.all()])
    
    def paper_attributes(self):
        return ", ".join([str(i) for i in self.attributes.all()])

    def __str__(self):
        return self.title
    

class Paper_Author(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = ('paper_id', 'author_id')
        verbose_name = 'Paper_Author_pair'
        verbose_name_plural = 'Paper_Author_pairs'


class File(models.Model):
    paper = models.ForeignKey(Paper, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to='files', blank=True, null=True)
    order = models.PositiveSmallIntegerField(blank=True, null=True)

    # attribute = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return self.file.name


# class Image(models.Model):
#     file = models.OneToOneField(File, on_delete=models.CASCADE)
#     caption = models.CharField(max_length=100, blank=True)
#     link_text  = models.CharField(max_length=100, blank=True)


class Paper_Reviewer(models.Model):
    status_choices = (
        ('Agreed', 'Agreed'),
        ('Declined', 'Declined'),
    )
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=status_choices, blank=True)
    is_invited = models.BooleanField(default=False)
    class Meta:
        ordering = ['order']
        unique_together = ('paper', 'reviewer')
        verbose_name = 'Paper_Reviewer_pair'
        verbose_name_plural = 'Paper_Reviewer_pairs'
    
    
class additionalAttribute(models.Model):
    name = models.CharField(max_length=100, blank=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='additionalAttributes', blank=True, null=True)

    class Meta:
        verbose_name = 'additionalAttribute'
        verbose_name_plural = 'additionalAttributes'

    def __str__(self):
        return self.name


class Review(models.Model):
    paper = models.ForeignKey(Paper, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, related_name="reviews", on_delete=models.CASCADE)
    # body = models.TextField()
    date_reviewed = models.DateTimeField(auto_now_add=True)

    paper_type = models.CharField(max_length=100, blank=True)
    has_best_paper_award_potential = models.CharField(max_length=10, blank=True)
    is_innovative = models.CharField(max_length=10, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    anything_to_be_deleted = models.CharField(max_length=10, blank=True)
    what_should_be_deleted = models.TextField(blank=True)
    amt_of_copy_editing = models.CharField(max_length=20, blank=True)
    interest_to_engineers = models.CharField(max_length=10, blank=True)
    will_review_revised_version = models.CharField(max_length=10, blank=True)
    recommendation = models.CharField(max_length=50, blank=True)
    comments_to_editor = models.TextField(blank=True)
    comments_to_author = models.TextField(blank=True)

    is_submitted = models.BooleanField(default=False)
    

