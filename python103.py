# 28/11/2018
# https://www.youtube.com/watch?v=rfscVS0vtbw&t=7237s

# build a comprehensive calculator. Allow the user to input 2 numbers, select operator, then calculate the result

num1 = float(input("enter first number:"))  # variable 1 & 2: ask for input, then convert to float
num2 = float(input("enter second number:"))
op = input("enter operator: +,-,/,*")       # ask for operator input from user

# check the operator input variable op, then do the calculation, then print the calculation
if op == "+":
    print (num1 + num2)
elif op == "-":
    print (num1 - num2)
elif op == "*":
    print (num1 * num2)
elif op == "/":
    print (num1 / num2)
else:
    print ("invalid operator")

###########################################################################################################################################################################
define a secret word, keep asking the user to input a word until the guess word matches the secret word

secret_word = "bla"     # define secret word
guess_word = ""         # define guess word
n = 0                   # set default number of trial for the guessing game = 0
n_limit = 3             # define maximum amount of guess user can input

while secret_word != guess_word and n < n_limit: # loop as long as the guess_word matches secret_word and number of guess trial is less than the defined limit
    guess_word = input("enter guess word: ")
    n += 1  # equal to n = n+1

if secret_word != guess_word:   # after running loop, if the guess word not = secret word, then say you loss. Else say you win
    print ("Run out of trial, you loss :( ")
else:
    print ("Congratulation, correct guess !")

###########################################################################################################################################################################
# exponential 
print (2**3)    # =8

# define a function to calculate exponential
def raise_to_power(base_num, power_num):        # raise_to_power() function with base_num and power_num as variables
    temp = base_num
    for n in range(power_num-1):
        temp *= base_num
    return temp

print (raise_to_power(3,200000))

###########################################################################################################################################################################
# convert every vowel in a string to letter "m"
def transl(input):  # define translate() function
    output = ""
    for letter in input:        # loop for each letter in input variable
        if letter in "aeiouy":  # if the letter is vowel
            if letter.isupper() is True:    # if letter is upper case
                output = output + "M"   # vowel = existing vowel & "m"
            else:                           # if letter is lower case
                output = output + "m"
        else:
            output = output + letter    # else, vowel = existing vowel & current letter
    return output

print (transl ( input("Please insert word: ")))

###########################################################################################################################################################################
# error catching Try / Except. A good practice is specify every possible error and handle them individually
try:    # anything below try statement is for capturing if they have any error
    # a = 10/0        # this should return error
    print ( int(input ( "Input number only: ")))    # convert input into integer
except ZeroDivisionError as err: # capture divide by zero statement
    print (err)     # print error message
except ValueError:
    print ("Invalid input")

###########################################################################################################################################################################
module: a python file that can be imported into current python file
default is in Lib folder of where python is installed
to install new module: use pip, or given instruction. If using pip, the module will be installed under Lib/site-packages folder
to uninstall: use 'pip uninstall python-docx' for example

inheritance: create a class that has all attributes of the existing class

