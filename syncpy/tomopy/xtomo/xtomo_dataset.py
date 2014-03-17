# -*- coding: utf-8 -*-
import numpy as np
import logging


class XTomoDataset:
    def __init__(tomo, log='INFO', color_log=True):
        """
        Constructor for the data object.
        
        Attributes
        ----------
        tomo : tomopy data object
            This is the core object that all low-level 
            attributes and methods are bound to.
            
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
        tomo.logger = None
        tomo._log_level = str(log).upper()
        tomo._init_logging()
    

    def importdata(tomo, data, data_white=None, 
                   data_dark=None, theta=None):
        """
        Import X-ray absorption tomography data.
        
        Parameters
        ----------
        tomo :  tomopy data object
            X-ray absorption tomography data object.
            
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
        """
        # Set the numpy Data-Exchange structure.
        tomo.data = np.array(data, dtype='float32', copy=False)
        tomo.data_white = np.array(data_white, dtype='float32', copy=False)
        tomo.data_dark = np.array(data_dark, dtype='float32', copy=False)
        tomo.theta = np.array(np.squeeze(theta), dtype='float32', copy=False)
        
        # Dimensions:
        num_projs = tomo.data.shape[0]
        num_slices = tomo.data.shape[1]
        num_pixels = tomo.data.shape[2]
        
        # Assign data_white
        if data_white is None:
            tomo.data_white = np.zeros((1, num_slices, num_pixels))
            tomo.data_white += np.mean(tomo.data[:])
            tomo.logger.warning("auto-normalization [ok]")
            
        # Assign data_dark
        if data_dark is None:
            tomo.data_dark = np.zeros((1, num_slices, num_pixels))
            tomo.logger.warning("dark-field assumed as zeros [ok]")
                
        # Assign theta
        if theta is None:
            tomo.theta = np.linspace(0, num_projs, num_projs)*180/(num_projs+1)
            tomo.logger.warning("assign 180-degree rotation [ok]")
            

    def _init_logging(tomo):
        """
        Setup and start command line logging.
        """
        # Top-level log setup.
        tomo.logger = logging.getLogger("tomopy") 
        if tomo._log_level == 'DEBUG':
            tomo.logger.setLevel(logging.DEBUG)
        elif tomo._log_level == 'INFO':
            tomo.logger.setLevel(logging.INFO) 
        elif tomo._log_level == 'WARN':
            tomo.logger.setLevel(logging.WARN)
        elif tomo._log_level == 'WARNING':
            tomo.logger.setLevel(logging.WARNING)
        elif tomo._log_level == 'ERROR':
            tomo.logger.setLevel(logging.ERROR)
        
        # Terminal stream log.
        ch = logging.StreamHandler()
        if tomo._log_level == 'DEBUG':
            ch.setLevel(logging.DEBUG)
        elif tomo._log_level == 'INFO':
            ch.setLevel(logging.INFO) 
        elif tomo._log_level == 'WARN':
            ch.setLevel(logging.WARN)
        elif tomo._log_level == 'WARNING':
            ch.setLevel(logging.WARNING)
        elif tomo._log_level == 'ERROR':
            ch.setLevel(logging.ERROR)
        
        # Show date and time.
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
            
        # Update logger.
        if not len(tomo.logger.handlers): # For fist time create handlers.
            tomo.logger.addHandler(ch)