# -*- coding: utf-8 -*-

class TomoDataset:
    def __init__(self):
        pass
    
    def read_xctdata(self, data, white, dark, theta):
        self.data = data
        self.white = white
        self.dark = dark
        self.theta = theta
        
    def read_xfmdata(self):
        pass

    def _check_xctdata(self):
        pass

    def _check_xfmdata(self):
        pass