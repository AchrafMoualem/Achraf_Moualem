#Exercise 1 : Hello World-I love Python
print("Hello world\n" * 4 + "I love python\n"*4) 


#Exercise 2 : What is the Season ?
month = str(input("tape the month : ")).lower()
if month=="march" or month=="april" or month=="may":
    print(month + " is in spring.")
elif month=="june" or month=="july" or month=="august":
    print(month + " is in summer.")
elif month=="september" or month=="october" or month=="november":
    print(month + " is in autumn.")
elif month=="december" or month=="janaury" or month=="febraury":
    print(month + " is in winter.")