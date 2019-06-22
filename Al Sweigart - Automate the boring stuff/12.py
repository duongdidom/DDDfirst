""" program randomise numbers from 1 to 10, and ask user to guess that number
user will input user's guess up to 5 times
after 5 attempts, programs will reveal the answer if user's previous guess are all incorrect
programm will let user knows if the guess is either too low or too high than the number the program picks
"""

import random

print ("I am gonna pick a number between 1 and 10, would you like to guess what that is?")
# randomise includes end number
guessInt = random.randint(1,10)

# loop 5 times for number of guess
for n in range(1,6): 
    # assign value for user input. Also convert to integer
    userInput = int(input("your guess is: "))

    if  userInput > guessInt:
        print ("Your guess is too high, please try again")
        n = n+1
    elif userInput < guessInt:
        print ("Your guess is too low, please try again")
        n = n+1
    else:
        # user guesses correctly
        break

if userInput != guessInt:
    # user could not guess correctly after 5 attempts
    print ("You failed all 5 attempts. My number is " + str (guessInt) + ". Thanks for trying")
else:
    # user guess correctly without using 5 attempts.
    print ("You take " + str(n) + " attempt(s) to guess my picked number: " + str(guessInt))