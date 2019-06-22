# 12/11/2018: https://cognitiveclass.ai/courses/python-for-data-science/

# # 1 # data types:
# print(type(11))    # 11 = int
# print(type( -123))    # -123 = int
# print (type(0))   # 0 = int
# # print type(12.0) # 12.0 = float
# print (type (6/3))  # 6/2 = float
# print (type(6//2))  # 6//2 = int. double // means take division then convert to integer
# print(type(12.11122))  # 12.11122 = float
# print(type ("holla as string"))    # "holla as string" = str

# # convert data type:
# float (2)   # = 2.0
# int (1.1)   # = 1
# str (1.1)   # = '1.1'. To convert float to string
# float ("A") # = could not convert string to float
# bool(1)     # convert number to boolean 1=True; 0=False
# int(True)   # convert boolean to number
# int("1.01") # convert "1" to int is ok. But cannot convert "1.01" to int
# int(float ("1.01"))  # = 1. To convert "1.01" to int, has to convert from string to float first, then convert float to string

# # variables:
# my_var = 10000000+1
# print(my_var)
# my_var_2 = my_var + 9000
# print(my_var_2/2)

# # String: it's helpful to think string is an sequence of characters, we can access individual characters by indexing the sequence
# Michael_name = "Michael Jackson"
# Michael_name[2]   # find 2nd character from the left = c. Note: indexing in python always starts from 0; space also counts as 1 character
# Michael_name[-2]    # find 2nd character from the right = o.
# Michael_name[-0]    # Note: when starting from the right, indexing starts from -1. Because [0] = [-0]
# Michael_name[0:4]   # find characters from position 0 to 4 from the left
# Michael_name[::2]   # stride values: starting from 0, select every 2nd characters, 0th character inclusive
# Michael_name[1:7:2]   # stride values: start from character 1 to 7, select every 2nd characters, 1st character inclusive
# len (Michael_name)  # string length
# Michael_name + "is best"    # concanate string
# (Michael_name + " ")*3     # replicate string
# print ("new line: \n new line") # \n = new line
# print ("tab: \t after tab") # \t = tab
# print ("back slash: \\ after back stash")   # \\ = back slash
# print(Michael_name.upper())   # upper case all characters
# print(Michael_name.lower())   # lower case all characters
# print (Michael_name.replace ("Michael","bla"))  # replace character
# print (Michael_name.find('ael'))    # find the position of the first character that need to find
# print (Michael_name.find('sea'))    # return -1 if not found any match
# print (Michael_name.find('Ael'))    # watch out for exact lower or upper case

############################################################################################################################################################################
# # 2 # tuples
# # contains multiple values, in either string, integer or float type. Values in the tuple can be recalled by indexing number similar to string
# tuple1 = ("disco",10,-12,1.1)     # define tuple in ()
# type(tuple1)    # type of tuple = tuple
# tuple1[0]   # index 1st value in tuple
# tuple1[-1]  # index last value in tuple
# tuple2 = tuple1 + ("new value1" , -999)     # concatenate tuple
# print (tuple2)
# print (tuple2[5])   # index new value in tuple
# tuple2 [2:5]    # slicing tuple
# len(tuple2)     # count number of elements in tuple
# # tuples are IMMUTABLE by default: we cannot change values or order or remove, etc inside tuple. If required, we have to create another tuple to change them
# tuple1 = (3,2,-1,10,12)
# sortedTuple1 = sorted(tuple1)
# print (sortedTuple1)
# # can nest tuple inside a tuple
# tuple1 = (-1,0,("str1","str2"),1,2)
# print (tuple1[2])   # 3rd element in tuple is another tuple = ('str1', 'str2')
# print (tuple1[2][0])    # 1st element in nested tuple = ('str1')
# print (tuple1[2][0] [1])    # = "t". 2nd character of 1st element in nested tuple

# # 3 # list
# # similar to tuple, list can contains string, integer, float, tuple, nest tuple, nest list. However, list is MUTABLE
# list1 = ['MK',-111, 23.11]    # define tuple in []
# print (list1)
# list1.extend(["new value1",-123,321])   # function extend() = add new element(s) to existing list, without creating another list
# print (list1[3])
# list1 = list1 + list1
# len(list1)  # there are 6 elements in list1 extended

