

def make_change(cents):
    quarters = cents // 25
    remaining_cents = cents - quarters * 25
    dimes = remaining_cents // 10
    remaining_cents = remaining_cents - dimes * 10
    nickels = remaining_cents // 5
    pennies = remaining_cents - nickels * 5
    return quarters, dimes, nickels, pennies


cents = int(input("How many cents of change? ")) #user input for the amount of change in cents

quarters, dimes, nickels, pennies = make_change(cents) #call function to calculate the number of coins needed for the given amount of change

if quarters == 1:
    quarter_text = "quarter"
else:
    quarter_text = "quarters"

if dimes == 1:
    dime_text = "dime"
else:
    dime_text = "dimes"

if nickels == 1:
    nickel_text = "nickel"
else:
    nickel_text = "nickels"

if pennies == 1:
    penny_text = "penny"
else:
    penny_text = "pennies" 

print(
    quarters, quarter_text + ",",
    dimes, dime_text + ",",
    nickels, nickel_text + ", and",
    pennies, penny_text + "."
) #print the results



