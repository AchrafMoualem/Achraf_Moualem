#Daily challenge: Old MacDonald’s Farm
class Farm():
    def __init__(self, farm_name):
        self.farm_name = farm_name
        self.animals = {}  

    def add_animal(self, animal_type, count=1):
        if animal_type in self.animals:
            self.animals[animal_type] += count
        else:
            self.animals[animal_type] = count

    def get_info(self):
        animal_list = []
        for animal, count in self.animals.items():
            animal_list.append(f"{animal}: {count}")
        return f'{self.farm_name} has these animals: {", ".join(animal_list)} \nE-I-E-I-0!'
    
    def get_short_types(self):
        return sorted(list(self.animals.keys()))
    
    def get_short_info(self):
        animal_types = self.get_short_types()
        animal_list = []
        
        for animal in animal_types:
            count = self.animals[animal]
            if count > 1:
                animal_list.append(f"{animal}s")  # Add 's' for plural
            else:
                animal_list.append(animal)
        
        # Format the string with proper grammar
        if len(animal_list) == 1:
            animals_str = animal_list[0]
        elif len(animal_list) == 2:
            animals_str = f"{animal_list[0]} and {animal_list[1]}"
        else:
            animals_str = f"{', '.join(animal_list[:-1])} and {animal_list[-1]}"
        
        return f"{self.farm_name}'s farm has {animals_str}."
    
    def add_animals(self, **animals):
        for animal_type, count in animals.items():
            self.add_animal(animal_type, count)

            
    


ainsbaa = Farm("ainsbaa")
ainsbaa.add_animal("lion")
ainsbaa.add_animal("monkey")
ainsbaa.add_animal("lion")
ainsbaa.add_animal("tiger")
ainsbaa.add_animal("lion")
ainsbaa.add_animal("giraffe")
ainsbaa.add_animal("monkey")

print(ainsbaa.get_info())
print(ainsbaa.get_short_types())
print(ainsbaa.get_short_info())

ainsbaa.add_animals(cow=5, sheep=3, chicken=10)
print(ainsbaa.get_short_info())