# list1 = ['MK',-111, 23.11]
# list1.append(["new value1",-123,321])   # function append() = add ONE element to existing list
# print (list1[3])
# len(list1)  # there are 4 elements in list1 appended, despite appending 3 items

# # amending the list:
# list1[0] = "replace MK with 0"  # change the first element
# print (list1[0:2])
# del(list1[1])   # delete the 2nd element
# print (list1)

# "replace MK with 0".split(" ")  # function split() split string into list, seperated by condition

# # list alias and clone
# list2 = list1   # can create alias by referring one list to another variable name
# print (list2)
# list1[1] = 123  # changing element of one list will also change element of alias, since all alias refer to same list
# print (list2)
# list2 = list1[:]    # can create clone version of a list
# print (list2)
# list1[1] = 123  # changing element of one list will NOT change element of the clone
# print (list1)
# print (list2)

# # 4 # set: can store all kind of types. However, do not record element. I.e. order the set randomly, not in a sequence when the set define. And, set can only record 1 type in a set.
# set1 = {"mot", "hai", "ba", "ba"}   # define tuple in {}. Duplicated items will not be presented, only the first item will show up
# set2 = set(list1)   # convert a list into a set
# set1.add("bon")     # add new element into a set
# set1.remove ("bon")     # remove element from a set
# print (" mot" in set1)   # check if an element is in the set. True = yes, False = no
# set3 = {"mot", "hai", "ba", "nam", "sau"}
# set1,set3       # visualise 2 sets
# set4 = set1 & set3   # use & to find common value(s) of 2 sets. This common value(s) will become a new set
# set4 = set1.intersection(set3)  # or can use intersection() function to achieve the same outcome
# set4 = set3.intersection(set1)
# print (set4)
# set3.difference(set1)       # use difference() to find any element in set3 not in set1
# set5 = set1.union(set3)     # use union() function to union all elements in 2 sets
# print (set5)
# print (set1.issubset(set3))  # use issubset() function to check if a set1 is subset of set3.
# print (set3.issuperset(set1))   # use issuperset() function to check if a set3 is superset of set1.
# print (len (set1))      # find numbers of elements in a set = 3
# set1 = {-1,0,1,2}
# print (sum(set1))       # calculate aggregation function for a set

# # 5 # dictionary: contains key and value of each key. The result of querrying a key from a dictionary is always = value of that particular key
# D={'a':0,'b':1,'c':2}   # define dictionary D in {}; each key followed by its value, seperated by colon ':'
# print (D)       # print keys and values in dictionary. Result is expressed in a set
# print ( D.values())     # print all values of dictionary. Result is expressed in a list
# print (D.keys())    # print keys in dictionary. Result is express in a list
# D={"key1":1,"key2":"2","key3":[3,3],"key4":(4,4),('key5'):5,(0,1):6,1:0,99:{"haha"}}
# # key can be any types, or tuple, but not list nor set. Value can be any of those and also can be list or set.
# # key needs to be distinct, no duplicate. Multiple keys can hold same value
# D["key3"]   # to retrieve the value of a particular key
# D[4321] = "1234"    # to add new element into the dictionary
# D
# del(D[4321])    # to remove an element. use del() function and specify key in the dictionary
# D
# 99 in D     # verify if a key is in dictionary
# "haha" in D # Cannot verify value this way

############################################################################################################################################################################
# # 6 # conditions: comparing values and variables
# a = -1  # define value for variable, use only one equal sign '='
# a == -1 # = True. compare if value equal another value, use two equal signs '=='
# a > 0   # = False. compare if value larget or smaller than another value
# a != 0  # = True. compare if value NOT equal another value
# "hh" == "fdsfasf"   # = False. compare if string are the same

# # 7 # branching: if else statement
# age = 21
# if (age > 20):      # remember the colon ':'
#     print ("enter")
# elif (age >= 15):    # second check if the first condition is not true
#     print ("enter back door")
# else:               # procedure if the all conditions are not true
#     print ("do not enter")
# print ("finished. Go home")

# # 8 # logic statement: and, or
# age = 20
# if (age > 20) and (age < 60):
#     print ("enter")
# else:
#     print ("do not enter")

# # 9 # range() function: a range of N produces Ns number of value in ordered sequence [0,1,2,... N-1]. Range only takes integer
# range (3)   # sequence starts from 0 to 2, = [0,1,2]. I.e. total of 3 outputs.
# range (2,5) # sequence starts from first value, continue but excluding the 2nd value

