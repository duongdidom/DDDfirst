""" create own function """
# to avoid duplication. Task de-duplicate

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# define function hello
def hello():
    # print hola
    print ("Hola")

# call hello() function
hello()

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# define hello function with parameter name
def hello2(name):
    # print name value
    print("hello " + name)

# call hello2() function
hello2("123")

# if missing parameter, script will return error
hello2()

# however, some function has captured scenario when paramater is null. And function will return None() as a result. 
print()

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# print() function has several parmater
# end. By default is \n meaning create a new line. We can change it to space character
print ("hola", end = " ")
print ("halo")

# sep. By default is " " character. We can change it to ";"
print ("cat", "dog", "pig", sep = " ; ", end = " +++ ")
print ("cat", "dog", "pig", sep = " & ")