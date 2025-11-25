#Challenge 1: Multiples of a Number
number = int(input("Enter the number : "))
length = int(input("Enter the lenght : "))
multiples = []
i=1
while len(multiples)<length:
    multiples.append(number*i)
    i+=1
print(multiples)


#Challenge 2: Remove Consecutive Duplicate Letters
word = input("Enter a word: ")
result = ""
for i in range(len(word)):
    if i == 0 or word[i] != word[i-1]:
        result += word[i]
print(result)