# # 10 # for loop
# squares = ["mot", "hai", "ba",4,5,6]
# for i in range(3):      # Alternative = for i in range(0,3):
    # squares[i] = "bla"
    # print (squares[i])
# print (squares)         # ['bla', 'bla', 'bla', 4, 5, 6]
# for i in range(len(squares)):
#     squares[i] = "blaaaaa"
# print (squares)           # ['blaaaaa', 'blaaaaa', 'blaaaaa', 'blaaaaa', 'blaaaaa', 'blaaaaa']

# for i in range(2,5):    # this loop will start from 3rd element of the list, up to the 5th
#     squares[i] = "bla"
# print (squares)         # ['mot', 'hai', 'bla', 'bla', 'bla', 6]

# # for tuple and list, can loop through those directly instead of via indexing range
# for i in squares:   # but what this means is that the loop will go through all values in the list. Have to use range if wanting to go through only a section of the list
#     print (i)
# tempTuple = (123123.12,-498321)
# for i in tempTuple:
#     print (i)

# # use enumerate to find the index number of the list as well as its equivalent value
# for i, squ in enumerate(squares):
#     print ("index # ",i,"=", squ)

# # 11 # while loop
# newSquares = []     # define new blank list
# i=0                 # define first value for i
# while isinstance(squares[i],str):       # check if element in the squares[] is srting, if so, print out that string value, and append that value to the newSquare[]
#     print (squares[i])
#     newSquares.append(squares[i])
#     i = i+1
# print (newSquares)

############################################################################################################################################################################
# # 12 # functions: can only be called after they are defined. Similar to defining variable
# # start with def & name of function & '(' & parameter & ')' & ':'
# def multiply10(a):  # for e.g. name the function multiply10 with one variable 'a'.
#     a=a*10          # inside the function, variable 'a' takes new value as multiplication of 'a' by 10
#     return a        # return = output of the multiply10 function. (Has to be indented, too)
# multiply10(60)      # = 600. Python return integer output for integer input
# multiply10(1.412)   # = 14.12. Python return float output for float input
# multiply10("blaa")  # = 'blaablaablaablaablaablaablaablaablaablaa' Python return replication of string as output for string input

# def aggreg(a,b):   # define aggreg function in short super simplified spec. Input 2 values 'a','b'. Return the addition of those
#     return a+b
# aggreg(1,2)        # = 3
# aggreg(923123, "asdf")    # = error. cannot add integer and string together

# def blaaaa():       # can create function to do something, without returning output.
#     print ("blaaa") # in this case, calling function blaaa() will print "blaaa"
# blaaaa()

# def printstuff(stuff):
#     print (global_scope_variable)       # global_scope_variable is not defined in the local scope function, it will look up if this variable has been defined prior in global scope 
#       # note: if global_scope_variable is already been defined in function, it will overide value in global scope, and takes new value within the function.
#     for i, s in enumerate(stuff):
#         print ("album " , i , " rated ", s)
# tempList = [10,8.5,9.5]     # define an example list
# global_scope_variable = "this is global scope value"    # if not defining global scope, the function will return error message and terminate the function
# printstuff(tempList)        # call function printstuff() with variable tempList
# print (i)       # = error, not defined. variable inside the scope function cannot be access outside the function. I.e. Cannot access local scope variable

# def function_without_return():
#     print ("aaa")
# print (function_without_return())   # when print a function without return, python will do whatever inside the function, and the return None.

# def default_variable(aa=4):     # define function where variable aa takes defult value 4
#     if (aa > 0):
#         print ("positive")
#     elif (aa == 0):
#         print ("zero")
#     else:
#         print ("negative")

# default_variable (-1)   # = negative. call function where variable is NOT ommitted
# default_variable (0)    # = zero
# default_variable ()     # = positive. call function where variable is ommitted. Function takes aa as 4 then carry on inside function

############################################################################################################################################################################
# # 13 # class: contains data attributes and methods attributes
# start with class & class name & '(' & class parent & ')'
# class circle (object):
#     def __init__ (self, radius, color):     # _in-it_() function stand for initialise constructor: to tell python to make new class.
#                                             # self parameter = new created instance of class
#                                             # radius , color = parameter to initialise data attributes
#         self.radius = radius    # passing radius attribute from radius parameter
#         self.color = color      # passing color attribute from color parameter

