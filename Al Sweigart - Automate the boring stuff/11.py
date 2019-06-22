# execution below should return error message = ZeroDivisionError: division by zero
# 42/0

# use try and except statement to capture

# assign value for n
n = 2

# try statement
try:
    # execute division and print result 
    print (12 / n)

    # once the code is error, it will NOT execute the rest of the code below until seeing except statment
    print ("Calculation complete")

# except statement. Syntax for error (ZeroDivisionError in this case) normally show up when trying to execute invalid function
except ZeroDivisionError:
    print ("divide by Zero error")

# capturing error when divide by string
except TypeError:
    print ("unable to divide by string value")

# capture all kind of errors
except:
    print ("some error has occured")