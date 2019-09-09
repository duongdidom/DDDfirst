""" 
Documenting and Refactoring

https://www.youtube.com/watch?v=8vQZourua0U
""" 

def printdoc_string():    
    return __doc__

def main():
    """ main function. Do not import """   
    print(printdoc_string())

if __name__ == "__main__":    
    main()