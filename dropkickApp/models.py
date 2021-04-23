from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import ModelFormWithFileField

# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class MyFile(models.Model):
    """Model representing a file that the user uploads."""
    name = models.CharField('file name', max_length=500, help_text='Enter file output name.', blank=True)
    upload = models.FileField(upload_to='uploads/', help_text='Only H5AD files are supported.')
    uploaded_at = models.DateTimeField('upload date', auto_now=True)
    
    class Meta:
        verbose_name = "file"
        ordering = ['uploaded_at', 'name']
    
    def __str__(self):
        """String for representing the Model object."""
        return self.name
    
    def get_absolute_url(self):
        """Returns the url to access a detail record for this file."""
        return reverse('file-detail', args=[str(self.id)])