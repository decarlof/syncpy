# -*- coding: utf-8 -*-
import numpy as np
import os
import h5py
import logging

from dataexchange.xtomo.xtomo_reader import XTomoReader

def _dset_read(f_in, dset_name, slice_list):
    """
    Helper function for reading data sets that might not exist with arbitrary slices

    Parameters
    ----------
    f_in : h5py.Group
       Open file or group

    dset_name : str
       name of dataset to try to read

    slice_list : list or tuple
       slice object to use slicing the data set.  length needs to math
       the number of dimensions
    """
    # try to read the data
    try:
        out_data = f_in[dset_name][slice_list]
    # if KeyError is raised (because the data set does not exist)
    except KeyError:
        # set data to None
        out_data = None

    # return the data
    return out_data

_no_data_err = "{file} does not contain '/exchange/data'"

def xtomo_reader(file_name,
                     projections_start=None,
                     projections_end=None,
                     projections_step=None,
                     slices_start=None,
                     slices_end=None,
                     slices_step=None,
                     pixels_start=None,
                     pixels_end=None,
                     pixels_step=None,
                     white_start=None,
                     white_end=None,
                     dark_start=None,
                     dark_end=None):
        """
        Read Data Exchange HDF5 file.

        Parameters
        ----------
        file_name : str
            Input file.

        projections_start, projections_end, projections_step : scalar, optional
            Values of the start, end and step of the projections to
            be used for slicing for the whole data.

        slices_start, slices_end, slices_step : scalar, optional
            Values of the start, end and step of the slices to
            be used for slicing for the whole data.

        pixels_start, pixels_end, pixels_step : scalar, optional
            Values of the start, end and step of the pixels to
            be used for slicing for the whole data.

        white_start, white_end : scalar, optional
            Values of the start and end of the
            slicing for the whole white field shots.

        dark_start, dark_end : scalar, optional
            Values of the start and end of the
            slicing for the whole dark field shots.

        Examples
        --------
        - Import data, white-field, dark-field and projection angles
          from HDF5 file:

            >>> import tomopy
            >>>
            >>> # Load data
            >>> myfile = 'demo/data.h5'
            >>> data, white, dark, theta = tomopy.xtomo_reader(myfile)
            >>>
            >>> # Image data
            >>> import pyplot as plt
            >>> plt.figure()
            >>> plt.imshow(data[:, 0, :])
            >>> plt.show()

        - Import only 4th slice from HDF5 file:

            >>> import tomopy
            >>>
            >>> # Load data
            >>> myfile = 'demo/data.h5'
            >>> data, white, dark, theta = tomopy.xtomo_reader(myfile,  slices_start=4, slices_end=5)
            >>>
            >>> # Image data
            >>> import pyplot as plt
            >>> plt.figure()
            >>> plt.imshow(data[:, 0, :])
            >>> plt.show()
        """

        # expand the file_name
        file_name = os.path.abspath(file_name)

        # open the hdf file with context manager so it will always close
        # properly, even if there are uncaught errors.
        with h5py.File(file_name, "r") as f:
            # set up all of the slices, these should really be passed in
            # and follow the pattern
            # if a is None:
            #    a = slice(None, None, None)
            proj_slc = slice(projections_start, projections_end,
                                projections_step)
            slices_slc = slice(slices_start, slices_end, slices_step)
            pixel_slc = slice(pixels_start, pixels_end, pixels_step)
            white_slc = slice(white_start, white_end)
            dark_slc = slice(dark_start, dark_end)

            # read the data
            data = _dset_read(f, "/exchange/data",
                              [proj_slc, slices_slc, pixel_slc])
            # add a check that data is not None
            if data is None:
                raise ValueError(_no_data_err.format(file=file_name))
            # read the white-field data
            data_white = _dset_read(f, "/exchange/data_white",
                                [white_slc, slices_slc, pixel_slc])

            # read the dark-field data
            data_dark = _dset_read(f, "/exchange/data_dark",
                                [dark_slc, slices_slc, pixel_slc])

            # read the theta data
            theta = _dset_read(f, "/exchange/theta", [proj_slc, ])

        return data, data_white, data_dark, theta


