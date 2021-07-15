from django.shortcuts import render, get_object_or_404
from dropkickApp.models import MyFile
from django.views import generic
from .forms import UploadFileForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
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

def upload_file(request):
    # if request.method == 'POST':
    #     my_form = UploadFileForm(request.POST, request.FILES)
    #     if my_form.is_valid():
    #         # file is saved
    #         my_form.save()
    #         return HttpResponseRedirect('/success/url/')
    # else:
    #     my_form = UploadFileForm()
    # return render(request, 'upload.html', {'form': form})

    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        #print(uploaded_file.name)
        #print(uploaded_file.size)
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
    return render(request,'upload.html')

def process(request):
    model = MyFile
    num_files = MyFile.objects.all().count()
    
    context = {
        'num_files': num_files,
    }
    return render(request, 'process.html')


# def run_script():
#     adata = sc.read("../media/3907_S1_jointcluster.h5ad")
#     # plot QC metrics
#     adata = dk.recipe_dropkick(adata, n_hvgs=None, X_final="raw_counts")
#     qc_plt = dk.qc_summary(adata)
#     return render(request,'process.html')
