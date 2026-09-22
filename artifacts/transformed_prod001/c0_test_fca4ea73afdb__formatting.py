def calculate_bmi(lst):
    s, w, h = (int(lst[0]), float(lst[1]), float(lst[2]))
    BMI = w / (h**2)

    print("BMI: ", BMI)

    if BMI < 18.5:
        print("Underweight")
    elif 18.5 <= BMI < 25:
        print("Normal weight")
    elif 25 <= BMI < 30:
        print("Overweight")
    else:
        print("Obese")


# Example usage:
lst = [1, 70, 1.75]
calculate_bmi(lst)
