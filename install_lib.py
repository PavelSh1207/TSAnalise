import subprocess
import sys

class Libs:
    libs = [
            'numpy', 
            'pandas',
            'statsmodels',
            'matplotlib',
            ]
    
    def install(self):
        for lib in self.libs:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                
            except Exception as e:
                print(f"ERROR IN LIB INSTALATION: {e}")
                
            print('='*100)
    
    def check(self):
        error_mes = 'ERROR IN LIBS CHECKING:'
        
        for lib in self.libs:
            try:
                result = subprocess.check_output([sys.executable, "-m", "pip", "show", lib], stderr=subprocess.STDOUT)
                print(f"{lib} installed suckcefull Version: {result.decode().strip()}")
                
            except subprocess.CalledProcessError as subprocess_error:
                print(f'{error_mes} {subprocess_error}')
                
            except Exception as e:
                print(f'{error_mes} {e}')
            
            print('='*100)

if __name__ == "__main__":
    
    Libs().install()            
    Libs().check()
                                            