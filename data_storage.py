import json
from calculations import *
def save_data(data, filename = ""):
    json_data = json.dumps(data)
    if filename =="":
        (day, month, year) = get_current_day_month_year()
        filename = 'data_' + str(day) +"_" +  str(month) + "_" +  str(year) + ".json"
    with open(filename, 'a') as file:
        file.write(json_data + "\n")


#def load_data(filename):
#    with open(filename, 'r') as file:
#        data = json.load(file)
#    return data
    
    
def load_data(filename):
    with open(filename, 'r') as file:
        data = {}

        #data_list = [json.loads(line.strip()) for line in file]
        for line in file:
            d = json.loads(line.strip())
            #print(d)
            key, value   = next(iter(d.items()))
            data[key] = value
            #print(line)
           
    return data