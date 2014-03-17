# -*- coding: utf-8 -*-
"""
This module containes a set of thin wrappers to 
hook the methods in preprocess package to X-ray 
absorption tomography data object.
"""

import numpy as np

# Import main TomoPy object.
from tomopy.xtomo import XTomoDataset

# Import available functons in the package.
from tomopy.algorithms.preprocess.apply_padding import _apply_padding
from tomopy.algorithms.preprocess.correct_drift import _correct_drift
from tomopy.algorithms.preprocess.downsample import _downsample2d, _downsample3d
from tomopy.algorithms.preprocess.median_filter import _median_filter
from tomopy.algorithms.preprocess.normalize import _normalize
from tomopy.algorithms.preprocess.phase_retrieval import _phase_retrieval, _paganin_filter
from tomopy.algorithms.preprocess.stripe_removal import _stripe_removal
from tomopy.algorithms.preprocess.zinger_removal import _zinger_removal

# Import multiprocessing module.
from tomopy.tools.multiprocess import distribute_jobs


# --------------------------------------------------------------------

def apply_padding(xtomo, num_pad=None,
                  num_cores=None, chunk_size=None,
                  overwrite=True):

    # Set default parameters.
    num_pixels = xtomo.data.shape[2]
    if num_pad is None:
        num_pad = np.ceil(num_pixels * np.sqrt(2))
                         
    # Check input.
    if not isinstance(num_pad, np.int32):
        num_pad = np.array(num_pad, dtype='int32')

    data = _apply_padding(xtomo.data, num_pad)
    
    # Update log.
    xtomo.logger.debug("apply_padding: num_pad: " + str(num_pad))
    xtomo.logger.info("apply_padding [ok]")

    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data

# --------------------------------------------------------------------

