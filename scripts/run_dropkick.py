from dropkickApp.model import MyFile
import scanpy as sc; sc.set_figure_params(color_map="viridis", frameon=False)
import dropkick as dk

<<<<<<< Updated upstream
def run():
    
    #new = Storage()
    #new.file = request.FILES['file']
    #new.save()
    
    sample = MyFile.objects.all()
    
=======
def run():    
>>>>>>> Stashed changes
    # read in counts data
    adata = sc.read("../media/3907_S1_jointcluster.h5ad")
    
    # plot QC metrics
    adata = dk.recipe_dropkick(adata, n_hvgs=None, X_final="raw_counts")
    qc_plt = dk.qc_summary(adata)
