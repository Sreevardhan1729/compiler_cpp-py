from django import forms

class SubmissionForm(forms.Form):
    language = forms.ChoiceField(choices=[('cpp', 'C++'), ('py', 'Python')])
    code = forms.CharField(widget=forms.HiddenInput())
    stdin = forms.CharField(widget=forms.Textarea, required=False)