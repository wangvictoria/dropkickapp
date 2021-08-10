from django.shortcuts import render, get_object_or_404
from dropkickApp.models import MyFile
from django.views import generic
from .forms import UploadFileForm, CheckboxForm, CustomForm
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
from django.core.files.storage import FileSystemStorage
import csv
import os
import zipfile
from io import BytesIO

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
    qc_plt.savefig('media/qc_plot.png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def labels(adata, min_genes, mito_names, n_ambient, n_hvgs, metrics, thresh_methods, directions, alphas, max_iter, n_jobs, seed):
    adata_model = dk.dropkick(
        adata, 
        min_genes=min_genes, 
        mito_names=mito_names, 
        n_ambient=n_ambient,
        n_hvgs=n_hvgs,
        metrics=metrics,
        thresh_methods=thresh_methods,
        directions=directions,
        alphas=[0.1],
        max_iter=max_iter,
        n_jobs=n_jobs,
        seed=seed)
    
    # display coefficient plot
    coef_plt = dk.coef_plot(adata)
    buf_coef = io.BytesIO()
    coef_plt.savefig(buf_coef, format = 'png')
    coef_plt.savefig('media/coef_plot.png')
    buf_coef.seek(0)
    string_coef = base64.b64encode(buf_coef.read())
    uri_coef = urllib.parse.quote(string_coef)
    
    # display score plot
    adata_score = dk.recipe_dropkick(adata, n_hvgs=None, verbose=False, filter=True, min_genes=50)
    score_plt = dk.score_plot(adata_score)
    buf_score = io.BytesIO()
    score_plt.savefig(buf_score, format = 'png')
    score_plt.savefig('media/score_plot.png')
    buf_score.seek(0)
    string_score = base64.b64encode(buf_score.read())
    uri_score = urllib.parse.quote(string_score)
    
    return adata, uri_score, uri_coef

def index(request):
    """View function for home page of site."""
    
    context = {
        'title': None,
        'qc_text': None, 'score_text': None, 'coef_text': None, 'labels_text': None,
        'qc_plot': None, 'score_plot': None, 'coef_plot': None, 'labels': None,
    }
    
    # upload file
    if request.method == 'POST':
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            fs = FileSystemStorage()
            fs.save(uploaded_file.name, uploaded_file)

            # read data
            adata = sc.read('media/' + uploaded_file.name)

            # label data results
            context['title'] = 'Your Results'

            # checkbox bool
            form = CheckboxForm(request.POST or None)
            if form.is_valid():
                if request.POST.get('qc_plot'):
                    # qc_plot checkbox was checked
                    context['qc_text'] = 'QC Plot'
                    context['qc_plot'] = qc_plot(adata)
                if request.POST.get('dropkick'):
                    # filter checkbox was checked
                    
                    # run dropkick
                    context['score_text'] = 'Score Plot'
                    context['coef_text'] = 'Coefficient Plot'
                    context['labels_text'] = 'Dropkick Labels'
                    
                    # default or custom settings
                    #form_param = DropkickParam(request.POST or None)
                    #if form_param.is_valid():
                    min_genes = int(form.cleaned_data.get('min_genes', None))
                    mito_names = form.cleaned_data.get('mito_names', None)
                    n_ambient = int(form.cleaned_data.get('n_ambient', None))
                    n_hvgs = int(form.cleaned_data.get('n_hvgs', None))
                    metrics = form.cleaned_data.get('metrics', None)
                    thresh_methods = form.cleaned_data.get('thresh_methods', None)
                    directions = form.cleaned_data.get('directions', None)
                    alphas = form.cleaned_data.get('alphas', None) # how to make into list???
                    max_iter = int(form.cleaned_data.get('max_iter', None))
                    n_jobs = int(form.cleaned_data.get('n_jobs', None))
                    seed = int(form.cleaned_data.get('seed', None))
                    df, context['score_plot'], context['coef_plot'] = labels(
                        adata, min_genes, mito_names, n_ambient, n_hvgs, metrics, thresh_methods, directions, alphas, max_iter, n_jobs, seed)
                    # convert dataframe to csv
                    fl_path = 'media/'
                    filename = uploaded_file.name + '_dropkick.csv'
                    df.obs.to_csv('media/dropkick_labels.csv')
                    
                    # convert to h5ad file
                    adata.write('media/dropkick_filter.h5ad', compression='gzip')
                    
                    # delete file
                    if os.path.exists('media/' + uploaded_file.name):
                        os.remove('media/' + uploaded_file.name)
                    
                    # TODO: fix info hover, alpha lists, and validation check
                    
            else:
                form = CheckboxForm
        
    return render(request,'index.html', context)

def download_csv(request):
    file = open('media/dropkick_labels.csv', 'rb') # Read the file in binary mode, this file must exist
    response = FileResponse(file)

    # decide the file name
    response['Content-Disposition'] = 'attachment; filename="dropkick_labels.csv"'
    return response

def download_h5ad(request):
    file = open('media/dropkick_filter.h5ad', 'rb') # Read the file in binary mode, this file must exist
    response = FileResponse(file)

    # decide the file name
    response['Content-Disposition'] = 'attachment; filename="dropkick_filter.h5ad"'
    return response

def download_sample(request):
    file = open('media/t_4k_small_dropkick_scores.csv', 'rb') # Read the file in binary mode, this file must exist
    response = FileResponse(file)
    
    response['Content-Disposition'] = 'attachment; filename="sample_dropkick_scores.csv"'
    return response

def download_qc(request):
    file = open('media/qc_plot.png', 'rb') # Read the file in binary mode, this file must exist
    response = FileResponse(file)
    
    response['Content-Disposition'] = 'attachment; filename="qc_plot.png"'
    return response

def download_coef(request):
    file = open('media/coef_plot.png', 'rb') # Read the file in binary mode, this file must exist
    response = FileResponse(file)
    
    response['Content-Disposition'] = 'attachment; filename="coef_plot.png"'
    return response

def download_score(request):
    file = open('media/score_plot.png', 'rb') # Read the file in binary mode, this file must exist
    response = FileResponse(file)
    
    response['Content-Disposition'] = 'attachment; filename="score_plot.png"'
    return response

def download_all_no_qc(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = ["media/dropkick_labels.csv", "media/dropkick_filter.h5ad", "media/coef_plot.png", "media/score_plot.png"]
    
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "dropkick_output"
    zip_filename = "%s.zip" % zip_subdir
    
    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")

    # ..and correct content-disposition
    response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return response

def download_all(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = ["media/dropkick_labels.csv", "media/dropkick_filter.h5ad", "media/qc_plot.png", "media/coef_plot.png", "media/score_plot.png"]
    
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "dropkick_output"
    zip_filename = "%s.zip" % zip_subdir
    
    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")

    # ..and correct content-disposition
    response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

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
