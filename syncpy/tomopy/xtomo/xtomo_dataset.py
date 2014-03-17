# -*- coding: utf-8 -*-
import numpy as np
import logging


class XTomoDataset:
    def __init__(xtomo, data, data_white=None, 
                 data_dark=None, theta=None, 
                 log='INFO', color_log=True):
        """
        Constructor for the X-ray absorption 
        tomography data object.
        
        Attributes
        ----------
        xtomo : tomopy data object
            This is the core X-ray absorption tomography 
            data object that all low-level 
            attributes and methods are bound to.
            
        data : ndarray
            3-D X-ray absorption tomography raw data. 
            Size of the dimensions should be: 
            [projections, slices, pixels].
    
        data_white, data_dark : ndarray,  optional
            3-D white-field/dark_field data. Multiple 
            projections are stacked together to obtain 
            a 3-D matrix. 2nd and 3rd dimensions should 
            be the same as data: [shots, slices, pixels].
            
        theta : ndarray, optional
            Data acquisition angles corresponding
            to each projection.
            
        log : str, optional
            Determines the logging level.
            Available arguments: {'DEBUG' 'INFO' 'WARN' 'WARNING' 'ERROR'}.
            
        color_log : bool, optional
            If ``True`` command line logging is colored. 
            You may want to set it ``False`` if you will use 
            file logging only.
        """      
        # Logging init.
        if color_log: # enable colored logging
            from tomopy.tools import colorer

        # Set the log level.
        xtomo.logger = None
        xtomo._log_level = str(log).upper()
        xtomo._init_logging()
 
        # Set the numpy Data-Exchange structure.
        xtomo.data = np.array(data, dtype='float32', copy=False)
        xtomo.data_white = np.array(data_white, dtype='float32', copy=False)
        xtomo.data_dark = np.array(data_dark, dtype='float32', copy=False)
        xtomo.theta = np.array(np.squeeze(theta), dtype='float32', copy=False)
        
        # Dimensions:
        num_projs = xtomo.data.shape[0]
        num_slices = xtomo.data.shape[1]
        num_pixels = xtomo.data.shape[2]
        
        # Assign data_white
        if data_white is None:
            xtomo.data_white = np.zeros((1, num_slices, num_pixels))
            xtomo.data_white += np.mean(xtomo.data[:])
            xtomo.logger.warning("auto-normalization [ok]")
            
        # Assign data_dark
        if data_dark is None:
            xtomo.data_dark = np.zeros((1, num_slices, num_pixels))
            xtomo.logger.warning("dark-field assumed as zeros [ok]")
                
        # Assign theta
        if theta is None:
            xtomo.theta = np.linspace(0, num_projs, num_projs)*180/(num_projs+1)
            xtomo.logger.warning("assign 180-degree rotation [ok]")

    def _init_logging(xtomo):
        """
        Setup and start command line logging.
        """
        # Top-level log setup.
        xtomo.logger = logging.getLogger("tomopy") 
        if xtomo._log_level == 'DEBUG':
            xtomo.logger.setLevel(logging.DEBUG)
        elif xtomo._log_level == 'INFO':
            xtomo.logger.setLevel(logging.INFO) 
        elif xtomo._log_level == 'WARN':
            xtomo.logger.setLevel(logging.WARN)
        elif xtomo._log_level == 'WARNING':
            xtomo.logger.setLevel(logging.WARNING)
        elif xtomo._log_level == 'ERROR':
            xtomo.logger.setLevel(logging.ERROR)
        
        # Terminal stream log.
        ch = logging.StreamHandler()
        if xtomo._log_level == 'DEBUG':
            ch.setLevel(logging.DEBUG)
        elif xtomo._log_level == 'INFO':
            ch.setLevel(logging.INFO) 
        elif xtomo._log_level == 'WARN':
            ch.setLevel(logging.WARN)
        elif xtomo._log_level == 'WARNING':
            ch.setLevel(logging.WARNING)
        elif xtomo._log_level == 'ERROR':
            ch.setLevel(logging.ERROR)
        
        # Show date and time.
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
            
        # Update logger.
        if not len(xtomo.logger.handlers): # For fist time create handlers.
            xtomo.logger.addHandler(ch)