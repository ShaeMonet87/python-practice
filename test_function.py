
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
