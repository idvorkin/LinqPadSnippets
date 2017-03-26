from datetime import date

zachBirthday = date(2010, 4, 22)
age = date.today() - zachBirthday
weeks = age.days / 7

print(f"Zach Age in weeks:{int(round(weeks))}")
