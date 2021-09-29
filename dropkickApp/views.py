from django.shortcuts import render, get_object_or_404
from dropkickApp.models import MyFile
from django.views import generic
from .forms import UploadFileForm, CheckboxForm, CustomForm, ScoreForm
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
from django.core.files.storage import FileSystemStorage
import csv
import os
import zipfile
from io import BytesIO
from django.core.exceptions import ValidationError
from django.contrib import messages

import scanpy as sc; sc.set_figure_params(color_map="viridis", frameon=False)
import dropkick as dk
import matplotlib.pyplot as plt; plt.switch_backend("Agg")
import io, base64, urllib
import numpy as np
import pandas as pd


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

def labels(adata, min_genes, mito_names, n_ambient, n_hvgs, thresh_methods, alphas, max_iter, seed):
    adata_model = dk.dropkick(
        adata, 
        min_genes=min_genes, 
        mito_names=mito_names, 
        n_ambient=n_ambient,
        n_hvgs=n_hvgs,
        thresh_methods=thresh_methods,
        alphas=alphas,
        max_iter=max_iter,
        n_jobs=5,
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

def check_int(value):
    if isinstance(value, int):
        return int(value)
    else:
        messages.error(request, 'Please enter a non-negative integer.')
        
def check_int(value):
    if isinstance(value, float):
        return float(value)
    else:
        messages.error(request, 'Please enter a non-negative integer.')

def index(request):
    """View function for home page of site."""
    
    context = {
        'title': None, 'counts_text': None, 'counts_false': None, 'counts_true': None, 
        'qc_text': None, 'score_text': None, 'coef_text': None, 'labels_text': None,
        'qc_plot': None, 'score_plot': None, 'coef_plot': None, 'labels': None,
    }
    
    # upload file
    if request.method == 'POST':
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            if uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.h5ad') or uploaded_file.name.endswith('.tsv'):
                fs = FileSystemStorage()
                fs.save(uploaded_file.name, uploaded_file)
            
                # checkbox bool
                form = CheckboxForm(request.POST or None)
                #params = [min_genes, mito_names, n_ambient, n_hvgs, thresh_methods, alphas_list, max_iter, seed]
                if form.is_valid():

                    # default or custom settings
                    min_genes = int(form.cleaned_data.get('min_genes', None))
                    mito_names = form.cleaned_data.get('mito_names', None)
                    n_ambient = int(form.cleaned_data.get('n_ambient', None))
                    n_hvgs = int(form.cleaned_data.get('n_hvgs', None))
                    thresh_methods = form.cleaned_data.get('thresh_methods', None)
                    score_thresh = float(form.cleaned_data.get('score_thresh', None))
                    alphas_list = form.cleaned_data.get('alphas', None).split(",")
                    alphas = [float(x) for x in alphas_list]
                    max_iter = int(form.cleaned_data.get('max_iter', None))
                    seed = int(form.cleaned_data.get('seed', None))

                    # read data
                    adata = sc.read('media/' + uploaded_file.name)

                    # label data results
                    context['title'] = 'Your Results'

                    if request.POST.get('qc_plot'):
                        # qc_plot checkbox was checked
                        context['qc_text'] = 'QC Plot'
                        context['qc_plot'] = qc_plot(adata)
                    if request.POST.get('dropkick'):
                        # filter checkbox was checked


                        # run dropkick
                        context['counts_text'] = 'Droplets Inventory'
                        context['score_text'] = 'Score Plot'
                        context['coef_text'] = 'Coefficient Plot'
                        context['labels_text'] = 'Dropkick Labels'


                        df, context['score_plot'], context['coef_plot'] = labels(
                            adata, min_genes, mito_names, n_ambient, n_hvgs, thresh_methods, alphas, max_iter, seed)

                        df.obs['dropkick_label'] = df.obs['dropkick_score'] > score_thresh

                        context['counts_false'] = df.obs['dropkick_label'].value_counts()[0]
                        context['counts_true'] = df.obs['dropkick_label'].value_counts()[1]

                        # convert dataframe to csv
                        fl_path = 'media/'
                        filename = uploaded_file.name + '_dropkick.csv'
                        df.obs.to_csv('media/dropkick_labels.csv')

                        # convert to h5ad file
                        adata.write('media/dropkick_filter.h5ad', compression='gzip')

                        # output counts and genes matrices
                        data_out = adata[df.obs['dropkick_label']==True]
                        data = pd.DataFrame(data_out.X.toarray())
                        data.to_csv('media/dropkick_counts.csv', header=False, index=False)
                        pd.DataFrame(data_out.var_names).to_csv('media/dropkick_genes.csv', header=False, index=False)

                # delete file
                if os.path.exists('media/' + uploaded_file.name):
                    os.remove('media/' + uploaded_file.name)
            else:
                messages.error(request,'Please upload a file of CSV, H5AD, or TSV type')
        else:
            messages.error(request,'Please select a file.')
    else:
        form = CheckboxForm()
        
        
    return render(request,'index.html', context)

def calc_score_thresh(request):
    if request.method == 'POST':
        form = ScoreForm(request.POST or None)
        if form.is_valid():
            score_thresh = form.cleaned_data.get('score_thresh', None)
            print(score_thresh)
    else:
        form = ScoreForm()

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

def download_counts(request):
    file = open('media/dropkick_counts.csv', 'rb')
    response = FileResponse(file)
    
    response['Content-Disposition'] = 'attachment; filename="dropkick_counts.csv"'
    return response

def download_genes(request):
    file = open('media/dropkick_genes.csv', 'rb')
    response = FileResponse(file)
    
    response['Content-Disposition'] = 'attachment; filename="dropkick_genes.csv"'
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
    filenames = ["media/dropkick_labels.csv", "media/dropkick_counts.csv", "media/dropkick_genes.csv", "media/dropkick_filter.h5ad", "media/coef_plot.png", "media/score_plot.png"]
    
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
    filenames = ["media/dropkick_labels.csv", "media/dropkick_counts.csv", "media/dropkick_genes.csv", "media/dropkick_filter.h5ad", "media/qc_plot.png", "media/coef_plot.png", "media/score_plot.png"]
    
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
