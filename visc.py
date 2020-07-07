import pandas as pd
import numpy as np
from sklearn import datasets, linear_model

def visc(fluid, temp):
    #getting address for fluid property file
    fluidfolder = r"M:\NIST_Tables"
    fluidadd = fluidfolder + '/' + fluid + '_' + str(temp) + '.cgi'
    #fluidadd = r"M:\NIST_Tables\co2_25.cgi"
    df_fluid = pd.read_csv(fluidadd, sep = '\t')
    #preparing data for LR
    X = np.array(df_fluid['Pressure (psia)']).reshape(-1,1)
    Y = np.array(df_fluid['Viscosity (cP)']).reshape(-1,1)
    X_train = X[30:]
    Y_train = Y[30:]
    #regressing data
    regr = linear_model.LinearRegression()
    regr.fit(X_train, Y_train)
    #extracting coefficient and intercept
    a=np.asscalar(regr.coef_[0])
    b=np.asscalar(regr.intercept_[0])
    return(a,b)