# # name a new object under the class circle, using the object constructor
# C1 = circle(10, "red")
#     # the constructor then becomes
#     # class circle (object):
#     #     def __init__ (self, 10, "red"): 
#     #         self.radius = 10    
#     #         self.color = "red"
# C1.radius   # = 10. find radius value of C1 circle 
# C1.radius = 100     # define new value for radius attribute
# print (C1.radius)   # double check C1's radius

# # methods are function that interact and change data attributes. 
# class rectangle (object):
#     def __init__ (self, color = "purple", height = 9, width = 1):      # define new class constructor with default value
#         self.color = color 
#         self.height = height
#         self.width = width
#     def newheight (self,h):     # define new method within class. Using parameter self and h (h is also optional)
#         self.height = self.height + h
#         return (self.height)
#     def drawRectangle(self):
#         import matplotlib.pyplot as plt     # import matplotlib to be able to draw picture
#         plt.gca().add_patch(plt.Rectangle((0, 0),self.width, self.height ,fc=self.color))
#         plt.axis('scaled')
#         plt.show()
# R1 = rectangle("yellow", 9, 1)
# # print (R1.newheight(999))   # = 1110 = 999 + 111 
# print (R1.color , " " , R1.width)   # other attributes don't change
# print (dir(R1))     # dir() function returns list of data attributes and methods of the class. However, no the value of the attributes
# R1.drawRectangle()

# # lab practice:
# class Car(object):
#     def __init__(self,make,model,color):
#         self.make=make
#         self.model=model
#         self.color=color
#         self.owner_number=0 
#     def car_info(self):
#         print("make: ",self.make)
#         print("model:", self.model)
#         print("color:",self.color)
#         print("number of owners:",self.owner_number)
#     def sell(self):
#         self.owner_number=self.owner_number+1

# my_car = Car("BMW","M3","red")      # create car instance under class Car, named my_car
# my_car.car_info()
# for i in range(5):
#     my_car.sell()
# print (my_car.car_info())

############################################################################################################################################################################
# # 14 # reading, write, append files
# # open() function: get the file object, open("filepath/filename",mode). Where mode can be w = write, r = read, a = appending, r+ = read & write
# # if python and text files are in the same directory then do not need to specify filepath
# pa2file = open ("C:/Users/douglas.cao/Google Drive/Python/read text file.txt","r")     # read file read text file and store it in pa2file variable
# pa2file.name    # = C:/Users/douglas.cao/Google Drive/Pythonread text file.txt. Full file path and name of the file
# pa2file.mode    # mode of the object
# pa2file.close() # always recommend to close the object
# pa2file.readable()    # check if a file is readable
# with open ("C:/Users/douglas.cao/Google Drive/Python/read text file.txt","r") as pa2File:     # use with statement will always automatically close the file
#     read_pa2 = pa2File.read(4)   # read() function store values of the file in string format. Value in parameter = number of characters going to be read
#     print   (type(read_pa2))    # = str
#     readlines_pa2 = pa2File.readlines()      # readlines() output every line as an element, then put them in a list
#     readline_pa2 = pa2File.readline()       # readline() -- without 's' -- output single line at a time
#     print (read_pa2)
#     print (readlines_pa2)
#     print (readline_pa2)

# print (pa2File.closed)        # boolean if the pa2File has been closed
# print (read_pa2)              # can print read, readline, readlines result after open() has closed
# print (readlines_pa2)
# print (readline_pa2)

# with open ("C:/Users/douglas.cao/Google Drive/Python/read text file.txt","r") as tempFile:    # loop through each line, using readline()
#     for n in tempFile:
#         print (n)

# with open ("C:/Users/douglas.cao/Google Drive/Python/new text file.txt","w") as writeFile:    # write mode. if file doesn't exist, python will create new file
#     writeFile.write("new sampleline 2")     # write() overwrite existing contents with contents in bracket
#     newText = ["line text 1","line text 2","line text 3"]
#     for n in newText:
#         writeFile.write(n + "\n")   # write each element in newText[] list and add a new line each time 

# with open ("C:/Users/douglas.cao/Google Drive/Python/continue file.txt","a") as appendFile:     # mode append will add new data into the file, without replacing existing data
#     appendFile.write("add new line 1")

