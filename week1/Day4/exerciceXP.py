#Exercise 1: What Are You Learning?
def display_message():
    print("I am learning about functions in Python.")

display_message()

#Exercise 2: What’s Your Favorite Book?
def favorite_book(title):
    print(f'one of my favorite books is {title}')
favorite_book("Candide")


#Exercise 3: Some Geography
def describe_city(city,country="Unknown"):
    print(f'{city} is in {country}.')
describe_city("Casablanca","Morocco")
describe_city("Torino")


#Exercise 4: Random
import random
def random_function(n):
    m = random.randint(1,100)
    if n==m:
        print("Success!")
    else :
        print(f'Fail! your number is {n}, Random number is {m}.')
random_function(44)


# Exercise 5: Let’s Create Some Personalized Shirts!
def make_shirt(size,text):
    print(f'The size of this shirt is {size} and the text is "{text}"')
make_shirt("Medium","I love my mom")

def make_shirt(size='Large',text='I love Python'):
    print(f'The size of this shirt is {size} and the text is "{text}"')
make_shirt()
make_shirt('Large')
make_shirt('Medium')
make_shirt('Small','I love Austria')

#(Bonus): Keyword Arguments
make_shirt(size="small", text="Hi friend")


#Exercise 6: Magicians…
magician_names = ['Harry Houdini', 'David Blaine', 'Criss Angel']
def show_magicians(magician_names):
    for i in magician_names:
        print(i)

def make_great(magician_names):
    for i in range(len(magician_names)):
        magician_names[i] = magician_names[i] + " the Great"

make_great(magician_names)
show_magicians(magician_names)


#Exercise 7: Temperature Advice
def get_random_temp():
    return random.randint(-10,40)

def get_random_temp():
    return random.uniform(-10,40)


def main():
    temp = get_random_temp()
    print(f'the temperature right now is {temp} degrees Celsius.')
    if temp < 0:
        print("Brrr, that's freezing! Wear some extra layers today.")
    elif 0 <= temp <= 16:
        print("Quite chilly! Don't forget your coat.")
    elif 16 < temp <= 23:
        print("Nice weather.")
    elif 24 <= temp <= 32:
        print("A bit warm, stay hydrated.")
    elif 32 < temp <= 40:
        print("It's really hot! Stay cool")

main()

#Month-Based Seasons (Bonus)
month = input("Enter a month : ").lower()
season = ""
if month=="march" or month=="april" or month=="may":
    season = "spring"
elif month=="june" or month=="july" or month=="august":
    season = "summer"
elif month=="september" or month=="october" or month=="november":
    season = "autumn"
elif month=="december" or month=="janaury" or month=="febraury":
    season = "winter"

def get_random_temp():
    print(f'in {season} the temperature is {random.uniform(-10,40)} degree Celsius.') 

get_random_temp()