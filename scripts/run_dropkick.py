from dropkickApp.model import MyFile
import scanpy as sc; sc.set_figure_params(color_map="viridis", frameon=False)
import dropkick as dk

def run():
    
    #new = Storage()
    #new.file = request.FILES['file']
    #new.save()
    
    sample = MyFile.objects.all()
    
    # read in counts data
    adata = sc.read(sample)
    
    # plot QC metrics
    adata = dk.recipe_dropkick(adata, n_hvgs=None, X_final="raw_counts")
    qc_plt = dk.qc_summary(adata)