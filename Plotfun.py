# -*- coding: utf-8 -*-
"""
Created on Mon Apr 09 17:56:43 2018

@author: JunbinZhang
"""
import matplotlib.pyplot as plt
import os.path
import numpy as np
class Plotfun:
    def path(self,name):
        fileDir = os.path.dirname(os.path.dirname(__file__)) #get the directory parallelly
        directory = os.path.join(fileDir,'Plots')
        if not os.path.exists(directory):
            os.makedirs(directory)      #create directory   
        else:
            pass
        filepath = os.path.join(directory,name + '.pdf')
        if os.path.exists(filepath):
            print("The name of the plot is already exist!")
            filepath = os.path.join(directory,name + '_1' + '.pdf') 
        else:
            pass
        return filepath        
    
    def PlotADC(self,name,ADCdata,saveflag=None):
        filepath = self.path(name) 
        fig = plt.figure(figsize=(10.0,8.0)) #set the size of figure
        plt.xlabel('chn 0 - 15')
        plt.ylabel('ADC counts')
        plt.title(name)
        plt.plot(ADCdata,'ko')
        x=np.arange(len(ADCdata))
        plt.xticks(x)
        if(saveflag == None):
            plt.show()         
        else:
            fig.savefig(filepath)
        plt.close()
        
    def PlotChn(self,name,CHNdata,saveflag=None):
        filepath = self.path(name) 
        fig = plt.figure(figsize=(10.0,8.0)) #set the size of figure
        plt.xlabel('samples')
        plt.ylabel('ADC counts')
        plt.title(name)
        plt.plot(CHNdata,'ko')
        if(saveflag == None):
            plt.show()         
        else:
            fig.savefig(filepath)
        plt.close()        
    #def __init__(self,saveinfo):
        
