# -*- coding: utf-8 -*-
"""
TomoPy is a Python toolbox to perform tomographic 
data processing and image reconstruction tasks at the 
Advanced Photon Source. It uses the HDF5 file format 
as the standard means of data exchange.
"""

try:
    import pkg_resources  # part of setuptools
    __version__ = pkg_resources.require("tomopy")[0].version
except:
    pass

