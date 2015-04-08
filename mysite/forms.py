'''
Created on 5.4.2015

@author: Ondrej
'''
from django import forms
from decision.models import CustomUser


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