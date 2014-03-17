# -*- coding: utf-8 -*-
"""
This module containes a set of thin wrappers for the other
modules in recon package to link them to TomoPy session.
Each wrapper first checks the arguments and then calls the method.
The linking is mostly realized through the multiprocessing module.
"""
import numpy as np

# Import main TomoPy object.
from tomopy.dataio.reader import Session

# Import available reconstruction functons in the package.
from mlem_test import _mlem_test

    
def mlem_test(tomo, iters=None, num_grid=None, init_matrix=None, overwrite=True):
    
    # Make checks first. 
    if not tomo.FLAG_DATA:
        tomo.logger.warning("mlem (data missing) [bypassed]")
        return
   
    if not tomo.FLAG_THETA:
        tomo.logger.warning("mlem (angles missing) [bypassed]")
        return
        
    if not hasattr(tomo, 'center'):
        tomo.logger.warning("mlem (center missing) [bypassed]")
        return
        

    # This works with radians.
    if np.max(tomo.theta) > 90: # then theta is obviously in radians.
        tomo.theta *= np.pi/180

    # Pad data first.
    data = tomo.apply_padding(overwrite=False)
    data = np.abs(-np.log(data));

    # Adjust center according to padding.
    center = tomo.center + (data.shape[2]-tomo.data.shape[2])/2.

        
    # Set default parameters.
    if iters is None:
        iters = 1
        tomo.logger.debug("mlem: iters set to " + str(iters) + " [ok]")

    if num_grid is None or num_grid > tomo.data.shape[2]:
        num_grid = np.floor(data.shape[2] / np.sqrt(2))
        tomo.logger.debug("mlem: num_grid set to " + str(num_grid) + " [ok]")
        
    if init_matrix is None:
        init_matrix = np.ones((data.shape[1], num_grid, num_grid), dtype='float32')
        tomo.logger.debug("mlem: init_matrix set to ones [ok]")
    

    # Check again.
    if not isinstance(data, np.float32):
        data = np.array(data, dtype=np.float32, copy=False)

    if not isinstance(tomo.theta, np.float32):
        theta = np.array(tomo.theta, dtype=np.float32, copy=False)

    if not isinstance(center, np.float32):
        center = np.array(center, dtype=np.float32, copy=False)
        
    if not isinstance(iters, np.int32):
        iters = np.array(iters, dtype=np.int32, copy=False)

    if not isinstance(num_grid, np.int32):
        num_grid = np.array(num_grid, dtype=np.int32, copy=False)
        
    if not isinstance(init_matrix, np.float32):
        init_matrix = np.array(init_matrix, dtype=np.float32, copy=False)

    #print data.shape, data.shape[2], tomo.data.shape[2]
    #print theta.dtype
    #print tomo.center, center.dtype
    #print center, center.dtype
    #print iters, iters.dtype
    #print num_grid, num_grid.dtype
    #print init_matrix.shape, init_matrix.dtype

    # Initialize and perform reconstruction.
    data_recon, update = _mlem_test(data, theta, center, num_grid, iters, init_matrix)
    #data_recon = 0
    
    # Update provenance and log.
    tomo.provenance['mlem'] = {'iters':iters}
    tomo.FLAG_DATA_RECON = True
    tomo.logger.info("mlem reconstruction [ok]")
    
    # Update returned values.
    if overwrite:
	tomo.data_recon = data_recon
    else:
	return data_recon
	    


# --------------------------------------------------------------------

# Hook all these methods to TomoPy.
setattr(Session, 'mlem_test', mlem_test)

# Use original function docstrings for the wrappers.
mlem_test.__doc__ = _mlem_test.__doc__