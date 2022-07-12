first_number = input("Enter your first number :")
second_number = input("Enter your second number :")


percent_diff = (((float(second_number) - float(first_number))/float(first_number)) * 100)
prefix = "+" if percent_diff > 0 else ''
print(f'Difference is {prefix}{percent_diff:.2f}%')

# Use alpha x2 to do mover updates every 30 mins/hour