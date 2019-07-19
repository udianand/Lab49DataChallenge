#	The problem 
#
#	1.Build a script that outputs the average return for an unknown number of 
#	Market Capitalization bins over an unknown time period.
#	For your output, use 5 for the number of bins.
#  
#	2.Generalize the solution to average over any factor, on bins of any factor. 

import os
import sys
import csv
import pandas as pd
import numpy as np
import inquirer
import datetime

class Lab49Challenge():

	"""Main class to calculate the weighted average return over a chosen factor
	for a chosen number of bins. Exposes a public method:get_average_returns()
	to calculate the average returns.
    Args:
        file_name(str): The data source in csv format.

    Attributes:
        file_name(str): The data source in csv format.
        factor(str): The user chosen factor to calculate the returns over.
        num_bins(str): The user chosen number of bins to split the factor into

    """
	RETURNS = "Returns"
	DEFAULT_FACTOR = "Mkt Cap"
	DEFAULT_NUM_BINS = 5
	DEFAULT_FILE_NAME = "equity_data.csv"

	def __init__(self, file_name=None):
		self.file_name = ""
		if file_name == None:
			self.file_name = self.DEFAULT_FILE_NAME
		else: self.file_name = file_name
		self.factor = "" # The user selected factor to average over
		self.num_bins = "" # The user selected number of bins to average over

	def __read_data(self):
		"""Reads csv data from the given file name. The file is stored 
		in the sub-directory called "data" within the current working directory.
    	Scope: 
    		Private
    	Args:
        	None
    	Returns:
        	dataframe: The given csv file in a dataframe.
    	"""
		cwd = os.getcwd()
		equity_data_file_path = cwd + '/' + 'data' + '/' + self.file_name
		equity_data_df = pd.read_csv(equity_data_file_path)
		return equity_data_df

	def __get_factor_name_and_num_bins(self, equity_data_df):
		"""Gets the user-input factor to average over and the number of bins.
		The default factor is set to "Mkt Cap".
		The default number of bins is set to 5.
		The input factors available to select are:
			a. Capitalization
	   		b. Mkt Cap (Default)
			c. FCF Yield
			d. Momentum
			e. Sales Growth 1Y
			f. Sales Growth 5Y
			g. EPS Revision
			h. Date
		The user input is captured in class variables: 
			self.factor and self.num_bins
    	Scope: 
    		Private
    	Args:
        	equity_data_df(data_frame): The Lab49 challenge data.
    	Returns:
        	None
    	"""
		factors = equity_data_df.columns.values.tolist()
		# Excluding colnames: Company Name,Date,Ticker & Returns
		# Will include the Date in the final list
		factors = factors[4:]
		factors.append("Date") 

		MESSAGE_FACTOR = "Please choose a factor. Default is Mkt Cap. " 
		MESSAGE_NUM_BINS = "Please enter the number of bins. Default is 5. "

		chosen_factor = [
			inquirer.List('factor',
	        	message = MESSAGE_FACTOR,
	            choices = factors,
	            carousel= True,
	            default = self.DEFAULT_FACTOR
	              ),
			inquirer.Text('num_bins', 
					message = MESSAGE_NUM_BINS,
					default = self.DEFAULT_NUM_BINS
				),
	    	]
		user_input = inquirer.prompt(chosen_factor)
		
		self.factor = user_input['factor']
		self.num_bins = user_input['num_bins'] 

	def __dtype_conversion(self, factor_data):
		"""Converts the generic data type object of factor data to specific 
		data type. 
    	Scope: 
    		Private
    	Args:
        	factor_data(Series): The factor data of generic type object.
    	Returns:
        	factor_data typecasted to a specific format.
    	"""
		factor_value = factor_data.iloc[0]
		try:
			datetime.datetime.strptime(factor_value, '%m/%d/%Y')
			return pd.to_datetime(factor_data, format='%m/%d/%Y')
		except ValueError:
			return factor_data.str.replace(",","").astype(float)

	def __clean_data(self, equity_data):
		"""Performs data pre-processing. Does the following:
		1. Removes rows which are Na
		2. Type casts data from generic object type to specific 
    	Scope: 
    		Private
    	Args:
        	equity_data(data_frame): The Lab49 challenge data.
    	Returns:
        	data_copy(data_frame): Pre-processed data.
    	"""
		data_copy = equity_data.copy()
		data_copy = data_copy.dropna()
		data_copy[self.factor] = data_copy[self.factor].astype(str)
		factor_data_string_format  = data_copy[self.factor]
		factor_data_typecasted_format = self.__dtype_conversion(factor_data_string_format)
		data_copy.loc[:,self.factor] = factor_data_typecasted_format 
		
		return data_copy

	def get_average_returns(self):
		"""Calculates the weighte average return for a chosen factor over a chosen number
		of bins. 
    	Scope: 
    		Public
    	Args:
        	None
    	Returns:
        	weighted_avg_return_over_all_bin(float): Weighted average of returs
        	over a chosen factor for a chosen number of bins.
    	"""	
		equity_data_df = self.__read_data()
		self.__get_factor_name_and_num_bins(equity_data_df)
		equity_factor_data = equity_data_df[[self.RETURNS, self.factor]]
		equity_factor_data = self.__clean_data(equity_factor_data)

		binned_data = (equity_factor_data
				.assign(Bin=lambda x: pd.cut(x[self.factor], 
						bins = int(self.num_bins)))
      			.groupby(['Bin'])
      			.agg({'Returns': ['sum', 'count', 'mean']}))

		print(binned_data.head())

		sum_returns_per_bin = binned_data['Returns']['sum']
		count_retuns_per_bin = binned_data['Returns']['count']
		mean_return_per_bin = binned_data['Returns']['mean']

		agg_per_bin = pd.DataFrame()
		agg_per_bin['sum'] = sum_returns_per_bin
		agg_per_bin['count'] = count_retuns_per_bin
		agg_per_bin['mean'] = mean_return_per_bin
		agg_per_bin = agg_per_bin[np.isfinite(agg_per_bin['mean'])]
				
		weighted_avg_return_over_all_bin = np.average(agg_per_bin['mean'], 
									weights=agg_per_bin['count'])
		
		return weighted_avg_return_over_all_bin

if __name__ == "__main__":
	
	data_file = "equity_data.csv" #Name of data file
	Challenge = Lab49Challenge(data_file)
	avg_return = Challenge.get_average_returns()
	print("\n Weighted Average Return : % 2f" %(avg_return))  
	
	
