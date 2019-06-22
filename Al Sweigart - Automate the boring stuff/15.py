""" methods = similar to VBA, an object (list , variable ...) has method and property """

# sort() function cannot sort between integer and string
# sort() function sort all upper case characters prior to lower case character
mylist = ["Zzzz", 'aa', "Apple", 'goava']
mylist.sort()
print (mylist)

# when explicitly specify key for sort() function, then it will be sorted properly
mylist.sort(key = str.lower)
print (mylist)