import syncpy

# Data Exchange reader.
file_name = '/local/Data/phase/A01_.h5'
f = syncpy.dataexchange.Import()
f.aps_hdf5(file_name,  slices_start=1000, slices_end=1001)


# Tomopy processing.
d = syncpy.tomopy.xtomodataset(f.data, f.data_white, f.data_dark, log='DEBUG')
d.normalize()
d.median_filter()
d.center = 650
d.mlem()