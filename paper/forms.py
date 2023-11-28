from django import forms
from accounts.models import Role
from paper.models import AERecommendation, Author, EICDecision, Paper, ReviewFile, Review, additionalAttribute


# class PaperForm(forms.ModelForm):
#     # file = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), required=False) #, validators=[allow_only_pdf_or_docx_validator]
#     is_submitter_author = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
#     class Meta:
#         model = Paper
#         fields = ['title', 'abstract', 'file', 'is_submitter_author'] 


class PaperForm1(forms.ModelForm):
    TYPE_CHOICES = [
        ('Review Article', 'Review Article'),
        ('Experimental Original', 'Experimental Original'),
        ('Clinical Original', 'Clinical Original'),
        ('Short Communication', 'Short Communication'),
        ('How To Do It', 'How To Do It'),
        ('Letter to the Editor', 'Letter to the Editor'),
        ('Invited Review Article', 'Invited Review Article')
    ]
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=TYPE_CHOICES, required=False)
    class Meta:
        model = Paper
        fields = ['type', 'title', 'abstract']
        widgets = {
          'abstract': forms.Textarea(attrs={'rows':4, 'cols':100}),
          'title': forms.Textarea(attrs={'rows':2, 'cols':50})
        }


class PaperForm2(forms.ModelForm):
    MSWord_file_choices = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('N/A', 'N/A')
    ]
    certification_form_choices = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('N/A', 'N/A')
    ]
    publish_elsewhere_choices = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('N/A', 'N/A')
    ]
    approval_choices = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]
    appropriate_statement_choices = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]
    figures_tables_published_elsewhere_choices = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]
    MSWord_file = forms.ChoiceField(widget=forms.RadioSelect, choices=MSWord_file_choices, required=False)
    certification_form = forms.ChoiceField(widget=forms.RadioSelect, choices=certification_form_choices, required=False)
    publish_elsewhere = forms.ChoiceField(widget=forms.RadioSelect, choices=publish_elsewhere_choices, required=False)
    approval = forms.ChoiceField(widget=forms.RadioSelect, choices=approval_choices, required=False)
    appropriate_statement = forms.ChoiceField(widget=forms.RadioSelect, choices=appropriate_statement_choices, required=False)
    figures_tables_published_elsewhere = forms.ChoiceField(widget=forms.RadioSelect, choices=figures_tables_published_elsewhere_choices, required=False)
    class Meta:
        model = Paper
        fields = ['cover_letter', 'number_of_figures', 'number_of_tables', 'word_count', 'MSWord_file', 'certification_form', 'publish_elsewhere', 'approval', 'appropriate_statement', 'figures_tables_published_elsewhere', 'figures_tables_published_elsewhere_desc']
        widgets = {
          'cover_letter': forms.Textarea(attrs={'rows':5, 'cols':100}),
          'figures_tables_published_elsewhere_desc': forms.Textarea(attrs={'rows':4, 'cols':100})
        }


class PaperForm3(forms.ModelForm):
    # def __init__(self, *args, conference=None, **kwargs):
    #     super(PaperForm3, self).__init__(*args, **kwargs)
    #     self.fields['attributes'].queryset = Attribute.objects.filter(conference=conference)

    class Meta:
        model = Paper
        fields = ['attributes']


class PaperForm4(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ['decision_response']
        widgets = {
          'decision_response': forms.Textarea(attrs={'rows':5, 'cols':100}),
        }


class AssignEditorForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ['associate_editor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter users based on the "Associate Editor" role
        associate_editors = Role.objects.get(name='Associate Editor').users.all()
        self.fields['associate_editor'].queryset = associate_editors    


class additionalAttributeForm(forms.ModelForm):
    class Meta:
        models: additionalAttribute
        fields = ['name']    

additionalAttributeFormSet = forms.inlineformset_factory(
    Paper, additionalAttribute, form=additionalAttributeForm,
    extra=1
)        

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'email']
    
  
class ReviewForm(forms.ModelForm):
    CHOICES_1 = [
        ('Full length technical paper', 'Full length technical paper'),
        ('Short technical note', 'Short technical note'),
        ('Tutorial/Survey paper', 'Tutorial/Survey paper')
    ]
    CHOICES_2 = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    CHOICES_3 = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    ]
    CHOICES_4 = [
        ('Light', 'Light'),
        ('Moderate', 'Moderate'),
        ('Heavy', 'Heavy'),
        ('None', 'None')
    ]
    CHOICES_5 = [
        ('Accept', 'Accept'),
        ('Minor Revision', 'Minor Revision'),
        ('Major Revision', 'Major Revision'),
        ('Reject and Resubmit', 'Reject and Resubmit'),
        ('Reject', 'Reject')
    ]
    paper_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_1, required=False)
    has_best_paper_award_potential = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    is_innovative = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_3, required=False)
    anything_to_be_deleted = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    amt_of_copy_editing = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_4, required=False)
    interest_to_engineers = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    will_review_revised_version = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    recommendation = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_5, required=False)

    class Meta:
        model = Review
        fields = ['paper_type', 'has_best_paper_award_potential', 'is_innovative', 'rating', 'anything_to_be_deleted', 'what_should_be_deleted', 'amt_of_copy_editing', 'interest_to_engineers', 'will_review_revised_version', 'recommendation', 'comments_to_editor', 'comments_to_author']
        widgets = {
          'comments_to_editor': forms.Textarea(attrs={'rows':4, 'cols':50}),
          'comments_to_author': forms.Textarea(attrs={'rows':4, 'cols':50}),
          'what_should_be_deleted': forms.Textarea(attrs={'rows':4, 'cols':50}),
        }


class RevFileForm(forms.ModelForm):
    view_choices = [
        ('Editor Only', 'Editor Only'),
        ('Author & Editor', 'Author & Editor'),
    ]
    view = forms.ChoiceField(widget=forms.RadioSelect, choices=view_choices, required=False)
    class Meta:
        model = ReviewFile
        fields = ['file', 'view']

ReviewFileModelFormset = forms.modelformset_factory(
    ReviewFile,
    form=RevFileForm,
    extra=0,
)


class AERecommendationForm(forms.ModelForm):
    recommendation_choices = [
        ('Accept', 'Accept'),
        ('Minor Revision', 'Minor Revision'),
        ('Major Revision', 'Major Revision'),
        ('Reject', 'Reject')
    ]
    recommendation = forms.ChoiceField(widget=forms.RadioSelect, choices=recommendation_choices, required=False)
    class Meta:
        model = AERecommendation
        fields = ['recommendation', 'comments_to_eic', 'comments_to_author']
        widgets = {
          'comments_to_eic': forms.Textarea(attrs={'rows':4, 'cols':50}),
          'comments_to_author': forms.Textarea(attrs={'rows':4, 'cols':50}),
        }

class EICDecisionForm(forms.ModelForm):
    decision_choices = [
        ('Accept', 'Accept'),
        ('Minor Revision', 'Minor Revision'),
        ('Major Revision', 'Major Revision'),
        ('Reject', 'Reject')
    ]
    decision = forms.ChoiceField(widget=forms.RadioSelect, choices=decision_choices, required=False)
    class Meta:
        model = EICDecision
        fields = ['decision', 'comments']
        widgets = {
          'comments': forms.Textarea(attrs={'rows':4, 'cols':50}),
        }        