from django import forms

from .models import additionalResearchArea, User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'institution', 'country', 'state', 'city', 'researchAreas'] 

    # def clean(self):
    #     cleaned_data =  super(UserForm, self).clean()    
    #     email = cleaned_data.get('email')

    #     user = User.objects.get(email=email, role='Editor')

    #     if password != confirm_password:
    #         raise forms.ValidationError(
    #             "Password does not match!"
    #         )    
        
class additionalResearchAreaForm(forms.ModelForm):
    class Meta:
        model = additionalResearchArea       
        fields = ['name']

# ResearchAreaModelFormset = forms.formset_factory(
#     ResearchArea,
#     #form = ResearchAreaForm,
#     # fields = ['name'],
#     extra = 0
# )

additionalResearchAreaFormSet = forms.inlineformset_factory(
    User, additionalResearchArea, form=additionalResearchAreaForm,
    extra=1,
    # max_num=2, absolute_max=2, 
    # validate_max = True,
    # min_num=1,
    # validate_min=True
    
)        

