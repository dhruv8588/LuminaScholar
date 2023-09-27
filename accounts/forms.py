from django import forms

from .models import ResearchArea, User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] 

    # def clean(self):
    #     cleaned_data =  super(UserForm, self).clean()    
    #     email = cleaned_data.get('email')

    #     user = User.objects.get(email=email, role='Editor')

    #     if password != confirm_password:
    #         raise forms.ValidationError(
    #             "Password does not match!"
    #         )    
        
class ResearchAreaForm(forms.ModelForm):
    class Meta:
        model = ResearchArea       
        fields = ['name']

# ResearchAreaModelFormset = forms.formset_factory(
#     ResearchArea,
#     #form = ResearchAreaForm,
#     # fields = ['name'],
#     extra = 0
# )

ResearchAreaFormSet = forms.inlineformset_factory(
    User, ResearchArea, form=ResearchAreaForm,
    extra=1,
)        

