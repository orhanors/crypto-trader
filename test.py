test_dic = dict()

test_dic["name"] = "Orhan"
test_dic["surname"] = "Örs"
test_dic["address"] = {"line1":"Boyno",zip:27500}

if test_dic["address"]["line1"] is "Boyno":
    print("Not in")
else:
    print("I'm in")

print(test_dic)