#Exercise 1: Cats
class Cat():
    def __init__(self, name, age):
        self.name = name
        self.age = age

cat1 = Cat("Kitty" , 6)
cat2 = Cat("Mimi" , 2)
cat3 = Cat("Tom" , 5)

def oldestCat(a,b,c):
    max = a.age
    if b.age>max:
        print(f'The oldest cat is {b.name} and is {b.age} years old.')
    elif c.age>max:
        print(f'The oldest cat is {c.name} and is {c.age} years old.')
    else:
        print(f'The oldest cat is {a.name} and is {a.age} years old.')

oldestCat(cat1, cat2, cat3)


#Exercise 2 : Dogs
class Dog():
    def __init__(self, name, height):
        self.name = name
        self.height = height

    def bark(self):
        print(f'{self.name} goes woof!')

    def jump(self):
        print(f'{self.name} jumps {self.height*2} cm height!')

davids_dog = Dog("Diblo" , 100)
sarahs_dog = Dog("Karla" , 50)

print(f"the name of David's dog is {davids_dog.name} and he is {davids_dog.height} cm height!")
print(f"the name of Sarah's dog is {sarahs_dog.name} and she is {sarahs_dog.height} cm height!")

davids_dog.bark()
davids_dog.jump()
sarahs_dog.bark()
sarahs_dog.jump()

if davids_dog.height > sarahs_dog.height:
    print(f"David's dog '{davids_dog.name}' is heigher than Sarah's dog '{sarahs_dog.name}' !")
else :
    print(f"Sarah's dog '{sarahs_dog.name}' is heigher than David's dog '{davids_dog.name}' !")


#Exercise 3 : Who’s the song producer?
class Song():
    def __init__(self, lyrics):
        self.lyrics = lyrics

    def sing_me_a_song(self):
        for i in self.lyrics:
            print(i, end=" ")

sweater_weather = Song([
    "And all I am is a man",
    "I want the world in my hands",
    "I hate the beach but I stand",
    "In California with my toes in the sand.\n"
])

sweater_weather.sing_me_a_song()


#Exercise 4 : Afternoon at the Zoo
class Zoo():
    def __init__(self, zoo_name, animals=[]):
        self.zoo_name = zoo_name
        self.animals = animals

    def add_animal(self, new_animal):
        if new_animal not in self.animals:
            self.animals.append(new_animal)
    
    def get_animals(self):
        print(f'animals exist are :')
        for animal in self.animals:
            print(animal)
    
    def sell_animal(self, animal_sold):
        if animal_sold in self.animals:
            print(f'Selling : {animal_sold}')
            self.animals.remove(animal_sold)
    
    def sort_animals(self):
        sorted_animals = sorted(self.animals)

        animals_dict = {}
        for animal in sorted_animals:
            first_letter = animal[0]
            if first_letter not in sorted_animals:
                animals_dict[first_letter] = []
            animals_dict[first_letter].append(animal)
        print(animals_dict)

    def add_animal(self, *new_animals):
        for animal in new_animals:
            if animal not in self.animals:
                self.animals.append(animal)
                print(f'Adding: {animal}')
            else:
                print(f'{animal} is already in the zoo!')


ainsbaa_zoo = Zoo("zoo_AinSbaa")

ainsbaa_zoo.add_animal("lion", "wolf", "aligator", "bunney")
ainsbaa_zoo.add_animal("giraffe")
ainsbaa_zoo.add_animal("tiger")
ainsbaa_zoo.add_animal("monkey")

ainsbaa_zoo.get_animals()

ainsbaa_zoo.sell_animal("giraffe")

ainsbaa_zoo.get_animals()

ainsbaa_zoo.sort_animals()