def correct_drift(xtomo, air_pixels=20, 
                  num_cores=None, chunk_size=None,
                  overwrite=True):
    
    # Check input.
    if not isinstance(air_pixels, np.int32):
        air_pixels = np.array(air_pixels, dtype='int32')
    
    data = _correct_drift(xtomo.data, air_pixels)
   
    # Update log.
    xtomo.logger.debug("correct_drift: air_pixels: " + str(air_pixels))
    xtomo.logger.info("correct_drift [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data

# --------------------------------------------------------------------

def downsample2d(xtomo, level=1,
                 num_cores=None, chunk_size=None,
                 overwrite=True):
    
    # Check input.
    if not isinstance(level, np.int32):
        level = np.array(level, dtype='int32')

    data = _downsample2d(xtomo.data, level)
    
    # Update log.
    xtomo.logger.debug("downsample2d: level: " + str(level))
    xtomo.logger.info("downsample2d [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data
	
# --------------------------------------------------------------------

def downsample3d(xtomo, level=1,
                 num_cores=None, chunk_size=None,
                 overwrite=True):

    # Check input.
    if not isinstance(level, np.int32):
        level = np.array(level, dtype='int32')

    data = _downsample3d(xtomo.data, level)
    
    # Update log.
    xtomo.logger.debug("downsample3d: level: " + str(level))
    xtomo.logger.info("downsample3d [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data	

# --------------------------------------------------------------------

def median_filter(xtomo, size=5, 
                  num_cores=None, chunk_size=None,
                  overwrite=True):
        
    # Distribute jobs.
    _func = _median_filter
    _args = (size)
    _axis = 1 # Slice axis
    data = distribute_jobs(xtomo.data, _func, _args, _axis, 
                           num_cores, chunk_size)
   
    # Update log.
    xtomo.logger.debug("median_filter: size: " + str(size))
    xtomo.logger.info("median_filter [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data	

# --------------------------------------------------------------------

def normalize(xtomo, cutoff=None, 
              num_cores=None, chunk_size=None,
              overwrite=True):

    # Calculate average white and dark fields for normalization.
    avg_white = np.mean(xtomo.data_white, axis=0)
    avg_dark = np.mean(xtomo.data_dark, axis=0)
    
    # Distribute jobs.
    _func = _normalize
    _args = (avg_white, avg_dark, cutoff)
    _axis = 0 # Projection axis
    data = distribute_jobs(xtomo.data, _func, _args, _axis, 
			   num_cores, chunk_size)

    # Update log.
    xtomo.logger.debug("normalize: cutoff: " + str(cutoff))
    xtomo.logger.info("normalize [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data	

# --------------------------------------------------------------------

def phase_retrieval(xtomo, pixel_size=None, dist=None, 
                    energy=None, alpha=1e-5, padding=True,
                    num_cores=None, chunk_size=None,
                    overwrite=True):        
        
    # Compute the filter.
    H, x_shift, y_shift, tmp_proj = _paganin_filter(xtomo.data,
                                    pixel_size, dist, energy, alpha, padding)                 
                     
    # Distribute jobs.
    _func = _phase_retrieval
    _args = (H, x_shift, y_shift, tmp_proj, padding)
    _axis = 0 # Projection axis
    data = distribute_jobs(xtomo.data, _func, _args, _axis, 
                           num_cores, chunk_size)

    # Update log.
    xtomo.logger.debug("phase_retrieval: pixel_size: " + str(pixel_size))
    xtomo.logger.debug("phase_retrieval: dist: " + str(dist))
    xtomo.logger.debug("phase_retrieval: energy: " + str(energy))
    xtomo.logger.debug("phase_retrieval: alpha: " + str(alpha))
    xtomo.logger.debug("phase_retrieval: padding: " + str(padding))
    xtomo.logger.info("phase_retrieval [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data	

# --------------------------------------------------------------------

def stripe_removal(xtomo, level=None, wname='db5', sigma=4,
                   num_cores=None, chunk_size=None,
                   overwrite=True):

    # Find the higest level possible.
    if level is None:
        size = np.max(xtomo.data.shape)
        level = int(np.ceil(np.log2(size)))
        
    # Distribute jobs.
    _func = _stripe_removal
    _args = (level, wname, sigma)
    _axis = 1 # Slice axis
    data = distribute_jobs(xtomo.data, _func, _args, _axis,
                           num_cores, chunk_size)
			
    # Update log.
    xtomo.logger.debug("stripe_removal: level: " + str(level))
    xtomo.logger.debug("stripe_removal: wname: " + str(wname))
    xtomo.logger.debug("stripe_removal: sigma: " + str(sigma))
    xtomo.logger.info("stripe_removal [ok]")
    
    # Update returned values.
    if overwrite: xtomo.data = data
    else: return data	

# --------------------------------------------------------------------

def zinger_removal(xtomo, zinger_level=1000, median_width=3,
                   num_cores=None, chunk_size=None,
                   overwrite=True):

    # Distribute jobs.
    _func = _zinger_removal
    _args = (zinger_level, median_width)
    _axis = 0 # Projection axis
    data = distribute_jobs(xtomo.data, _func, _args, _axis,
                           num_cores, chunk_size)

    data_white = distribute_jobs(xtomo.data_white, _func, _args, _axis,
                           num_cores, chunk_size)
    
    data_dark = distribute_jobs(xtomo.data_dark, _func, _args, _axis,
                           num_cores, chunk_size)

    # Update log.
    xtomo.logger.debug("zinger_removal: zinger_level: " + str(zinger_level))
    xtomo.logger.debug("zinger_removal: median_width: " + str(median_width))
    xtomo.logger.info("zinger_removal [ok]")

    # Update returned values.
    if overwrite:
        xtomo.data = data
        xtomo.data_white = data_white
        xtomo.data_dark = data_dark
    else: return data, data_white, data_dark

# --------------------------------------------------------------------
    
# Hook all these methods to TomoPy.
setattr(XTomoDataset, 'apply_padding', apply_padding)
setattr(XTomoDataset, 'correct_drift', correct_drift)
setattr(XTomoDataset, 'downsample2d', downsample2d)
setattr(XTomoDataset, 'downsample3d', downsample3d)
setattr(XTomoDataset, 'median_filter', median_filter)
setattr(XTomoDataset, 'normalize', normalize)
setattr(XTomoDataset, 'phase_retrieval', phase_retrieval)
setattr(XTomoDataset, 'stripe_removal', stripe_removal)
setattr(XTomoDataset, 'zinger_removal', zinger_removal)

# Use original function docstrings for the wrappers.
apply_padding.__doc__ = _apply_padding.__doc__
correct_drift.__doc__ = _correct_drift.__doc__
downsample2d.__doc__ = _downsample2d.__doc__
downsample3d.__doc__ = _downsample3d.__doc__
median_filter.__doc__ = _median_filter.__doc__
normalize.__doc__ = _normalize.__doc__
phase_retrieval.__doc__ = _phase_retrieval.__doc__
stripe_removal.__doc__ = _stripe_removal.__doc__
zinger_removal.__doc__ = _zinger_removal.__doc__
