#Exercise 1: Favorite Numbers
my_fav_numbers = {1 , 3 , 5 , 7 , 9 , 11}

my_fav_numbers.add(17)
my_fav_numbers.add(21)
print(my_fav_numbers)

my_fav_numbers.remove(21)
print(my_fav_numbers)

friend_fav_numbers = {2 , 4 , 6 , 8 , 10 , 12}
print(friend_fav_numbers)

our_fav_numbers = my_fav_numbers.union(friend_fav_numbers)
print(our_fav_numbers)


#Exercise 2: Tuple
my_tuple = (1 , 2 , 3 , 4)
l = list(my_tuple)
l.append(5)
l.append(6)
my_tuple = tuple(l)
print(my_tuple)


#Exercise 3: List Manipulation
basket = ["Banana", "Apples", "Oranges", "Blueberries"]
print(basket)
basket.remove("Banana")
print(basket)
basket.remove("Blueberries")
print(basket)
basket.append("Kiwi")
print(basket)
basket.append("Apples")
print(basket)
print(basket.count("Apples"))

basket.clear()
print(basket)


#Exercise 4: Floats
mixed = []
i=1.5
while i<=5:
    mixed.append(i)
    i+=0.5
print(mixed)


#Exercise 5: For Loop
for i in range(1,21):
    print(i)
for i in range(1, 21):
    if (i - 1) % 2 == 0:
        print(i)


#Exercise 6: While Loop
name = input("Enter your name : ")
while len(name)<3 or name.isdigit():
    name = input("give a correct name with no digit and at least 3 letters long : ")
print("thank you ")


#Exercise 7: Favorite Fruits
fav_fruit = input("what are your fav fruits : ").split()
fruits = []
fruits.extend(fav_fruit)

fruittt = input("Enter any fruit : ")
if fruittt in fruits:
    print("You chose one of your favorite fruits! Enjoy!")
else:
    print("You chose a new fruit. I hope you enjoy it!")


#Exercise 8: Pizza Toppings
active = True
toppings = []
while active :
    topping = input("Enter your pizza topping (tape 'quit' to quit adding toppings): ")
    if topping == "quit":
        active = False
        break
    print(f'adding [{topping}] to your pizza')
    toppings.append(topping)
print(f'the price of your pizza with {toppings} is {10 + len(toppings)*2.50} $')


#Exercise 9: Cinemax Tickets
ages = []
while True:
    age = input("enter the age of each person in your family (tape 'quit' to quit) : ")
    if(age == "quit"):
        break
    if age.isdigit():
        ages.append(int(age))
    else:
        print("Please enter a valid age!")

prix_total = 0
for age in ages:
    if age < 3:
        continue 
    elif age <= 12:
        prix_total += 10
    else:
        prix_total += 15

print(f'The total ticket cost is {prix_total} $')


#Bonus
new_ages = []
while True:
    age1 = input("Enter the age of each person in your family (type 'quit' to quit): ")
    if age1 == "quit":
        break
    if age1.isdigit():
        new_ages.append(int(age1))
    else:
        print("Please enter a valid age!")

allowed_ages = []
for age in new_ages:
    if 16 <= age <= 21:
        allowed_ages.append(age)
    else:
        print(f"Age {age} is not allowed. This movie is only for ages 16-21.")

print(f'Clients allowed to watch this movie are: {allowed_ages}')