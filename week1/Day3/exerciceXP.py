#Exercise 1: Converting Lists into Dictionaries
keys = ['Ten', 'Twenty', 'Thirty']
values = [10, 20, 30]

dictionary = dict(zip(keys,values))
print(dictionary)


#Exercise 2: Cinemax #2
family = {
    "rick": 43, 
    'beth': 13, 
    'morty': 5, 
    'summer': 8
}
total_cost=0
for key,value in family.items():
    if 3<=value<=12:
        total_cost+=10
    elif value>12:
        total_cost+=15
print(total_cost)


#Bonus
names=[]
ages=[]  
while True:
    name = input("the name of the family member : ")
    age = int(input("the age of the family member : "))
    quit = input("print 'quit' to quit or enter to add members : ")
    names.append(name)
    ages.append(age)
    if quit == "quit":
        break
family_member = dict(zip(names,ages))
total_price=0
for key,value in family_member.items():
    if 3<=value<=12:
        total_price+=10
    elif value>12:
        total_price+=15
print(total_price)


#Exercise 3: Zara
brand = {
    'name': 'Zara',
    'creation_date': 1975,
    'creator_name': 'Amancio Ortega Gaona',
    'type_of_clothes': ['men', 'women', 'children', 'home'],
    'international_competitors': ['Gap', 'H&M', 'Benetton'],
    'number_stores': 7000,
    'major_color': {
        'France': 'blue',
        'Spain': 'red', 
        'US': ['pink', 'green']
    }
}

brand['number_stores'] = 2

clients = brand['type_of_clothes']
sentence = f"Zara serves {', '.join(clients[:-1])} and {clients[-1]} clients."
print(sentence)

brand['country_creation'] = 'Spain'
if 'international_competitors' in brand:
    brand['international_competitors'].append('Desigual')

del brand['creation_date']

print(brand['international_competitors'][-1])
print(brand['major_color']['US'])
print(len(brand.keys()))
print(brand.keys())

#Bonus
more_on_zara = {
    'creation_date' : 1975,
    'number_stores' : 7000
}

zara = brand | more_on_zara
print(zara)


#Exercise 4: Disney Characters   
users = ["Mickey", "Minnie", "Donald", "Ariel", "Pluto"]

dict_char_ind = dict(zip(users,range(0,len(users))))
print(dict_char_ind)

dict_ind_char = dict(zip(range(0,len(users)),users))
print(dict_ind_char)

sorted_users = sorted(users)
dict_ordered = dict(zip(sorted_users,range(0,len(sorted_users))))
print(dict_ordered)