""" interactive message with computer. Input value to computer, computer communicate back to user """

# computer greets user
print("Hello")

# computer request user input
print("Please insert your name")

# assign user input into a variable
UserName = input()

# computer calculate and interact back with user
print("Hello " + UserName + ", your name is " + str(len(UserName)) + " character(s) long.")

# computer request user input again
print("How old are you?")

# assign user age to another variable
UserAge = input()

# second computer interaction
# first, use float to convert string to decimal number, in case user input decimal number
# second, convert float to integer
# third, plus 1 to integer number to work out next year age
# fourth, convert next year age in integer to string to be able to insert to message
print(UserName + ", you are turning " + str(int(float(UserAge))+1) + " next year.")