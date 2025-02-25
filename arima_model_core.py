#lLIB INITIALISATION    

#lib for works with data
import numpy as np
import pandas as pd
import os

#inicialisation statmodels parts for works with sattistic models
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

#lib for plot bulding
import matplotlib.pyplot as plt

#CORE CODE

class Log:
    def __init__(self,message = None, save = False, csvname = f'log.csv'):
        
        self.message =  message
        self.save = save
        self.csvname = csvname
        
    def logs(self):
        
        if self.save:
            
            with open(self.csvname, mode ="w", newline="") as file:
                
                file.write(self.message)
            
            message_log = f'\nlog was written to {self.csvname}\n'
            
            print(message_log)
            
        print(self.message)
        
class DeleteOutliers:
    
    def __init__(self, data, save, column):
        
        self.data = data
        self.save = save
        self.column = column
        
    def deleteOutliers(self):
            
        #aparameters inicialisation
        residuals = pd.array(self.data)
        
        #init Quatilies
        Q1 = np.percentile(residuals, 25)
        Q3 = np.percentile(residuals, 75)
        
        #Count IQR
        IQR = Q3 - Q1
        
        #init lower and hieght border
        lower_border = Q1 - 0.5 * IQR
        hieghter_border = Q3 - 0.5 * IQR
        
        #create binary varaible 1 - outlaer, 0 - normal
        outlier_mask = np.logical_or(residuals < lower_border , residuals > hieghter_border)
        
        #deleting outliers with mask
        self.filtred_data = residuals[~outlier_mask]
           
    def plotEnterface(self):
            
            self.png_filename = f'{self.column}_arima_delete_otliers.png'
            self.title_plot = f'arima delete otliers for column <{self.column}>'
            self.xlabe_plt = f'Time'
            self.message = f'arima delete outliers plot for column <{self.column}> was created'
            
    def plot(self): 

            self.argument_plot = self.filtred_data

            plt.figure(figsize=(10, 5))
            plt.plot(self.argument_plot)
            plt.title(self.title_plot)
            plt.xlabel(self.xlabe_plt)
            plt.ylabel(self.column)
            
            if self.save:
                
                plt.savefig(self.png_filename)
                
            else:
                
                plt.show()
                
            plt.close()
            
            print(self.message)
            
    def logsEnterface(self):
            
            self.log = Log(
                message= f'arima filtred outliers:\n {self.filtred_data}',
                save = self.save,
                csvname= f'arima_filtred_outliers_{self.column}_log.csv'
            )

    def logs(self):  

        self.log.logs()  
                
class DataInit:
    
    project_path = os.getcwd() + "//.venv//"
    
    def __init__(self, filename):
        
        self.filename = filename
        self.path = self.project_path + self.filename
    
    def returnData(self):
        
        try:
            
            return pd.read_csv(self.path)
        
        except Exception as e:
            
            error_message = f'ERROR {e}\ncheck file directory or name whose giveing as class argument'
            print(error_message)
    
class Tests:
    
    def __init__(self, column, data):

        self.data = data
        self.column = column
        self.time_series = pd.Series(self.data[self.column])
    
    def adfTest(self):

        #test core logic
        adf_test = adfuller(self.time_series)
        p_value = adf_test[0]
        message = f"ADF Test\nADF Statistic: {p_value}\np-value: {adf_test[1]}"
        
        #logs
        print(message)

        for key, value in adf_test[4].items():

            mes = f"\nCritical Value <{key}>: {value}"
            print(mes)
            message = message + mes
            
            
        csvnamee = f'{self.column}_adf_test.csv'
        with open (csvnamee, mode = "w", newline= "") as file:
            file.write(message)

        return adf_test

    def acfTest(self, lags= 12):

        #core
        acf_values = acf(self.time_series, lags)

        #logs
        
        #plot logic
        
        plt.figure(figsize=(10, 5))
        plot_acf(self.time_series, lags=lags)
        plt.title(f'ACF Plot for <{self.column}> (Lags={lags})')
        
        #saving file logic
        png_name = f'ACF_Plot_{self.column}.png'
        plt.savefig(png_name)
        print(f'Plot was built as {png_name}')
        plt.close()
        
        
        #logs logic
        message = f"ACF Values: {acf_values}"
        print(message)
        
        csvnamee = f'{self.column}_acf_test.csv'
        with open (csvnamee, mode = "w", newline= "") as file:
            file.write(message)

        return acf_values

    def pacfTest(self, lags= 12):

        #core
        pacf_values = pacf(self.time_series, nlags=lags, method="ywm")

        #logs
        
        #plot logic
        plt.figure(figsize=(10, 5))
        plot_pacf(self.time_series, lags=lags, method="ywm")
        plt.title(f'PACF Plot for <{self.column}> (Lags={lags})')
        
        #saving file logic
        png_name = f'PACF_Plot_{self.column}.png'
        plt.savefig(png_name)
        print(f'Plot was built as {png_name}')
        plt.close()
        
        #logs logic
        message = f"PACF Values: {pacf_values}"
        print(message)
        
        csvnamee = f'{self.column}_pacf_test.csv'
        with open (csvnamee, mode = "w", newline= "") as file:
            file.write(message)

        return pacf_values