# # copy content of one file to another: open source file in read mode and open destination file in write mode. For every line in source file, write new line in
# with open ("C:/Users/douglas.cao/Google Drive/Python/read text file.txt","r") as readFile:        # open source file as read
#     with open("C:/Users/douglas.cao/Google Drive/Python/new text file.txt","w") as writeFile:     # open destination file as write
#         for n in readFile:
#             writeFile.write(n)

############################################################################################################################################################################
# # 15 # pandas: pre-built library for data analysis
# import pandas as pd     # import library and use pd as alias
# csv_file = "https://ibm.box.com/shared/static/keo2qz0bvh4iu6gf5qjq4vdrkt67bvvb.csv"    # assign csv file to a variable
# dfcsv = pd.read_csv(csv_file)      # read csv file and store it in df variable (short for dataframe)
# xlsx_file='https://ibm.box.com/shared/static/mzd4exo31la6m7neva2w45dstxfg5s86.xlsx'     # assign xls file to a variable
# dfxls = pd.read_excel(xlsx_file)      # method for reading excel file
# print (dfcsv.head())       # head() method returns first 5 rows of the dataframe, by default
# print (dfxls.head(10))      # head(n) with specified parameter, print first n+1 rows of the dataframe. It assumes the first row is header row
# temp1 = dfxls[["Length"]]  # create new dataframe temp1, (with column header). Where data is from specified column in dataframe dfxls
# temp1
# temp2 = dfxls["Length"]     # create new dataframe temp2, (without column header)
# temp2
# temp3 = dfxls [['Artist','Length','Genre']]     # using multiple columns
# temp3

# # can create dataframe out of a dictionary where column header = key; data in a column = elements in a list. Then cast dictionary to dataframe by using function dataframe

# dfxls.iloc[1,0]         # iloc() - index location - method to index particular location in a dataframe. Similar to cells() function in VBA. Python index 1st row and column with 0
# dfxls.loc [0,"Artist"]  # loc() - location - use to access n-th element in a specified column
# dfxls.iloc[0:2, 3:6]        # use iloc() to cut a sub-section of the dataframe, where column header is NOT specified.
#                             # before comma: starting from row 0 up to before row 2. After comma: start from column 3 up to before column 6 
# dfxls.loc [2:7, "Genre":"Soundtrack"]    # use loc() to cut a sub-section of the dataframe, where column header is specified
#                             # before comma: start from row 2 up to before row 7. After comma: where column name from "Genre" to "Soundtrack"

# df1 = df[df['Released'] >= 1920]    # this code will extract all columns in dataframe df, where value in 'Released' column >= 1920
# df1.to_csv("sample.csv")    # save a particular dataframe to csv file

############################################################################################################################################################################
# # 16 # numpy
# import numpy as np 
# a = np.array([-2,-1,3,4,6]) # assign a list into an numpy array. Consider that this array will become a vector = a vertical order
# b = np.array ([[123,876],[343,-67],[480,33]])  # assign multi dimension array. Notice: using [] inside the ()
# b   # b becomes     [123,876]
#     #               [343,-67]
#     #               [480,33]
# a[0]        # = -2
# b[0]        # = array([123, 876])
# b[2][1]     # = 33  = 3rd row, 2nd column
# b[0:2,0]    # = [123, 343]  = row from 0 to before 2, column 1
# b [1:3][1]  # = array([480,  33]) = row from 1 to before 3, then 2nd row
# type (a)    # = class 'numpy.ndarray'
# a.dtype     # = type (a[0]) = type of data in numpy array
# a.size      # = 5 = elements of array = number of row * number of column = 5 * 1
# b.size      # = 6 = 3*2
# a.ndim      # = 1 = dimension of the array. In case array has more than one dimension
# b.ndim      # = 2
# a.shape     # = (5,) = size of the array each dimension
# b.shape     # = (3,2) = 3 rows/lists, 2 columns/size each list
# a[1] = 10   # change value of the n-th element of the array
# a
# a[1:3]      # select array element from 1 to before 3
# a[1:5] = 1,11,111,1111  # change multiple valur of the array
# a
# # using vector operation with 1 dimension array
# u = np.array([1,0])
# v = np.array([11,21])
# z = u + v
# z       # = array(1+11,0+21) = array(12, 21)
# z = u - v
# z       # = array([-10, -21])
# z = 2 * u
# z       # = array([1*2, 0*2]) = array([2, 0])
# z = u * v 
# z       # = array([1*11,0*21)] = array([11, 0])
# z = np.dot(u,v)       # numpy dot() function takes multiplication of same location value between arrays, then add them together. Useful in multiply matrix
# z       # = 1*11 + 0 *21 = 11
# z = u+10    # add constant to array
# z           # = array([11,10])
# v.max()     # = 21
# v.mean()    # = 16
# v.std()     # = 5
# b.T     # = array([[123, 343, 480],
#         #           [876, -67,  33]]) = transpose
# np.pi       # = 3.14 = pi number
# u = np.array([0, 144 , np.pi])     # assign value for array u
# u_sqrt = np.sqrt(u)      # u_sin is a function of variable u
# u_sqrt       # = array([0. , 12. , 1.77245385]) = calculate square root for every value in array u
# np.linspace(-2,3,8)    # linspace() return evenly space numbers over specified interval. 1st value = starting point, 2nd value = ending point, 3rd value = number of samples
# generate 100 values from 0 to 2*pi >>> create function sin of those values >>> plot that sin function
# x = np.linspace(0,2*np.pi,100)
# y = np.sin(x)
# import matplotlib.pyplot as plt
# plt.plot (x,y)
# plt.show()      # graph the function

