'''
Created on 5.4.2015

@author: Ondrej
'''
from django import forms
from django.forms.models import inlineformset_factory
from django.forms.widgets import Textarea

from decision.models import CustomUser, Decision, Criteria_Variant
from django.contrib.auth.forms import UserCreationForm


class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'image')

class DecisionForm(forms.ModelForm):
    description = forms.CharField( widget=forms.Textarea(attrs={'rows':4,}) )
    class Meta:
        model = Decision
        fields = ('name', 'description', 'image')
        
CriteriaVariantFormSet = inlineformset_factory(Decision,
                                               Criteria_Variant,
                                               fields=('name','description', 'image', 'crit_var'),
                                               extra=0,
                                               min_num=2,
                                               widgets={'description': Textarea(attrs={'rows':4,})})