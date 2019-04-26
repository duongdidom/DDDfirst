# # lesson 1: 15/Aug
# # declare variables

# x = "hello11111111"     #string variable, inside double quotation symbol "" 
# y = "50"        
# y1 = 50
# y2 = 434.111    #number/decimal, without double quotation mark
# isMale  = True  #boolen, variable value = True or False
# xplusy = x + y 

# # main code
# print (x+y) 
# print ("haha\n new line")   #\n = new line
# print ("haha\" quotation mark")    #\" = double quotation mark
# print ("haha".upper())  #access built in function with . after variable #e.g. upper, lower, etc....
# print ("haha".upper().islower())    #function after function
# print(len(x+y))  #string length
# print (xplusy[2])  #python start indexing character from 0 instead of 1. Access by using []
# print (xplusy.index("5"))   #index to find character in the string. Will through error if character doesn't exist
# print (xplusy.replace("hell","hall"))

# # lesson 2: 17/Aug/2018: loop
# import datetime

# startD = datetime.datetime.strptime("01/07/2018","%d/%m/%Y")
# endD = datetime.datetime.strptime("31/07/2018","%d/%m/%Y")
# dates = [startD + datetime.timedelta(days=x) for x in range(0, (endD-startD).days)]     #every single dates from start dates to end dates

# # main:
# for date in dates:  # loop each date in dateS
#     yyyymmdd= date.strftime("%Y%m%d")   #strip string, convert to yyyymmdd format
#     print (yyyymmdd)

# # lesson 3: loop. Watch out for indentation. The end of the loop is identified by the indentation
# for i in range(5):  # this will print "wow" under each of number, i.e. "wow" is inside the loop
#     print (i)
#     print ("wow")

# for i in range(5):  # this will print each number and then "wow" string. i.e. "wow" is after the loop. 
#     print (i)
# print ("wow")

# # lesson 4: 20/Aug/2018: file path
# import os
# import glob

# # Folder where original parameters and position are kept    
# os.chdir(r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\original pa2 and position") 

# # Find the latest parameter file 
# yyyymmdd = "20180817"   
# latest_pa2_file = max(glob.iglob('NZX.' + yyyymmdd + '*.pa2'), key=os.path.getmtime)    #find pa2 file with on yyyymmdd date with latest modified time (getmtime)
# print (latest_pa2_file)
# latest_pa2_filepath = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\original pa2 and position" + "\\" + latest_pa2_file
# print (latest_pa2_filepath)
# # Find the latest position file
# latest_position_file = max(glob.iglob('SPANPOS_' + yyyymmdd + '*.txt'), key=os.path.getmtime)
# latest_position_filepath = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\original pa2 and position" + "\\" + latest_position_file
# print (latest_position_filepath)


# # lesson 5: anconda with VS code: https://www.youtube.com/watch?v=g-aS9oVY-DA
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 20, 100)  # Create a list of evenly-spaced numbers over the range
plt.plot(x, np.sin(x))       # Plot the sine of each x point
plt.show()                   # Display the plot

