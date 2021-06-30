from django.shortcuts import render, get_object_or_404, redirect
from .models import MyFile
from django.views import generic
from .forms import UploadFileForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Create your views here.

def index(request):
    """View function for home page of site."""
    
    # Generate count of files
    num_files = MyFile.objects.all().count()
    
    context = {
        'num_files': num_files,
    }
    
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def handle_uploaded_file(f):
    files = MyFile.objects.all()
    return render(request, 'process.html', {'files: file'})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('handle_uploaded_file')
        else:
            form = UploadFileForm()
#     context = {}
#     if request.method == 'POST':
#         uploaded_file = request.FILES['upload']
#         fs = FileSystemStorage()
#         name = fs.save(uploaded_file.name, uploaded_file)
#         context['url'] = fs.url(name)
#         print(uploaded_file.name)
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#             # file is saved
            
#             #new = Storage()
#             #new.file = request.FILES['file']
#             #new.save()
            
#             #profile = Profile()
#             #profile.name = MyProfileForm.cleaned_data["name"]
#             #profile.picture = MyProfileForm.cleaned_data["picture"]
#             #profile.save()
#             #saved = True
            
#             #user_process = form.save(commit = False)
#             #user_process.run_dropkick = request.FILES['upload']
#             #return HttpResponseRedirect('/success/url/')
#     else:
#         form = UploadFileForm()
    return render(request, 'index.html', { 'form': form })

#def read(request):
    #file = request.FILES[MyFile.name]
    #df = pd.read_csv('file')
    #file = open(os.path.join(settings.BASE_DIR, 'filename'))