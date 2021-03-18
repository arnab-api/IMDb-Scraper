def getPeopleDict(people_arr):
    key = None
    people_dict = {}
    for people in people_arr:
        if(len(people) <= 1):
            continue
        if(":" in people):
            key = people[0:-1]
            people_dict[key] = []
        else:
            people_dict[key].append(people)
    return people_dict

people_arr = ['Directors:', 'Anthony Russo', ',', 'Joe Russo', '', '|', 'Stars:', 'Tom Holland', ',', 'Ciara Bravo', ',', 'Jack Reynor', ',', 'Forrest Goodluck', '']

print(getPeopleDict(people_arr))
print(" ".join(people_arr))