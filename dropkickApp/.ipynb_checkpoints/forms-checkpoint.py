from django import forms
from .models import MyFile

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = MyFile
        fields = ('name', 'upload',)

class CheckboxForm(forms.Form):
    qc_plot = forms.BooleanField(label = "qc_plot", required = False)
    filer = forms.BooleanField(label = "filter", required = False)