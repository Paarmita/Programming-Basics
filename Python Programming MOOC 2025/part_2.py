#1
number = int(input("Please type in a number: "))
if number>100 :
    print("The number was greater than one hundred")
    number = number - 100 
    print("Now its value has decreased by one hundred")
    print(f"Its value is now {number}")
print(f"{number} must be my lucky number!")
print("Have a nice day!")

#2
# Write your solution here
word = input("Please type in a word: ")
length = len(word)
if length == 1:
    print("Thank you!")
else:
    print(f"There are {length} letters in the word {word}")
    print("Thank you!")

#3
number = float(input("Please type in a number: "))
print("Integer part:", int(number))
decimal_part = number - int(number)
print("Decimal part:", float(decimal_part))

#4
age = int(input("How old are you? "))

if age >= 18:
    print("You are of age!")
else:
    print("You are not of age!")

#5
num1 = int(input("Please type in the first number: "))
num2 = int(input("Please type in the another number: "))

if num1 > num2:
    print(f"The greater number was: {num1}")
elif num2 > num1:
    print(f"The greater number was: {num2}")
elif num2 == num1:
    print("The numbers are equal!")

#6
print("Person 1:")
name1 = input("Name: ")
age1 = int(input("Age: "))
print("Person 2:")
name2 = input("Name: ")
age2 = int(input("Age: "))
if age1 > age2:
    print(f"The elder is {name1}")
elif age2 > age1:
    print(f"The elder is {name2}")
elif age2 == age1:
    print(f"{name1} and {name2} are the same age")

#7
name1 = input("Please type in the 1st word: ")
name2 = input("Please type in the 2nd word: ")
if name1 == name2:
    print("You gave the same word twice.")
elif name1 > name2:
    print(f"{name1} comes alphabetically last.")
else:
    print(f"{name2} comes alphabetically last.")

#8