class Import():
    def __init__(xtomo, data=None, data_white=None,
                 data_dark=None, theta=None, log='INFO'):

        xtomo.data = data
        xtomo.data_white = data_white
        xtomo.data_dark = data_dark
        xtomo.theta = theta

        # Set the log level.
        xtomo.logger = None
        xtomo._log_level = str(log).upper()
        xtomo._init_logging()

    # put this here for backwards compatibility
    xtomo_reader = staticmethod(xtomo_reader)

    #@staticmethod
    def series_of_images(xtomo, file_name,
                         projections_start=0,
                         projections_end=0,
                         projections_step=1,
                         slices_start=0,
                         slices_end=None,
                         slices_step=1,
                         pixels_start=0,
                         pixels_end=0,
                         pixels_step=1,
                         white_file_name=None,
                         white_start=0,
                         white_end=0,
                         white_step=1,
                         dark_file_name=None,
                         dark_start=0,
                         dark_end=0,
                         dark_step=1,
                         projections_angle_range=180,
                         projections_zeros=True,
                         projections_digits=4,
                         white_digits=None,
                         dark_digits=None,
                         white_zeros=True,
                         dark_zeros=True,
                         dtype='uint16',
                         data_type='tiff',
                         sample_name=None,
                         log='INFO'):
        """
        Read a stack of 2-D HDF4, TIFF, spe or netCDF images.

        Parameters
        ----------
        file_name : str
            Base name of the input HDF4 or TIFF files.
            For example if the projections names are /local/data/test_XXXX.hdf
            file_name is /local/data/test_.hdf

        projections_start, projections_end, projections_step : scalar, optional
            start and end index for the projection
            images to load. Use step to define a stride.

        slices_start, slices_end, slices_step : scalar, optional
            start and end pixel of the projection image to load
            along the rotation axis. Use step to define a stride.

        white_file_name, dark_file_name : str, optional
            Base name of the white and dark field input files.
            For example if the white field names
            are /local/data/test_bg_XXXX.hdf
            file_name is /local/data/test_bg_.hdf.
            If omitted white_file_name = file_name.

        white_start, white_end, white_step : scalar, optional
            start and end index for the white field
            files to load. Use step define a stride.

        dark_start, dark_end, dark_step : scalar, optional
            start and end index for the dark field
            files to load. Use step to define a stride.

        projections_digits, white_digits, dark_digits : scalar, optional
            Number of projections_digits used for file indexing.
            For example if 4: test_XXXX.hdf

        projections_zeros, white_zeros, dark_zeros : bool, optional
            If ``True`` assumes all indexing uses four
            projections_digits (0001, 0002, ..., 9999).
            If ``False`` omits projections_zeros in
            indexing (1, 2, ..., 9999)

        sample_name : str, optional
            sample name. If not defined the file name is assigmed as sample name

        hdf5_file_name : str, optional
            if set the series for images is saved as a data exchange file

        dtype : str, optional
            Corresponding Numpy data type of file.

        data_type : str, optional
            supported options are:
                - ``hdf4``: HDF4 files used on old detector at APS 2-BM
                - ``compressed_tiff``: tiff files used at elettra
                - ``tiff``: uncompressed regualar tiff files
                - ``spe``: spe data from APS 13-BM
                - ``nc``: netCDF data from 13-BM

        Returns
        -------
        Output : data, data_white, data_dark, theta
             if hdf5_file_name is set the series for images is saved as a data exchange file
       """

        # Set default prefix for white and dark.
        if white_file_name is None:
            white_file_name = file_name
        if dark_file_name is None:
            dark_file_name = file_name

        # Set default digits.
        if white_digits is None:
            white_digits = projections_digits
        if dark_digits is None:
            dark_digits = projections_digits


        # Determine file name and extension type.
        if (data_type is 'hdf4'):
            if file_name.endswith('h4') or \
                file_name.endswith('hdf'):
                data_file = file_name.split('.')[-2]
                dataExtension = file_name.split('.')[-1]
            if white_file_name.endswith('h4') or \
                white_file_name.endswith('hdf'):
                data_file_white = white_file_name.split('.')[-2]
            if dark_file_name.endswith('h4') or \
                dark_file_name.endswith('hdf'):
                data_file_dark = dark_file_name.split('.')[-2]

        elif (data_type is 'spe'):
            if file_name.endswith('SPE') or \
                file_name.endswith('spe'):
                data_file = file_name.split('.')[-2]
                dataExtension = file_name.split('.')[-1]
            if white_file_name.endswith('SPE') or \
                white_file_name.endswith('spe'):
                data_file_white = white_file_name.split('.')[-2]
            if dark_file_name.endswith('SPE') or \
                dark_file_name.endswith('spe'):
                data_file_dark = dark_file_name.split('.')[-2]

        elif (data_type is 'nc'):
            if file_name.endswith('NC') or \
                file_name.endswith('nc'):
                data_file = file_name.split('.')[-2]
                dataExtension = file_name.split('.')[-1]
            if white_file_name.endswith('NC') or \
                white_file_name.endswith('nc'):
                data_file_white = white_file_name.split('.')[-2]
            if dark_file_name.endswith('NC') or \
                dark_file_name.endswith('nc'):
                data_file_dark = dark_file_name.split('.')[-2]

        elif ((data_type is 'tiff') or (data_type is 'compressed_tiff')):
            if file_name.endswith('tif') or \
                file_name.endswith('tiff'):
                data_file = file_name.split('.')[-2]
                dataExtension = file_name.split('.')[-1]
            if white_file_name.endswith('tif') or \
                white_file_name.endswith('tiff'):
                data_file_white = white_file_name.split('.')[-2]
            if dark_file_name.endswith('tif') or \
                dark_file_name.endswith('tiff'):
                data_file_dark = dark_file_name.split('.')[-2]


        projections_file_index = ["" for x in range(projections_digits)]
        for m in range(projections_digits):
            if projections_zeros is True:
                projections_file_index[m] = '0' * (projections_digits-m-1)
            elif projections_zeros is False:
                projections_file_index[m] = ''

        white_file_index = ["" for x in range(white_digits)]
        for m in range(white_digits):
            if white_zeros is True:
                white_file_index[m] = '0' * (white_digits-m-1)
            elif white_zeros is False:
                white_file_index[m] = ''

        dark_file_index = ["" for x in range(dark_digits)]
        for m in range(dark_digits):
            if dark_zeros is True:
                dark_file_index[m] = '0' * (dark_digits-m-1)
            elif dark_zeros is False:
                dark_file_index[m] = ''

        xtomo.logger.debug('')


        # Data ------------------------------------------------

        # Start reading projections one-by-one.
        ind = range(projections_start, projections_end, projections_step)
        for m in range(len(ind)):
            for n in range(projections_digits):
                if ind[m] < np.power(10, n+1):
                    _file_name = data_file + projections_file_index[n] + str(ind[m]) + '.' + dataExtension
                    xtomo.logger.info("Generating projection file names: [%s]", _file_name)
                    break

            if os.path.isfile(_file_name):
                xtomo.logger.info("Reading projection file: [%s]", os.path.realpath(_file_name))
                xtomo.logger.info("data type: [%s]", data_type)

                f = XTomoReader(_file_name)
                if (data_type is 'hdf4'):
                    tmpdata = f.hdf4(x_start=slices_start,
                                     x_end=slices_end,
                                     x_step=slices_step,
                                     array_name='data')

                elif (data_type is 'compressed_tiff'):
                    tmpdata = f.tiffc(x_start=slices_start,
                                      x_end=slices_end,
                                      x_step=slices_step,
                                      dtype=dtype)

                elif (data_type is 'spe'):
                    tmpdata = f.spe()

                elif (data_type is 'nc'):
                    tmpdata = f.netcdf()

                elif (data_type is 'tiff'):
                    tmpdata = f.tiff(x_start=slices_start,
                                     x_end=slices_end,
                                     x_step=slices_step,
                                     dtype='uint16')

                if ((data_type is 'tiff') or
                    (data_type is 'compressed_tiff') or
                    (data_type is 'hdf4')):
                    if m == 0: # Get resolution once.
                        input_data = np.empty((len(ind),
                                             tmpdata.shape[0],
                                             tmpdata.shape[1]),
                                             dtype=dtype)
                    input_data[m, :, :] = tmpdata

                if ((data_type is 'spe') or
                    (data_type is 'nc')):
                    if m == 0: # Get resolution once.
                        input_data = np.vstack([tmpdata])
                    else:
                        input_data = np.concatenate((input_data, tmpdata), axis=0)

        # Update data.
        if len(ind) > 0:
            xtomo.data = input_data

        # White ------------------------------------------------

        # Reading white fields.
        ind = range(white_start, white_end, white_step)
        for m in range(len(ind)):
            for n in range(white_digits):
                if ind[m] < np.power(10, n+1):
                    _file_name = data_file_white + white_file_index[n] + str(ind[m]) + '.' + dataExtension
                    xtomo.logger.info("Generating white file names: [%s]", _file_name)
                    break

            if os.path.isfile(_file_name):
                xtomo.logger.info("Reading white file: [%s]", os.path.realpath(_file_name))
                xtomo.logger.info("data type: [%s]", data_type)

                f = XTomoReader(_file_name)
                if (data_type is 'hdf4'):
                    tmpdata = f.hdf4(x_start=slices_start,
                                     x_end=slices_end,
                                     x_step=slices_step,
                                     array_name='data')

                elif (data_type is 'compressed_tiff'):
                    tmpdata = f.tiffc(x_start=slices_start,
                                      x_end=slices_end,
                                      x_step=slices_step,
                                      dtype=dtype)

                elif (data_type is 'spe'):
                    tmpdata = f.spe()

                elif (data_type is 'nc'):
                    tmpdata = f.netcdf()

                elif (data_type is 'tiff'):
                    tmpdata = f.tiff(x_start = slices_start,
                                     x_end = slices_end,
                                     x_step = slices_step,
                                     dtype = dtype)

                if ((data_type is 'tiff') or
                    (data_type is 'compressed_tiff') or
                    (data_type is 'hdf4')):
                    if m == 0: # Get resolution once.
                        input_data = np.empty((len(ind),
                                             tmpdata.shape[0],
                                             tmpdata.shape[1]),
                                             dtype=dtype)
                    input_data[m, :, :] = tmpdata

                if ((data_type is 'spe') or
                    (data_type is 'nc')):
                    if m == 0: # Get resolution once.
                        input_data = np.vstack([tmpdata])
                    else:
                        input_data = np.concatenate((input_data, tmpdata), axis=0)

        # Update white data.
        if len(ind) > 0:
            xtomo.data_white = input_data
        else:
            # Fabricate one white field
            nz, ny, nx = np.shape(xtomo.data)
            xtomo.data_white = np.ones((1, ny, nx))

        # Dark ------------------------------------------------

        # Reading dark fields.
        ind = range(dark_start, dark_end, dark_step)
        for m in range(len(ind)):
            for n in range(dark_digits):
                if ind[m] < np.power(10, n + 1):
                    _file_name = data_file_dark + dark_file_index[n] + str(ind[m]) + '.' + dataExtension
                    xtomo.logger.info("Generating dark file names: [%s]", _file_name)
                    break

            if os.path.isfile(_file_name):
                xtomo.logger.info("Reading dark file: [%s]", os.path.realpath(_file_name))
                xtomo.logger.info("data type: [%s]", data_type)

                f = XTomoReader(_file_name)
                if (data_type is 'hdf4'):
                    tmpdata = f.hdf4(x_start=slices_start,
                                     x_end=slices_end,
                                     x_step=slices_step,
                                     array_name='data')

                elif (data_type is 'compressed_tiff'):
                    tmpdata = f.tiffc(x_start=slices_start,
                                      x_end=slices_end,
                                      x_step=slices_step,
                                      dtype=dtype)

                elif (data_type is 'spe'):
                    tmpdata = f.spe()

                elif (data_type is 'nc'):
                    tmpdata = f.netcdf()

                elif (data_type is 'tiff'):
                    tmpdata = f.tiff(x_start=slices_start,
                                     x_end=slices_end,
                                     x_step=slices_step,
                                     dtype=dtype)

                if ((data_type is 'tiff') or
                    (data_type is 'compressed_tiff') or
                    (data_type is 'hdf4')):
                    if m == 0: # Get resolution once.
                        input_data = np.empty((len(ind),
                                             tmpdata.shape[0],
                                             tmpdata.shape[1]),
                                             dtype=dtype)
                    input_data[m, :, :] = tmpdata

                if ((data_type is 'spe') or
                    (data_type is 'nc')):
                    if m == 0: # Get resolution once.
                        input_data = np.vstack([tmpdata])
                    else:
                        input_data = np.concatenate((input_data, tmpdata), axis=0)

        # Update dark data.
        if len(ind) > 0:
            xtomo.data_dark = input_data
        else:
            # Fabricate one dark field
            nz, ny, nx = np.shape(xtomo.data)
            xtomo.data_dark = np.zeros((1, ny, nx))

        # Theta ------------------------------------------------

        if ((data_type is 'tiff') or
           (data_type is 'compressed_tiff') or
           (data_type is 'hdf4')):
            # Fabricate theta values.
            z = np.arange(projections_end - projections_start);

            # Fabricate theta values
            xtomo.theta = (z * float(projections_angle_range) / (len(z) - 1))

        # this "if" will be removed once I clean up the series of stack loading for netCDF and SPE
        if ((data_type is 'tiff') or (data_type is 'compressed_tiff') or (data_type is 'hdf4')):
            return xtomo.data, xtomo.data_white, xtomo.data_dark,  xtomo.theta
        else:
            return xtomo.data, xtomo.data_white, xtomo.data_dark

    def nexus(xtomo, file_name,
              hdf5_file_name,
              projections_start=0,
              projections_end=None,
              projections_step=1,
              slices_start=0,
              slices_end=None,
              slices_step=1,
              pixels_start=0,
              pixels_end=None,
              pixels_step=1,
              white_start=0,
              white_end=None,
              dark_start=0,
              dark_end=None,
              array_name='entry/instrument/detector/data',
              sample_name=None,
              dtype='float32'):
        """
        Read Data Exchange HDF5 file.

        Parameters
        ----------
        file_name : str
            Input file.

        projections_start, projections_end, projections_step : scalar, optional
            Values of the start, end and step of the projections to
            be used for slicing for the whole ndarray.

        slices_start, slices_end, slices_step : scalar, optional
            Values of the start, end and step of the slices to
            be used for slicing for the whole ndarray.

        pixels_start, pixels_end, pixels_step : scalar, optional
            Values of the start, end and step of the pixels to
            be used for slicing for the whole ndarray.

        white_start, white_end : scalar, optional
            Values of the start, end and step of the
            slicing for the whole white field shots.

        dark_start, dark_end : scalar, optional
            Values of the start, end and step of the
            slicing for the whole dark field shots.

        dtype : str, optional
            Desired output data type.
        """

        f = XTomoReader()
        # Read data from exchange group.
        xtomo.data = f.hdf5(file_name,
                            array_name=array_name,
                            x_start=projections_start,
                            x_end=projections_end,
                            x_step=projections_step,
                            y_start=slices_start,
                            y_end=slices_end,
                            y_step=slices_step,
                            z_start=pixels_start,
                            z_end=pixels_end,
                            z_step=pixels_step).astype(dtype)

        # Read white field data from exchange group.
        xtomo.data_white = f.hdf5(file_name,
                            array_name=array_name,
                            x_start=white_start,
                            x_end=white_end,
                            y_start=slices_start,
                            y_end=slices_end,
                            y_step=slices_step,
                            z_start=pixels_start,
                            z_end=pixels_end,
                            z_step=pixels_step).astype(dtype)

        # Read dark field data from exchange group.
        xtomo.data_dark = f.hdf5(file_name,
                            array_name=array_name,
                            x_start=dark_start,
                            x_end=dark_end,
                            y_start=slices_start,
                            y_end=slices_end,
                            y_step=slices_step,
                            z_start=pixels_start,
                            z_end=pixels_end,
                            z_step=pixels_step).astype(dtype)


    def _init_logging(xtomo):
        """
        Setup and start command line logging.
        """
        # Top-level log setup.
        xtomo.logger = logging.getLogger("data exchange")
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
