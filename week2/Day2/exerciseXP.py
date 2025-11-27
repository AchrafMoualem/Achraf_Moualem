#Exercise 1: Pets
class Pets():
    def __init__(self, animals):
        self.animals = animals

    def walk(self):
        for animal in self.animals:
            print(animal.walk())

class Cat():
    is_lazy = True

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def walk(self):
        return f'{self.name} is just walking around'
    
class Bengal(Cat):
    def sing(self, sounds):
        return f'{sounds}'

class Chartreux(Cat):
    def sing(self, sounds):
        return f'{sounds}'

class Siamese(Cat):
    def sing(self, sounds):
        return f'{sounds}'

all_cats = [Bengal('kiwi',3), Chartreux('tom',6), Siamese('mimi',2)]

sara_pets = Pets(all_cats)

sara_pets.walk()


#Exercise 2: Dogs
class Dog:
    def __init__(self, name, age, weight):
        self.name = name
        self.age = age
        self.weight = weight

    def bark(self):
        return f'{self.name} is barking.'
    
    def run_speed(self):
        return self.weight / self.age * 10
    
    def fight(self, other_dog):
        my_power = self.run_speed() * self.weight
        other_power = other_dog.run_speed() * other_dog.weight
        if my_power > other_power:
            return f"{self.name} won the fight!"
        elif my_power < other_power:
            return f"{other_dog.name} won the fight!"
        else:
            return "It's a tie!"
        

dog1 = Dog("Rex", 3, 30)
dog2 = Dog("Zaks", 2, 23)
dog3 = Dog("Ricky", 5, 40)

print(dog1.bark())
print(dog2.bark())
print(dog3.bark())

print(dog1.run_speed())
print(dog2.run_speed())
print(dog3.run_speed())

print(dog1.fight(dog2))


#Exercise 4: Family and Person Classes
class Person:
    def __init__(self, first_name, age):
        self.first_name = first_name
        self.age = age
        self.last_name = ""

    def is_18(self):
        return self.age >=18
    
    
class Family:
    def __init__(self, last_name):
        self.last_name = last_name
        self.members = []

    def born(self, first_name, age):
        self.age = age
        person = Person(first_name, self.age)
        person.last_name = self.last_name
        person.full_name = f"{first_name} {self.last_name}"
        self.members.append(person)
        return person
    
    def check_majority(self, first_name):
        for person in self.members:
            if person.first_name == first_name:
                if person.is_18():
                    print(f"You are over 18, your parents Jane and John accept that you will go out with your friends")
                else:
                    print("Sorry, you are not allowed to go out with your friends.")
                return

    def family_presentation(self):
        print(f'{self.last_name}')
        for person in self.members:
            print(f"- {person.first_name}, {person.age} years old")

smith_family = Family("Smith")
smith_family.born("John", 5)
smith_family.born("Jane", 20)
smith_family.born("Mike", 25)

# Test the method
smith_family.check_majority("John")    # Output: Sorry, you are not allowed to go out with your friends.
smith_family.check_majority("Jane")    # Output: You are over 18, your parents Jane and John accept that you will go out with your friends
smith_family.check_majority("Mike")    # Output: You are over 18, your parents Jane and John accept that you will go out with your friends
smith_family.check_majority("Sarah") 

smith_family.family_presentation()
