# 1. code in global scope cannot use local variable
# 2. code in local scope can use global variable 
# 3. code in one local scope cannot use variable in another local scope --> can use same name for variable as long as they are in different scope

# global variable created when the program initiates
var = 12
twothree = 23

# define function aaa()
def aaa():
    # despite var is assigned as 12 above, print var value here would return error since variable var is not yet LOCALLY defined in aaa() function
    # print (var) 
    # local variable created when its function is initiated
    var = 1234 

    onetwo = 12.12

    # despite not being defined in aaa() scope, can still use global variable twothree
    # illustrate point 2.
    foursix = twothree * 2 

    return var, foursix

# print 1234, 46 as value of var and foursix, a local variables of function aaa()
print ( aaa() ) 

# print 12 as value of var, a global variable. Instead of 1234, value of var, a local variable.
# illustrate point 1.
print ( var )

# try to print onetwo, but will return error since onetwo only exist in aaa() scope
# illustrate point 1.
# print ( onetwo )  

# assign value for double-twothree variable from 2nd result of function aaa()
double_twothree = aaa()[1]
print (double_twothree)

# however would yield error if print foursix, a local variable
# illustrate point 1.
# print (foursix)

# define function bbb()
def bbb():
    # assign a different value for var, local variable in different local scope
    # illustrate point 3.
    var = "one two three four"

    # EXPLICITLY specify python to use global variable twothree, to assign new value to global variable
    global twothree

    # assign new value for global variable twothree
    twothree = "two three 2 3"

    # print var would print the variable define in this local scope only 
    print ( var )


# print twothree would return 23 because global variable was not modified, since bbb() was not called yet
print ("old global twothree = " + str(twothree))

# call function bbb()
bbb()

# print twothree would return new value because global variable was modified, since bbb() has been called
print ("new global twothree = " + str(twothree))