from django.shortcuts import render, get_object_or_404
from dropkickApp.models import MyFile
from django.views import generic
from .forms import UploadFileForm
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

import scanpy as sc; sc.set_figure_params(color_map="viridis", frameon=False)
import dropkick as dk
import matplotlib.pyplot as plt
import io, base64, urllib
import numpy as np


def qc_plot(adata):
    # plot QC metrics
    adata = dk.recipe_dropkick(adata, n_hvgs=None, X_final="raw_counts")
    qc_plt = dk.qc_summary(adata)
    
    # display chart
    buf = io.BytesIO()
    qc_plt.savefig(buf, format = 'png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def score_plot(adata):
    score_plt = dk.score_plot(adata)
    
    # display chart
    buf = io.BytesIO()
    score_plt.savefig(buf, format = 'png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def coef_plot(adata):
    coef_plt = dk.coef_plot(adata)
    
    # display chart
    buf = io.BytesIO()
    coef_plt.savefig(buf, format = 'png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def labels(adata):
    adata_model = dk.dropkick(adata, n_jobs=5)
    return adata_model

def index(request):
    """View function for home page of site."""
    
    context = {'qc_plot': None, 'score_plot': None, 'coef_plot': None, 'labels': None}
    
    # upload file
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        #print(uploaded_file.name)
        #print(uploaded_file.size)
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
    
        # read data
        adata = sc.read('media/' + uploaded_file.name)
        
        # run dropkick
        #adata_model = dk.dropkick(adata, n_jobs=5)

        # run scripts and create plots
        
        context['qc_plot'] = qc_plot(adata)
        #context['score_plot'] = score_plot(adata)
        #context['coef_plot'] = coef_plot(adata)
        #context['labels'] = labels(adata)
        
    return render(request,'index.html', context)

#     # Generate count of files
#     num_files = MyFile.objects.all().count()
    
#     context = {
#         'num_files': num_files,
#     }
    
#     results = run_script()
#     context['results'] = results
    
    # Render the HTML template index.html with the data in the context variable
    #return render(request, 'index.html', context=context)

# def upload_file(request):
#     if request.method == 'POST':
#         uploaded_file = request.FILES['document']
#         #print(uploaded_file.name)
#         #print(uploaded_file.size)
#         fs = FileSystemStorage()
#         fs.save(uploaded_file.name, uploaded_file)
#     return render(request,'upload.html')

# def process(request):
#     model = MyFile
#     num_files = MyFile.objects.all().count()
    
#     context = {
#         'num_files': num_files,
#     }
#     return render(request, 'process.html')


# def run_script():
#     adata = sc.read("../media/3907_S1_jointcluster.h5ad")
#     # plot QC metrics
#     adata = dk.recipe_dropkick(adata, n_hvgs=None, X_final="raw_counts")
#     qc_plt = dk.qc_summary(adata)
#     return render(request,'process.html')
