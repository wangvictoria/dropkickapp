from django import forms
from .models import MyFile

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = MyFile
        fields = ('name', 'upload',)