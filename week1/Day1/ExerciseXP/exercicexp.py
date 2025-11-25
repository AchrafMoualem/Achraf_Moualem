#Exercice 1 : Hello World
print("Hello wolrd\n" * 4)


#Exercice 2 : Some Math
print((99**3)*8)


#Exercise 3: What is the output?
print(5 < 3) #False
print(3 == 3) #True
#print(3 == "3") #Error
#print("3" > 3) #Error
print("Hello" == "hello") #False


#Exercise 4: Your computer brand
computer_brand = "HP"
print("I have a " + computer_brand + " computer.")


#Exercise 5: Your information
name = "Achraf Moualem"
age = 22
shoe_size = 41
info = f"My name is {name}, I am {age} years old and my shoe's size is {shoe_size}."
print(info)


#Exercise 6: A & B
a = 4
b = 2
if a>b :
    print("Hello World")


#Exercise 7: Odd or Even
a = int(input("Write a number : "))
if a%2 == 0:
    print(f'{a} is even.')
else :
    print(f'{a} is odd.')


#Exercise 8: What’s your name?
name = str(input("What is your name ? "))
if name == "achraf" :
    print("You have stolen my name HAHAHAH ")


#Exercise 9: Tall enough to ride a roller coaster
tall = int(input("What is your height in cm ? "))
if tall > 145:
    print("You are tall enough to ride.")
else :
    print("You need to grow some more to ride.")