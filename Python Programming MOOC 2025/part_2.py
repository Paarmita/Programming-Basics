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
age = int(input("What is your age? "))

if age < 0:
    print("That must be a mistake")
elif age < 5:
    print("I suspect you can't write quite yet...")
else:
    print(f"Ok, you're {age} years old")

#9
name = input("Please type in your name: ")

if name in ("Huey", "Dewey", "Louie"):
    print("I think you might be one of Donald Duck's nephews.")
elif name in ("Morty", "Ferdie"):
    print("I think you might be one of Mickey Mouse's nephews.")
else:
    print("You're not a nephew of any character I know of.")

#10
points = int(input("How many points [0-100]: "))
if points > 100: 
    print("Grade: impossible!")
elif points >= 90 and points <= 100:
    print("Grade: 5")
elif points >= 80 and points <= 89:
    print("Grade: 4")   
elif points >= 70 and points <= 79:
    print("Grade: 3")   
elif points >= 60 and points <= 69:
    print("Grade: 2")  
elif points >= 50 and points <= 59:
    print("Grade: 1")  
elif points >= 0 and points <= 49:
    print("Grade: fail")  
else:
    print("Grade: impossible!")

#11
number = int(input("Number: "))

if number % 3 == 0 and number % 5 == 0:
    print("FizzBuzz")
elif number % 3 == 0:
    print("Fizz")
elif number % 5 == 0:
    print("Buzz")

#12
yr = int(input("Please type in a year: "))

if (yr % 4 == 0 and yr % 100 != 0) or (yr % 400 == 0):
    print("That year is a leap year.")
else:
    print("That year is not a leap year.")

#13
a = input("1st letter: ")
b = input("2nd letter: ")
c = input("3rd letter: ")

if (a <= b <= c) or (c <= b <= a):
    middle = b
elif (b <= a <= c) or (c <= a <= b):
    middle = a
else:
    middle = c

print("The letter in the middle is", middle)

#14
value_of_gift = int(input("Value of gift:  "))

if value_of_gift > 5000 and value_of_gift < 25000:
    tax_amount = 100 + (value_of_gift - 5000)* 0.08
    print("Amount of tax:", tax_amount)
elif value_of_gift > 25000 and value_of_gift < 55000:
    tax_amount = 1700 + (value_of_gift - 25000)* 0.10
    print("Amount of tax:", tax_amount)
elif value_of_gift > 55000 and value_of_gift < 200000:
    tax_amount = 4700 + (value_of_gift - 55000)* 0.12
    print("Amount of tax:", tax_amount)
elif value_of_gift > 200000 and value_of_gift < 1000000:
    tax_amount = 22100 + (value_of_gift - 200000)* 0.15
    print("Amount of tax:", tax_amount)
elif value_of_gift > 1000000:
    tax_amount = 142100 + (value_of_gift - 1000000)* 0.17   
    print("Amount of tax:", tax_amount)
else:
    print("No tax!")

#15
while True:
    print("hi")
    code = input("Shall we continue? ")
    if code == "no":
        print("okay then")
        break

#16
from math import sqrt

while True:
    number = int(input("Please type in a number: "))

    if number == 0:
        print("Exiting...")
        break
    elif number < 0:
        print("Invalid number")
    else:
        print(sqrt(number))

#17
number = 5
print("Countdown!")
while True:
  print(number)
  number = number - 1
  if number == 0:
    break
print("Now!")

#18
password = input("Password: ")
while True:
  repeat_pass= input("Repeat password:")
  if repeat_pass == password:
    print("User account created!")
    break
  print("They do not match!")


#19
attempts = 0

while True:
    code = input("Please type in your PIN: ")
    attempts += 1

    if code == "4321":
        success = True
        break
    print("Wrong")

if success and attempts >1:
    print(f"Correct! It took you {attempts} attempts")
else:
    print("Correct! It only took you one single attempt!")

#20
year = int(input("Year: "))

next_year = year + 1

while True:
    if (next_year % 4 == 0 and next_year % 100 != 0) or (next_year % 400 == 0):
        print(f"The next leap year after {year} is {next_year}")
        break

    next_year += 1

#21
story = ""
previous = ""
first = True

while True:
    word = input("Please type in a word: ")

    if word == "end" or word == previous:
        break

    if first:
        story = word
        first = False
    else:
        story += " " + word

    previous = word

print(story)

#22
print("Please type in integer numbers. Type in 0 to finish.")

count = 0
total = 0
positive = 0
negative = 0

while True:
    number = int(input("Number: "))

    if number == 0:
        break

    count += 1
    total += number

    if number > 0:
        positive += 1
    else:
        negative += 1

mean = total / count

print("Numbers typed in", count)
print("The sum of the numbers is", total)
print("The mean of the numbers is", mean)
print("Positive numbers", positive)
print("Negative numbers", negative)
