from exerciseXP import Dog
import random

class PetDog(Dog):
    def __init__(self, name, age, weight, trained=False):
        # Call the parent class (Dog) constructor
        super().__init__(name, age, weight)
        self.trained = trained
    
    def train(self):
        print(self.bark())
        self.trained = True

    def play(self, *dogs):
        dog_names = [self.name]  # Start with current dog's name
        for dog in dogs:
            dog_names.append(dog.name)
        print(f"{', '.join(dog_names)} all play together")

    def do_a_trick(self):
        tricks = ["does a barrel roll", "stands on his back legs", "shakes your hand", "plays dead"]
        
        if self.trained:
            random_trick = random.choice(tricks)
            print(f"{self.name} {random_trick}")
        else:
            print(f"{self.name} is not trained yet! Use the train() method first.")

# Test the fixed code
dog1 = PetDog("Buddy", 3, 15)
dog2 = PetDog("Max", 2, 12)
dog3 = PetDog("Bella", 4, 18)

print(f"Is Buddy trained? {dog1.trained}")
dog1.train()
print(f"Is Buddy trained now? {dog1.trained}")

dog1.play(dog2, dog3)

dog1.do_a_trick()  
dog2.do_a_trick()

dog2.train()
dog2.do_a_trick()