############################################################################################################################################################################
"""
try, except, else, finally
"""


def try_except_else_finally():
    # test for anything inside try if return any error
    try:
        x = 1  # x=x+1 would yield error because x has not yet been defined
    # if return any error, run whatever inside except below
    except:
        x = "error in try"
    # if anything inside try does not return any error, run whatever inside else below
    else:
        x = x + 999
    # always run whatever inside finnaly below, regardless whether try return error or not. I.e. after running except or else
    finally:
        print(x)


######################################################################
r""" 
regular expression, RegEx
find certain pattern in given string

identifier:
\d = any number
\D = anything but number 
\s = space
\S = anything but space
\w = letter
\W = anything but letter
. any character except new line
\b = spaces around words
\. = period '.'

modifier:
\d{1,5} = any number that has 1-5 digits. E.g 1234, 99, 433. But not 123456
+ = matches 1 or more
? = matches 0 or 1
* = matches 0 ore more
$ = match end of string
^ = match start of string
| = match either or. E.g. a|b = match a or b
[a-zA-Z]... = find any lowercase letter from a-z and uppercase from A-Z
{x} = x amount of preceding code

white space character:
\n = new line
\s = space 
\t = tab
\e = escape
\r = carriage return
\f = form feed

escape required '\'
. + * ? [] $ ^ () {} | \ /
"""


def regular_expression():
    # example string
    str_example = '</P><A HREF="https://msdn2.microsoft.com">MSDN Home Page</A></P><A HREF="http://www.microsoft.com">Microsoft Corporation Home Page</A></P><A HREF="http://blogs.msdn.com/bclteam">.NET Base Class Library blog</A></P><A HREF="https://gmail-google.net/login">Login page Gmail by Google</A></P>'

    # find all url after A HREF=\
    r"""
    http = 'http' word
    s? = 0 or 1 letter s
    :// = colon, forward slash, forward slash characters
    [a-z\d]+ = one or more letter and number by however length
    .? = zero or one period '.' character
    -? = one or more dash '-' character
    \w*\d* = any letter and number by however length
    \. = period '.' character 
    [a-z0-9]* = any letter and number by however length
    \/? = zero or one forward slash character
    """
    str_URL = re.findall(
        r"https?://[a-z\d]+.?-?\w*\d*\.[a-z0-9]*\/?[a-z0-9]*", str_example
    )

    print(str_URL)


############################################################################################################################################################################
# working with datetime module
# useful link: https://www.w3schools.com/python/python_datetime.asp
from datetime import timedelta, date, datetime

start_date = date(2013, 1, 1)
end_date = date(2013, 1, 10)

for x in range(0, (end_date-start_date).days):  # loop from 0 to number of days from start date to end date. 
                                                # range() function excludes end date
        print (start_date + timedelta(x))       # for each loop, convert x from inteter to date using timedelta. Plus that number to start date
x = datetime(2018, 6, 1)

print(x.strftime("%Y%m"))


############################################################################################################################################################################
# 17 function enumerate() generate index number for each item in a list. Could be useful for looping
seasons = ['Spring', 'Summer', 'Fall', 'Winter']
for l in enumerate(seasons): print (l)
for l in enumerate(seasons): print (str(l[0]) + " = " + l[1])