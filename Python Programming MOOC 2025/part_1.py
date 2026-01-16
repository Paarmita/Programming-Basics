#Introduction to Programming course (BSCS1001, 5 ECTS) and the Advanced Course in Programming (BSCS1002, 5 ECTS) from the Department of Computer Science at the University of Helsinki.
#https://programming-25.mooc.fi/

#1
print(":-)")

#2
# Fix the code
print("Aapo")
print("Eero")
print("Juhani")
print("Lauri")
print("Simeoni")
print("Timo")
print("Tuomas")

#3
print("Row, row, row your boat,")
print("Gently down the stream.")
print("Merrily, merrily, merrily, merrily,")
print("Life is but a dream.")

#4
print("Minutes in a year:")
print(365*24*60) # 365 days, 24 hours in each day, 60 minutes in each hour

#5
print('print("Hello there!")')

#6
name = input("What is your name? ")
print(name)
print(name)

#7
name = input("What is your name? ")
print("!" + name + "!" + name + "!")

#8
name = input("Given name:")
family_name = input("Family name: ")
street_address = input("Street address: ")
city_postal_code = input("City and postal code: ")
print(name + " " + family_name)
print(street_address)
print(city_postal_code)

#9
name = input("Please type in a name:  ")
year = input("Please type in a year: ")

print(name + " is a valiant knight, born in the year " + year + ". One morning " + name + " woke up to an awful racket: a dragon was approaching the village. Only " + name + " could save the village's residents." )

#10
name = "Tim Tester"
age = 20
skill1 = "python"
level1 = "beginner"
skill2 = "java"
level2 = "veteran"
skill3 = "programming"
level3 = "semiprofessional"
lower = 2000
upper = 3000

print(f"my name is {name}, I am {age} years old \n\nmy skills are \n - {skill1} ({level1}) \n - {skill2} ({level2}) \n - {skill3} ({level3}) \n\nI am looking for a job with a salary of {lower}-{upper} euros per month")

#11
x = 27
y = 15

print(f"{x} + {y} = {x + y}")
print(f"{x} - {y} = {x - y}")
print(f"{x} * {y} = {x * y}")
print(f"{x} / {y} = {x / y}")

#12
print(5, end="")
print(" + ", end="")
print(8, end="")
print(" - ", end="")
print(4, end="")
print(" = ", end="")
print(5 + 8 - 4, end="")

#13
number = int(input("Please type in a number: "))
times = 5 * number 
print(f"{number} times 5 is {times}")

#14
name = input("What is your name? ")
year = int(input("Which year were you born? "))
print(f"Hi {name}, you will be {2021 - year} years old at the end of the year 2021")

#15
# Write your solution here
days = int(input("How many days? "))
print(f"Seconds in that many days: {days * 24 * 60 * 60}")

#16
# Fix the code
number1 = int(input("Please type in the first number: "))
number2 = int(input("Please type in the second number: "))
number3 = int(input("Please type in the third number: "))

product = number1 * number2 * number3

print(f"The product is {product}")

#17
number1 = int(input("Number 1: "))
number2 = int(input("Number 2: "))

print(f"The sum of the numbers: {number1 + number2}")
print(f"The product of the numbers: {number1 * number2}")

#18
number1 = int(input("Number 1: "))
number2 = int(input("Number 2: "))
number3 = int(input("Number 3: "))
number4 = int(input("Number 4: "))
sum = number1 + number2 + number3 + number4
print(f"The sum of the numbers is {sum} and the mean is {sum / 4}")

#19
frequency = int(input("How many times a week do you eat at the student cafeteria? "))
price = float(input("The price of a typical student lunch? "))
cost = float(input("How much money do you spend on groceries in a week? "))
weekly = frequency * price + cost
print(f"\nAverage food expenditure: \nDaily: {weekly / 7} euros \nWeekly: {weekly} euros")

#20
num = int(input("How many students on the course? "))
group_size = int(input("Desired group size? "))

groups = num // group_size

# If there is a remainder, add one more group
if num % group_size != 0:
    groups += 1
print(f"Number of groups formed: {groups}")

#21
number = int(input("Please type in a number: "))

if number == 1984:
    print("Orwell")

#22
number = int(input("Please type in a number: "))

if number < 0:
    print(f"The absolute value of this number is {number * -1}")

if number >= 0:
    print(f"The absolute value of this number is {number}")

#23
name = input("Please tell me your name: ")
if name != "Jerry":
    portion = int(input("How many portions of soup? "))
    print(f"The total cost is {portion * 5.90} \nNext please!")

if name == "Jerry":
    print(f"Next please!")

#24
number = int(input("Please type in a number: "))
if number < 1000 :
    print(f"This number is smaller than 1000")
if number < 100 :
    print(f"This number is smaller than 100")
if number < 10:
    print(f"This number is smaller than 10")
print(f"Thank you!")


#25
number1 = int(input("Number 1: "))
number2 = int(input("Number 2: "))
operation = input("Operation: ")

if operation == "add" :
    print(f"\n{number1} + {number2} = {number1 + number2}")
if operation == "multiply" :
    print(f"\n{number1} * {number2} = {number1 * number2}")
if operation == "subtract" :
    print(f"\n{number1} - {number2} = {number1 - number2}")

#26
fahrenheit = float(input("Please type in a temperature (F): "))
celsius = (fahrenheit - 32) * 5 / 9
if celsius < 0 :
    print(f"{fahrenheit} degrees Fahrenheit equals {celsius} degrees Celsius \nBrr! It's cold in here!")
if celsius >= 0 :
    print(f"{fahrenheit} degrees Fahrenheit equals {celsius} degrees Celsius")

#27
wage = float(input("Hourly wage: "))
worked = float(input("Hours worked: "))
week_day = input("Day of the week: ")

if week_day == "Sunday" :
    print(f"Daily wages: {2 * wage * worked} euros")
if week_day != "Sunday" :
    print(f"Daily wages: {wage * worked} euros")

#28
points = int(input("How many points are on your card? "))
if points < 100:
    points *= 1.1
    print("Your bonus is 10 %")
else:
    points *= 1.15
    print("Your bonus is 15 %")

print("You now have", points, "points")

#29
print("What is the weather forecast for tomorrow?")

temp = int(input("Temperature: "))
rain = input("Will it rain (yes/no): ")

print("Wear jeans and a T-shirt")

if temp <= 20:
    print("I recommend a jumper as well")
if temp <= 10:
    print("Take a jacket with you")
if temp <= 5:
    print("Make it a warm coat, actually")
    print("I think gloves are in order")

if rain == "yes":
    print("Don't forget your umbrella!")

#30
# Let's take the square root of math-module in use
from math import sqrt

# Note that the square root can also be calculated using power.
# sqrt(9) is equivalent to 9 ** 0.5
a = int(input("Value of a: "))
b = int(input("Value of b: "))
c = int(input("Value of c: "))
x = (-b + sqrt(b*b-4*a*c))/(2*a)
y = (-b - sqrt(b*b-4*a*c))/(2*a)

print(f"The roots are {x} and {y}")
