from statsmodels.tsa.ardl import ARDL
from statsmodels.tsa.stattools import adfuller
import pandas as pd
from arima_model_core import DataInit, Log, ErrorCalculate, DeleteOutliers
from typing import override
import matplotlib.pyplot as plt
 
class CreatedDeleteOutliers(DeleteOutliers):

    @override
    def plotEnterface(self):

            self.png_filename = f'{self.column}_ardl_delete_otliers.png'
            self.title_plot = f'ardl delete otliers for column <{self.column}>'
            self.xlabe_plt = f'Time'
            self.message = f'ardl delete outliers plot for column <{self.column}> was created'

    @override
    def logEnterface(self):
        
        self.log = Log(
            
            message= f'ardl filtred outliers:\n {self.filtred_data}',
            save = self.save,
            csvname= f'ardl_filtred_outliers_{self.column}_log.csv'

            )

class ModelARDL:

    def __init__(self, filename):

        #parameters init
        try:
            
            dataInit = DataInit(filename)
            self.data = dataInit.returnData()
            
        except Exception as e:
            
            error_message = f'ERROR {e}\ncheck file directory or name whose giveing as class argument'
            print(error_message)

    def ardl(self, lags = 1, dep_var = None, ex_var = None):

        self.dep_var = dep_var
        self.ex_var = ex_var

        def optimal_diff(timeseries):

            #inicialisation parameters
            
            p_value = adfuller(timeseries)[1]
            time_diff = pd.DataFrame(timeseries)
            diff_count = 0
            first_p_value = p_value

            #core logic

            while p_value > 0.05:

                time_diff = time_diff.diff().dropna()
                diff_count += 1
                p_value = adfuller(time_diff)[1]

            #logs

            log = Log(message = '')
            
            if diff_count != 0:

                log.message = f'time series is stionarity p_value is {p_value}'
            
            else:

                log.message =  f'time series was non stationarity p_value was {first_p_value}, therefore timeseries was different {diff_count} times and p_value now is {p_value}'

            log.logs()

            #returned value

            return time_diff
    
        #initilaistion parameters

        self.time_series_dep_var = optimal_diff(self.data[dep_var])
        self.time_series_ex_var  = optimal_diff(self.data[ex_var])  
   
        #core logic

        self.model_ardl = ARDL(self.time_series_dep_var, lags = lags, exog= self.time_series_ex_var)
        self.result = self.model_ardl.fit()
        self.summary_model_ardl = self.result.summary()

    def plot(self, save = False):

            png_filename = f'{self.dep_var}_ardl_residuals.png'
            title_plot = f'ardl residuals for column <{self.dep_var}>'
            xlabe_plt = f'Time'
            message = f'ardl residuals plot for column <{self.dep_var}> was created'
            argument_plot = self.result.resid[1:]
            
            plt.figure(figsize=(10, 5))
            plt.plot(argument_plot)
            plt.title(title_plot)
            plt.xlabel(xlabe_plt)
            plt.ylabel(self.dep_var)
            
            if save:
                
                plt.savefig(png_filename)
                
            else:
                
                plt.show()
                
            plt.close()
            
            print(message)

        
    def logs(self):
        
        log = Log(
            
            message = f'Model ARDL for depend variable is <{self.dep_var}>. explain variable is <{self.ex_var}:\n{self.summary_model_ardl}',
            csvname= f'ardl_for_{self.dep_var}_{self.ex_var}.csv',
            save = True
            
            )
        
        log.logs()


         
class CustomError(ErrorCalculate):
    
    @override
    def logs(self):
        
        log = Log(
            message= f'model <{self.fit_model.model.__class__.__name__}> for column <{self.column}>\nmodel parameters = {self.fit_model.model._order}\n\nERROR RAPORT:\n\n{self.errorCalculate()}',
            save = True,
            csvname= f'{self.fit_model.model.__class__.__name__}_{self.column}_error_model_log.csv'
        )
        
        log.logs()
            
    

if __name__ == "__main__":
    
    ardl_model = ModelARDL("mainDataSet.csv")
    columns_data = ardl_model.data.columns
    ardl_model.ardl(dep_var= columns_data[3], ex_var= columns_data[[2]])
    ardl_model.logs()
    
    errorModel = ErrorCalculate(ardl_model.result, ardl_model.data, column= columns_data[3])
    customEerrorModel = CustomError(ardl_model.result, ardl_model.data, column= columns_data[3])
    customEerrorModel.errorCalculate()
    customEerrorModel.logs()
    
    deleteOutliers = CreatedDeleteOutliers(data= ardl_model.result.resid, column = columns_data[3], save= True)
    deleteOutliers.deleteOutliers()
    deleteOutliers.logsEnterface()
    deleteOutliers.logs()
    deleteOutliers.plotEnterface()
    deleteOutliers.plot()
    
    ardl_model.plot(save= True)
    
    
    
    
    
        
        



