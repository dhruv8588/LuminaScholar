from django import forms
from django.forms import modelformset_factory

from accounts.models import User
from paper.models import Reviewer

# class ReviewerForm(forms.Form):
#     email = forms.EmailField()       

class ReviewerForm(forms.ModelForm):
    class Meta:
        model = Reviewer
        fields = ['first_name', 'last_name', 'email']

class InviteUserForm(forms.ModelForm):
    is_invited = forms.BooleanField(required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
      
UserModelFormset = modelformset_factory(
    User,
    # fields = ['first_name', 'last_name'],
    form = InviteUserForm,
    extra = 0,
)        

