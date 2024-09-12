#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 17:26:46 2024

@author: cyberdim
"""




"""

THIS CODE AUTOMATES THE COMPILATION OF MULTIPLE LATEX FILES 


MODULE NEEDED: conda-forge / packages / latexmk 4.76
    
    https://anaconda.org/conda-forge/latexmk
"""




import os
import subprocess

def compile_tex_files(folder_path):
    # Get a list of all .tex files in the folder
    tex_files = [f for f in os.listdir(folder_path) if f.endswith('.tex')]
    
    for tex_file in tex_files:
        # Construct the full path to the .tex file
        full_tex_file = os.path.join(folder_path, tex_file)
        
        # Call latexmk to compile the .tex file
        subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', full_tex_file], cwd=folder_path)

# Specify the path to the folder containing the .tex files
folder_path = '/Users/cyberdim/Library/CloudStorage/Dropbox/WESTERN_ECONOMICS/JMP/Spanish_data/Stata_files/pdf/Prod_FN_Gross_Output/'

#folder_path = '/Volumes/EHDD1/Dropbox/WESTERN_ECONOMICS/JMP/Spanish_data/Stata_files/pdf/Prod_FN_Gross_Output/'

# Compile all .tex files in the folder
compile_tex_files(folder_path)



# Specify the path to the folder containing the .tex files
folder_path = '/Users/cyberdim/Library/CloudStorage/Dropbox/WESTERN_ECONOMICS/JMP/Spanish_data/Stata_files/pdf/Prod_FN_Gross_Output_YFE/'
#folder_path = '/Volumes/EHDD1/Dropbox/WESTERN_ECONOMICS/JMP/Spanish_data/Stata_files/pdf/Prod_FN_Gross_Output_YFE/'
# Compile all .tex files in the folder
compile_tex_files(folder_path)
