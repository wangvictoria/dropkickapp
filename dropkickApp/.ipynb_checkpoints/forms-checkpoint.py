from django import forms
from .models import MyFile

class UploadFileForm(forms.ModelForm):
    #name = forms.CharField(max_length = 50)
    #upload = forms.FileField()
    class Meta:
        model = MyFile
        fields = ('name', 'upload',)
    #obj, created = MyFile.objects.get_or_create(name='John', last_name='Lennon',
                  #defaults={'birthday': date(1940, 10, 9)})
    