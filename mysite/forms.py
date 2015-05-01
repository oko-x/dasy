'''
Created on 5.4.2015

@author: Ondrej
'''
from django import forms
from django.forms.models import inlineformset_factory

from decision.models import CustomUser, Decision, Criteria_Variant


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ('name', 'description', 'image')
        
CriteriaVariantFormSet = inlineformset_factory(Decision, Criteria_Variant, fields=('name','description', 'image', 'crit_var'), extra=0, min_num=2,)