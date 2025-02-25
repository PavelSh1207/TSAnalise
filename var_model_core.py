from arima_model_core import DataInit, Parameters, ErrorCalculate, Log, DeleteOutliers
from statsmodels.tsa.api import VAR
import pandas as pd
from typing import override
import numpy as np

#lib for plot bulding
import matplotlib.pyplot as plt

class CreatedDeleteOutliers(DeleteOutliers):

    
    @override
    def deleteOutliers(self):
        
                   
        #aparameters inicialisation
        residuals = pd.DataFrame(self.data)
        
        #init Quatilies
        Q1 = np.percentile(residuals, 25)
        Q3 = np.percentile(residuals, 75)
        
        #Count IQR
        IQR = Q3 - Q1
        
        #init lower and hieght border
        lower_border = Q1 - 10 * IQR
        hieghter_border = Q3 - 10 * IQR
        
        
        #create binary varaible 1 - outlaer, 0 - normal
        #outlier_mask = np.logical_or(residuals < lower_border , residuals > hieghter_border)
        outlier_mask = (residuals < lower_border) | (hieghter_border>residuals)
        
        #deleting outliers with mask
        self.filtred_data = np.where(outlier_mask, np.mean(residuals), residuals)
    
    @override
    def plotEnterface(self):

            self.png_filename = f'{self.column}_var_delete_otliers.png'
            self.title_plot = f'var delete otliers for column <{self.column}>'
            self.xlabe_plt = f'Time'
            self.message = f'var delete outliers plot for column <{self.column}> was created'

    @override
    def logEnterface(self):
        
        self.log = Log(
            
            message= f'var filtred outliers:\n {self.filtred_data}',
            save = self.save,
            csvname= f'var_filtred_outliers_{self.column}_log.csv'

            )


class ModelVAR:
    
    def __init__(self, filename):
        
        dataInit = DataInit(filename)
        self.data = pd.DataFrame(dataInit.returnData())
        
    def modelVAR(self):
        
        columns = self.data.columns[1:]
        diff_data = pd.DataFrame()

        for col in columns:
            
            column_parameters = Parameters(self.data, col)
            self.column_diff = column_parameters.parameters()[0]  
            
            timeseries = pd.Series(self.data[col]).copy()

            for _ in range(self.column_diff):
                
                timeseries = timeseries.diff().dropna()

            diff_data[col] = timeseries

        self.diff_data = diff_data.dropna()
        
        self.model_var = VAR(diff_data)

        if self.model_var.select_order(maxlags=20).aic != None:
            
            self.lag = self.model_var.select_order(maxlags=20).aic
            
        else:
            
            self.lag = 1

        self.model_var_fit = self.model_var.fit(self.lag)
        self.model_var_fit_summary = self.model_var_fit.summary()
        
    def logs(self):
        
        log = Log(
            
            message= f'\nVAR Model lag = {self.lag}, diferencacion = {self.column_diff}\n\n{self.model_var_fit_summary}',
            csvname= f'VAR_model.csv',
            save= True
            
            )
        
        log.logs()
    
    def plot_fitted_model(self, save = True):
        
        png_name = f'fitted_VAR_model.png'
        
        plt.figure(figsize=(12, 5))

        for col in self.model_var_fit.fittedvalues.columns:  
            plt.plot(self.model_var_fit.fittedvalues[col], label=f"{col} (Fitted)")

        plt.legend()
        plt.title("Fitted Values from VAR Model")
        plt.xlabel("Time")
        plt.ylabel("Values")
        plt.grid()
        
        if save:
            
            plt.savefig(png_name)
        
        else:    
            
            plt.show()    
        
    def plot_resid_model(self, save = True):
        
        png_name = f'resid_VAR_model.png'
        
        plt.figure(figsize=(12, 5))

        for col in self.model_var_fit.resid.columns:  
            
            plt.plot(self.model_var_fit.resid[col], label=f"{col} (Residuals)")

        plt.legend()
        plt.title("Fitted Values from VAR Model")
        plt.xlabel("Time")
        plt.ylabel("Values")
        plt.grid()
        
        if save:
            
            plt.savefig(png_name)
        
        else:    
            
            plt.show()
            
            
class CustomErrorCalculate(ErrorCalculate):  
    
    @override
    def logs(self):
        
        log = Log(
            message= f'model <{self.fit_model.model.__class__.__name__}>\nmodel parameters = {self.fit_model.k_ar}\n\nERROR RAPORT:\n\n{self.errorCalculate()}',
            save = True,
            csvname= f'{self.fit_model.model.__class__.__name__}_error_model_log.csv'
        )
        
        log.logs()
                
if __name__ == "__main__":
    
    #model init
    modelVAR = ModelVAR('mainDataSet.csv')
    
    #model run
    model_var_result = modelVAR.modelVAR()
    
    #model output
    modelVAR.logs()
    modelVAR.plot_fitted_model()
    modelVAR.plot_resid_model()
    
    #model errors reworking
    customErrorCalculate = CustomErrorCalculate(modelVAR.model_var_fit, data= modelVAR.diff_data)
    customErrorCalculate.errorCalculate()
    customErrorCalculate.logs()
    
    deleteOutliers = CreatedDeleteOutliers(data= modelVAR.model_var_fit.resid, column = modelVAR.model_var_fit.names, save= True)
    deleteOutliers.deleteOutliers()
    deleteOutliers.logsEnterface()
    deleteOutliers.logs()
    deleteOutliers.plotEnterface()
    deleteOutliers.plot()
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
        
            
        
        

