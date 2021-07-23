from django.shortcuts import render, get_object_or_404
from dropkickApp.models import MyFile
from django.views import generic
from .forms import UploadFileForm, CheckboxForm
from django.http import HttpResponse, StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import mimetypes

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

def labels(adata):
    adata_model = dk.dropkick(adata, n_jobs=5)
    
    coef_plt = dk.coef_plot(adata)
    # display chart
    buf_coef = io.BytesIO()
    coef_plt.savefig(buf_coef, format = 'png')
    buf_coef.seek(0)
    string_coef = base64.b64encode(buf_coef.read())
    uri_coef = urllib.parse.quote(string_coef)
    
    adata_score = dk.recipe_dropkick(adata, n_hvgs=None, verbose=False, filter=True, min_genes=50)
    score_plt = dk.score_plot(adata_score)
    # display chart
    buf_score = io.BytesIO()
    score_plt.savefig(buf_score, format = 'png')
    buf_score.seek(0)
    string_score = base64.b64encode(buf_score.read())
    uri_score = urllib.parse.quote(string_score)
    
    
    return adata.obs, uri_score, uri_coef

def index(request):
    """View function for home page of site."""
    
    context = {
        'title': None,
        'qc_text': None, 'score_text': None, 'coef_text': None, 'labels_text': None,
        'qc_plot': None, 'score_plot': None, 'coef_plot': None, 'labels': None,
    }
    
    # upload file
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        #uploaded_file.name = request.FILES['name']
        #print(uploaded_file.name)
        #print(uploaded_file.size)
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        
        # read data
        adata = sc.read('media/' + uploaded_file.name)
        
        
        # label data results
        context['title'] = 'Your Results'
        context['qc_text'] = 'QC Plot'

        # run scripts and create plots
        
        # checkbox bool
        form = CheckboxForm(request.POST or None)
        if form.is_valid():
            if request.POST['qc_plot']:
                # qc_plot checkbox was checked
                context['qc_plot'] = qc_plot(adata)
            if request.POST['filter']:
                # filter checkbox was checked
                # run dropkick
                context['score_text'] = 'Score Plot'
                context['coef_text'] = 'Coefficient Plot'
                context['labels_text'] = 'Dropkick Labels'
                df, context['score_plot'], context['coef_plot'] = labels(adata)
                
                # convert dataframe to csv
                fl_path = 'media/'
                filename = uploaded_file.name + '_dropkick.csv'
                df.to_csv('media/dropkick_filter.csv')
                
                #content = file(filename).read()
                #response = HttpResponse(content, content_type='text/csv')
                #response['Content-Length'] = os.path.getsize(filename)
                #response['Content-Disposition'] = 'attachment; filename=%s' % filename
                
                #response = StreamingHttpResponse(fl_path + filename, content_type="text/csv")
                #response['Content-Disposition'] = 'attachment; filename=%s' %filename
#                 fl_path = 'media/'
#                 filename = uploaded_file.name + '_dropkick.csv'
#                 df.to_csv(fl_path + filename)
#                 fl = open(fl_path, filename)
#                 response = HttpResponse(fl, content_type=mime_type)
#                 response['Content-Disposition'] = "attachment; filename=%s" % filename
                #context['labels'] = response
                
        else:
            form = CheckboxForm
        
    return render(request,'index.html', context)

def download_file(request):
    # response content type
    response = HttpResponse(content_type='text/csv')

    #decide the file name
    response['Content-Disposition'] = 'attachment; filename="dropkick_filter.csv"'
    return response

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
