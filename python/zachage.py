#!/usr/bin/env python3
from datetime import date

zachBirthday = date(2010, 4, 22)
age = date.today() - zachBirthday
ageInWeeks = age.days / 7

print(f"Zach Age in weeks:{round(ageInWeeks):d}")
