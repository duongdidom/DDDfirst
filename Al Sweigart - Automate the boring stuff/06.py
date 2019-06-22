# # program keep asking for user input until user's input = your name

# # set your name = ''
# name  = '' 

# # loop until name variable = your name
# while name != 'your name':     
#     # message user
#     print ("please insert your name")   
#     # override new value for variable name = user's input
#     name = input()

# # thank user
# print ("thanks")



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# # infinite loop
# # terminate by Ctrl C

# # True will always be true, hence execute code in the following block 
# while True:
#     print ("a")


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# # use break() function to get out of loop

# # True will always be true
# while True:
#     # request user input with prompt message
#     # check if the input equal 123
#     if input("please insert your name") == "123":
#         # if user input is 123, break out of loop
#         break
#     # since user input is not 123, loop continue infinitely
#     print ("again")


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# user continue() function to jamp back to loop checking again, without executing any of the code below continue() function
# the code below should print n value for every integer from -5 to 5 except when n = zero

# assign value for n
n = -5

# loop as long as n < 5
while n < 5:
    # add one to n to avoid infinite loop
    n = n + 1
    # check if n = 0
    if n == 0:
        # no longer execute the code below continue function
        continue
    # print value of n
    print ("n value = " + str(n))