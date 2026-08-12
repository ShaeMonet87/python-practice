
currentTemp = (input("What is the current temperature in Fahrenheit? "))

print(currentTemp)

print (currentTemp.isdigit())

def convertToCelcius(temp):
   return (temp - 32) * 5/9

def convertStringTempToCelcius(temp):

   if temp.isdigit():
      temp = int(temp)
      return convertToCelcius(temp)

temp_in_cel = convertStringTempToCelcius(currentTemp)
print(temp_in_cel)

def make_change(cents):
    quarters = cents // 25
    remaining_cents = cents - quarters * 25
    dimes = remaining_cents // 10
    remaining_cents = remaining_cents - dimes * 10
    nickels = remaining_cents // 5
    pennies = remaining_cents - nickels * 5
    return quarters, dimes, nickels, pennies

