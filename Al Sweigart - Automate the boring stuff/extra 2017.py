"""
# Albert Sweigart, "Logging and Testing and Debugging, Oh My!", PyBay2017
# URL https://youtu.be/ONCVvS-gDMA

import logging
logging.basicConfig(level = logging.DEBUG)  # can add filename parameter to it
logging.disable(logging.CRITICAL)   # this will remove everything critical and below

first = input("enter 1st number: ")
logging.debug(type(first))  #note: function level eg debug() in this case is lower case. While, constance that represents the level themselves as in line 5 above is upper case

second = input("enter 2nd number: ")
logging.debug(type(second))

print ("sum of two numbers = " + first + second)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# It's Time to Learn Regular Expressions PyCon 2017
# URL https://www.youtube.com/watch?v=abrcJ9MpF60