class Parameters:

    def __init__(self, data, column):

        self.data, self.column = data, column
        self.test = Tests(data= self.data, column= self.column)
    
    def parameters(self):

        p_adf = 1
        d = 1 
        
        timeseries = pd.Series(self.data[self.column])
        
        while p_adf > 0.05:
            
            #core logic
            p_adf = adfuller(timeseries)[1]
            timeseries = timeseries.diff().dropna()
            
            #returned value
            d+=1
             

        pacf_values, confict_pacf = pacf(self.test.time_series, alpha= 0.05, nlags= 20, method= "ywm")
        acf_values, confict_acf = acf(self.test.time_series, alpha= 0.05, nlags= 20)

        def find_significant_lag(values, confint):
            
            for i, (val, (lower, upper)) in enumerate(zip(values, confint)):
                
                if i == 0:
                    
                    continue

                if val < lower or val > upper:
                    
                    return i
                
            return 1
        
        p = find_significant_lag(pacf_values, confict_pacf)
        q = find_significant_lag(acf_values, confict_acf)

        return (d, q, p)
    
class Arima:

    def __init__(self, data ,column):

        #init constructor parameters
        self.data = data
        self.column = column
        
        #init parameters
        self.dpq  = Parameters(data=data, column=column).parameters()

        #model
        self.model = ARIMA(data[column], order= self.dpq)
        self.fit_model = self.model.fit()
        self.summary_model = self.fit_model.summary()
        
    def logs(self):

        log = Log(
            
            message= f'd = {self.dpq[0]}, p = {self.dpq[1]}, q = {self.dpq[2]}\n\ncolumn <{self.column}> \n\n{self.summary_model}',
            save= True, 
            csvname= f'{self.column}_arima.csv'
            
        )
        
        log.logs()
            
    def plot_generate(self, save = True):
            
            png_filename = f'{self.column}_arima_residuals.png'
            title_plot = f'arima {self.dpq} residuals for column <{self.column}>'
            xlabe_plt = f'Time'
            message = f'arima residuals plot for column <{self.column}> was created'
            argument_plot = self.fit_model.resid[1:]
            
            plt.figure(figsize=(10, 5))
            plt.plot(argument_plot)
            plt.title(title_plot)
            plt.xlabel(xlabe_plt)
            plt.ylabel(self.column)
            
            if save:
                
                plt.savefig(png_filename)
                
            else:
                
                plt.show()
                
            plt.close()
            
            print(message)

class ErrorCalculate:
    
    def __init__(self, fit_model, data, column= None):
        
        self.fit_model = fit_model
        self.data = pd.DataFrame(data)
        self.column =column
        
    def errorCalculate(self):
        
        residuals = self.fit_model.resid
        
        if self.column != None:
            
            actual = self.data[self.column].values
        
        else:
            
            actual = self.data.values
            
        #lengts cutting
        min_len = min(len(residuals), len(actual))
        residuals = residuals[:min_len]
        actual = actual[:min_len]
        
        error_metrics = {
            
            "ME": np.mean(residuals).tolist(),
            "MAE": np.mean(np.abs(residuals)).tolist(),
            "RMSE": np.sqrt(np.mean(residuals**2)).tolist(),
            "MPE": np.mean(np.where(actual != 0, (residuals / actual) * 100, np.mean(actual))).tolist(),
            "MAPE": np.mean(np.where(actual != 0, np.abs(residuals / actual) * 100, np.mean(actual))).tolist()
        }
        return error_metrics
        
    
    def logs(self):

        log = Log(
            message= f'model <{self.fit_model.model.__class__.__name__}> for column <{self.column}>\nmodel parameters = {self.fit_model.model.order}\n\nERROR RAPORT:\n\n{self.errorCalculate()}',
            save = True,
            csvname= f'{self.fit_model.model.__class__.__name__}_{self.column}_error_model_log.csv'
        )
        
        log.logs()
        

if __name__ == "__main__":

    dataInit = DataInit("mainDataSet.csv")
    data = dataInit.returnData()
    last_element_index = len(data.columns)
    columns_data = data.columns[1:last_element_index]
        

    for col in columns_data:
        
        arima = Arima(data= data, column = col)
        arima.logs()
        arima.plot_generate()
        
        errorCalculate = ErrorCalculate(arima.fit_model, arima.data, column= col)
        errorCalculate.logs()
        
        deleteOutliers = DeleteOutliers(arima.fit_model.resid, column= col, save= True)
        deleteOutliers.deleteOutliers()
        deleteOutliers.plotEnterface()
        deleteOutliers.plot()
        deleteOutliers.logsEnterface()
        deleteOutliers.logs()

        tests = Tests(data= data, column= col)
        adf_test = tests.adfTest()
        acf_value = tests.acfTest()
        pacf_value = tests.pacfTest()

    
        



        
        

        


        



    

