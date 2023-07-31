import numpy as np

from data_storage import *
import time

models = {}
my_weights   = {
    #-2:[0.42982597, 0.7217528 ],
    #-1:[0.42982597, 0.7217528 ],
    #0:[0.42982597, 0.7217528 ],
    #1:[0.42982597, 0.7217528 ],
    #2:[0.42982597, 0.7217528 ],
    
    -2 :  [0.84515102, 0.26235059] ,
    -1 :  [1.21170167, 1.62549348] ,
    0 :  [-0.03799311,  1.47198369] ,
    1 :  [ 0.45523164, -0.0424256 ] ,
    2 :  [ 0.16498181, -0.12023374] ,

    }
#weights are :  [0.74387474 0.33611525]
#weights are :  [ 2.01488669 -0.42343241]
#weights are :  [-1.4683703   0.24792563]
#weights are :  [0.51748651 2.11914066]

def custom_format(arg):
    if isinstance(arg, float):
        return "{:.2f}".format(arg)
    elif isinstance(arg, dict):
        return {k: custom_format(v) for k, v in arg.items()}
    elif isinstance(arg, (list, tuple)):
        return type(arg)(custom_format(item) for item in arg)
    else:
        return arg

def print_custom(*args, **kwargs):
    formatted_args = [custom_format(arg) for arg in args]
    __builtins__.print(*formatted_args, **kwargs)
    
class BinaryClassifier:
    def __init__(self,num_features, weights):
        #print("num_features :", num_features)
        #self.weights = np.random.randn(num_features)
        self.weights = weights #my_weights
        #print("weights are : " ,  self.weights)
        self.bias = 0.0
        
    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def predict_proba(self, X):
        z = np.dot(X, self.weights) + self.bias
        return self.sigmoid(z)

    def predict(self, X, threshold=0.5):
        probabilities = self.predict_proba(X)
        return [1 if p >= threshold else 0 for p in probabilities]

    def update_model(self, X, y, learning_rate=0.01, time_weights=None, regularization_param=0.01):
        m = X.shape[0]
        predictions = self.predict_proba(X)
        if time_weights is not None:
            weighted_errors = time_weights * (predictions - y)
        else:
            weighted_errors = predictions - y
        gradient_weights = (np.dot(X.T, weighted_errors) + regularization_param * self.weights) / m
        gradient_bias = np.sum(weighted_errors) / m
        self.weights -= learning_rate * gradient_weights
        self.bias -= learning_rate * gradient_bias
        
    def update_model_unregulated(self, X, y, learning_rate=0.01, time_weights=None):
        m = X.shape[0]
        predictions = self.predict_proba(X)
        if time_weights is not None:
            weighted_errors = time_weights * (predictions - y)
        else:
            weighted_errors = predictions - y
        gradient_weights = np.dot(X.T, weighted_errors) / m
        gradient_bias = np.sum(weighted_errors) / m
        self.weights -= learning_rate * gradient_weights
        self.bias -= learning_rate * gradient_bias

def train_model(data_points, num_iterations,regularization_param=0,learning_rate = 0.01, weights = [.1,.1]):
    # Assuming data_points is a list of tuples (tick_value, label, time_fraction)
    # where label is 1 if it ended above the tick_threshold, otherwise 0.

    # Extract features (tick_value and time_fraction) and labels from the data_points.
    features = np.array([(data[0], data[1]) for data in data_points])
    labels = np.array([data[2] for data in data_points])

    # Normalize the features to help the convergence of SGD.
    features = (features - np.min(features, axis=0)) / (np.max(features, axis=0) - np.min(features, axis=0))
    #print(weights)
    # Create a binary classifier and train it using SGD with time-based weighting.
    classifier = BinaryClassifier(features.shape[1], weights)
    #num_iterations = 5000  # You can adjust the number of iterations as needed.
    time_weights = 1.0 - features[:, 1]  # Time weights are inverse of time_fraction
    for _ in range(num_iterations):
        if regularization_param ==0:
            classifier.update_model_unregulated(features, labels, learning_rate,time_weights=time_weights)
        else:
            classifier.update_model(features, labels, learning_rate,time_weights=time_weights,regularization_param = regularization_param)

    return classifier

def calculate_probability(model, current_indicative_value, time_left):
    # Prepare the input for prediction (using the current indicative value and time_fraction).
    time_fraction = time_left / 300.0
    input_data = np.array([current_indicative_value, time_fraction])

    # Predict the probability of ending above the given tick_threshold.
    probability = model.predict_proba(input_data.reshape(1, -1))

    # Add the current indicative value to the model for future updates.
    
    #add the following lines in order to update with each point.
    #extended_features = np.vstack((model.weights, input_data))
    #model.weights = extended_features

    return probability

def break_to_periods(data):
        #input data: data[time][name]["ind", etc] = value  from raw file.
        #data[end_time][name][epoch]["values", "prices"]  values = [ind, percent_left, final]  final is not known yet though.
        #prices = dictionary will all tick values/prices
        global interval
        ret ={}
        times = list(data.keys())
        #print("time: ", times[0])
        start = (int(times[0]) + interval -1) // interval * interval
        if len(data) ==1:
            start = 0
        end = start + interval
        curr = start
        #ret[end] = {}
        for k in times:
            #print(k)
            for name in data[k]:
                #name = list(data[k].keys())[0]
                #print(name, k, end)
                    #print("here", ret[end])
                if k > end:  #this period is over
                    while int(k) > end:  #need this in case the next interval is blank.  do not want empty keys.
                        end += interval
                    start = end-interval
                    #ret[end] = {}
                    #ret[end][name] = {}
                if int(k) >= start:
                    #print("setting now", end, name, k)
                    percent = (end-k)/interval
                    prices = data[k][name]
                    if not prices:
                        print("got it here 32432")
                        continue
                    values = [prices.pop("ind")]
                    values.append(percent)
                    #print(ret[end])
                    if not end in ret:
                        ret[end] = {}
                    if not name in ret[end]:
                        ret[end][name] = {}
                    ret[end][name][k] = {"values": values, "prices": prices}

        #print(len(ret))
        #print("it is", ret[1690423500])
        return ret        
        
def remove_bad_ticks(data,ticks):
    #input data  = values list of data.   i.e. data["tick1"] = .1192
    #return removed ticks.
    #ticks = []
    #for k in data:
    #    if "tick" in k:
    #        ticks.append(k)
    #skip bad ticks:  i.e. both high and low are "-"
    #print(ticks)
    #print(ticks)
    for k in ticks:
        n = k[4:]
        if data["t" + n + "low"] == "-" and data["t" + n + "high"] == "--":
            del data["t" + n + "low"]
            del data["t" + n + "high"]
            del data[k]
            continue
        if data["t" + n + "low"] == "-":
            data["t" + n + "low"] == 0
        if data["t" + n + "high"] == "-":
            data["t" + n + "high"] == 100
    if len(ticks) ==5:
        return data
    #print(data)
    #print("")
def rename_ticks(d, ticks):
    #input data:  a single epoch time, bad ticks removed.
    #input example:  data["tick1"] = .111
    #output:  renamed ticks.  ex:  data["t-1h"] = 99
    data = d["prices"]
    #print(d)
    ind = d['values'][0]
    sorted_ticks = list(sorted(ticks, reverse = True))
    ret = {}
    i = -2
    initial_value = 0
    for k in sorted_ticks:
        new_num = str(i)
        old_num = k[4:]
        if new_num == "0":
            initial_value = data["tick" + old_num ]  #used for normalizing ind value
        #ret["tick" + new_num] = data[k]  #actual tick value.  Not needed I think.
        ret["t" + new_num + "l"]  = data["t" + old_num + "low"]
        ret["t" + new_num + "h"]  = data["t" + old_num + "high"]
        i+=1
    i=0
    res = 0
    while 1:
        k1 = 'tick' + str(i)
        k2 = 'tick' + str(i+1)
        if k1 in data and k2 in data:
            res = data[k1] - data[k2]
            break
        i+=1
        if i>11:
            print("What?!!!! that can't be 4343243.  Waiting for instructions.")
            while 1:
                pass
    #print(ret)
    ret["res"] = res
    ret2 = {}
    ret2["values"] = d["values"]
    #print(ret)
    #print(d["values"][0], initial_value, res)
    #exit(0)
    ret2["values"][0] = (d["values"][0] - initial_value)/res  #1690609800
    ret2["prices"] = ret
    
    #print(ret2)
    return ret2
def normalize_data(data):
    #input:   data[end][name][epoch][values, prices] = list of values.
    #output:  data[end][name][epoch][values, proces, final, resolution] = normalized by tick.
    #output will also rename ticks, etc.
    ends = list(data.keys())
    for end in ends:
        for name in data[end]:
            #for epoch in data[end][name]: 
            #print(name)
            for k in list(data[end][name].keys()):
                    d = data[end][name][k]
                    if not d['prices']:
                        continue
                    ticks = []
                    #print(d)
                    for k2 in d['prices']:
                        if "tick" in k2:
                            ticks.append(k2)
                    #print(ticks)
                    #print(d)
                    #exit(0)
                    
                    d["prices"] = remove_bad_ticks(d["prices"],ticks)
                    #print(d["prices"])
                    if d["prices"]:
                        d = rename_ticks(d, ticks)
                        #d["values"][0] = (d["values"][0] - d["prices"]["tick0"])/d["prices"]["res"]  #normalize ind value
                    else:
                        #d["prices"]  = "HAHAHA"  #just for debug
                        pass
                    data[end][name][k] = d
                    if d['prices']:
                        #print(k,end,name, data[end][name][k])
                        pass
                        #exit(0)                
    for d in data:
        for n in data[d]:
            for epoch in data[d][n]:
                #print(data[d][n][epoch])
                pass

    i  = 0              
    for d in data:
 
        for name in data[d]:
            keys = list(data[d][name].keys())
            for epoch in keys:
                if not data[d][name][epoch]["prices"]:
                    del data[d][name][epoch]
                    #print("del")
    for d in data:
        keys = list(data[d].keys())
        for name in keys:
            if not data[d][name]:
                del data[d][name]
    keys = list(data.keys())            
    for d in keys:
        if not data[d]:
            del data[d]
            

    #exit(0)
    return data      
                
                
        
def set_final(data): 
    #input complete data : data[end][name][epoch]["prices", "values"] = list.
    #set final value of time period. 
    for end in data:
        for name in data[end]:
            t = list(data[end][name].keys())[-1]
            final = data[end][name][t]["values"][0]
            for t2 in data[end][name]:
                data[end][name][t2]["values"].append(final)
                #print(end, name, t2, final, t) #check out 1690609781, 1690609800
    return data
    
                   
def remove_bad_data(data):
    #remove the bad periods I don't want to use.
    # current requirement:  no more than .01 from beginning or end (need to know beginning and end values)
    #take full data:  data[end][name][epoch]["prices","values"] = list.
    #return:  same as input but remove the bad end times.
    good_data = {}
    threshold = .01# 3 seconds for 5 minute stock.
    for d in data:
        good_ending  = {}
        for name in data[d]:
            #print(name)
            #if name=="USD/JPY":
            #    print(name)
            #name = list(data[d].keys())[0]
            first = list(data[d][name].keys())[0]
            last = list(data[d][name].keys())[-1]
            #print(data[d][name][first]["values"][1], data[d][name][last]["values"][1], d)
            if data[d][name][first]["values"][1] > 1-threshold and data[d][name][last]["values"][1] < threshold:  #it's a good periods
                good_ending[name] = data[d][name]
            else:
                #print("nope, not doig it here", d)
                pass
                #if name != "USD/JPY":
                #    print(name, data[d][name][first]["values"][1], data[d][name][last]["values"][1])
        if good_ending:
            good_data[d] = good_ending
    return good_data
        
def fix_data_types(data):  #for now, epoch needs to be an int.
    ret = {}
    for k in data:
        ret[int(k)] = data[k]
    return ret
    
def format_single_data(data):  #pull directly from a live run.  Convert to normalized.
    #ret[0] = {}
    ##t = list(data.keys()][0]
    #name = list(data[t].keys())[0]
    #ind = data[t][name]['ind']
    
    #ret[0][name] = {}
    #ret[0][name][t] = {}
    #d = load_data("data/data_27_7_2023.json")
    #t = list(d.keys())[0]
    #data = {}
    #data[t] = d[t]
    #print("starting", data)
    data = fix_data_types(data)
    #print("fixed", data)
    data = break_to_periods(data)
    #print("broke",data)
    data = normalize_data(data)
    #print("normal",data)
    return data
    
def load_formatted_data(file):
    #load the data into the format of data[end_time][name]["final","ind", "tick_resolution", t_-2high, t_-1,low, etc.
    data = load_data(file)  #return data[end][name][epoch]["ind", etc] straight from the file.

    data = fix_data_types(data)
    #print("loaded")
    #print_first(data)
    data = break_to_periods(data)# return periods with data[end][name][epoch][values, prices] = a list of values
    #print("broke")
    #print_first(data)
    #print("")
    #print(data[1690509600])

    data = remove_bad_data(data)

    data = normalize_data(data)

    #print("normal")
    #print_first(data)
    #exit(0)
    data = set_final(data)
    #print("final")
    #print_first(data)
    #exit(0)

    #print("done")
    #print_first(data)

    return data
 
    
def print_first(data):  #take any dictionary.  print the firt items
    key = list(data.keys())[0]
    #print(data.keys())
    print(key)
    print(key,data[key])

def train_model(data_points, num_iterations,regularization_param=0,learning_rate = 0.01, weights = [.1,.1]):
    # Assuming data_points is a list of tuples (tick_value, label, time_fraction)
    # where label is 1 if it ended above the tick_threshold, otherwise 0.

    # Extract features (tick_value and time_fraction) and labels from the data_points.
    features = np.array([(data[0], data[1]) for data in data_points])
    labels = np.array([data[2] for data in data_points])

    # Normalize the features to help the convergence of SGD.
    features = (features - np.min(features, axis=0)) / (np.max(features, axis=0) - np.min(features, axis=0))

    # Create a binary classifier and train it using SGD with time-based weighting.
    classifier = BinaryClassifier(features.shape[1], weights)
    #num_iterations = 5000  # You can adjust the number of iterations as needed.
    time_weights = 1.0 - features[:, 1]  # Time weights are inverse of time_fraction
    for _ in range(num_iterations):
        if regularization_param ==0:
            classifier.update_model_unregulated(features, labels, learning_rate,time_weights=time_weights)
        else:
            classifier.update_model(features, labels, learning_rate,time_weights=time_weights,regularization_param = regularization_param)

    return classifier

def create_model_old(data, name, tick, num_iterations, regulated, learning_rate):
    new_data = []
    for period in data:
        if not name in data[period]:
            continue
        for epoch in data[period][name]:
            l = data[period][name][epoch]['values']
            v = 0
            if l[2] > tick:
                v = 1
            n == [l[0],l[1], v]
            data.append(n)

def create_model(d,name,tick,num_iterations, regulated, learning_rate, weights):
    
    data = []
    for key in d:
        if not name in d[key]:
            print(d[key])
            print("well, this is a problems :", name, key)
            
            exit(0)
        for epoch in d[key][name]:
            
            l = d[key][name][epoch]['values']
        
            #print(l)
            v = 0
            if l[2] > tick:
                v = 1
            else:
                v = 0
                
            n = [l[0],l[1],v]
            #print(l, v, tick, epoch)
            data.append(n)
    #data = data[int((1-percent)*len(data)):]
    for d in data:
        #print(d)
        pass
    #print(len(data))

    return train_model(data,num_iterations, regulated, learning_rate, weights[tick])  #data, num_iterations,
    
def create_models(test_data,name, num_iterations=500, regulated = 0, learning_rate =.5, weights = [.1,.1]):    
    #models["EUR/USD"][1] = this_model
    #names = set()
    #for t in test_data:
    #    for k in test_data[t]:
    #        names.add(k)
    #print(names)
    #for name in names:
    models = {}
    for tick in [-2,-1,0,1,2]:
        #print("Creating for tick: ", tick)
        models[tick] = create_model(test_data,name, tick, num_iterations,regulated, learning_rate, weights)
        #print(name, tick)

    return models   
def second_attempt_buy(name,test_data,epoch,tick,threshold):
    model = models[name]
    for t in test_data:
        if t> epoch + 5: #waited long enough.
            (buy, details) = should_buy_sell(name,test_data[t], t,tick, threshold)    
            return (buy, details,t)
    return (0, {},epoch+5)
    
def should_buy_sell(name,dic, epoch,tick,threshold):
    global interval, models
    #print(models)
    #print(name)
    model = {}
    try:
        model = models[name][tick]
    except:
        print(models)
        print(name, tick)
        print("error 13423")
        while 1:
            pass
    final = -100
    if len(dic['values'])>2:
        final = dic["values"][2]
    current_indicative_value = dic["values"][0]
    end_time = (int(epoch) + interval -1) // interval * interval + interval
    #time_left_seconds = end_time - int(epoch)
    time_left_seconds = dic["values"][1]
    probability = calculate_probability(model, current_indicative_value, time_left_seconds)[0]
    #print(probability)
    cost_buy = dic["prices"]["t" + str(tick) + "h"]
    cost_sell = 100 - dic["prices"]["t" + str(tick) + "l"]
    prof_buy = probability*100 -cost_buy
    prof_sell = (1-probability)*100 -cost_sell
    if prof_buy > 40 or prof_sell > 40:
        #prof_buy = prof_sell = 0
        pass
    result = 0
    details = {
        "buy": cost_buy,
        "sell": cost_sell,
        "prob": probability,
        "ind": current_indicative_value,
        "left": time_left_seconds,
        "l2":  dic["values"][1],
        "tick": tick,
        "final": final,
        "epoch": epoch,
        "endtime": end_time,
    }

    if (prof_buy > threshold and prof_sell > threshold):
        print("That isn't possible!!!!!")
    if (prof_buy > threshold):
        #print("")
        #print(cost)
        #print(probability,time_left_seconds, current_indicative_value)
        profit = -1 *cost_buy -1 #1 dollar just to buy it.
        if final > tick:
            result = 1
        if result == 1:
            profit +=99 #only get 99 for winning
        details["profit"] = profit
        details["result"] = result
        details["expected"] = prof_buy
        

        #print(1, details)
        #exit(0)
        return (1, details)
    if (prof_sell > threshold):
        profit = -1 * cost_sell
        if final >= tick:
            result = 1
        if result == 0:
            profit += 99 # only get 99 for winning.
        details["profit"] = profit
        details["result"] = result
        details["expected"] = prof_sell
        return (-1, details)
    return (0, details) 

def setup_models(training_data, names, num_iterations, regulated, learning_rate,weights):
    global models
    models = {}
    for name in names:
        models[name] = create_models(training_data, name, num_iterations, regulated, learning_rate,weights)
def run_debug_test(test_data, names, threshold, weights):
    total_profit = 0
    num = 0
    wait_for = 0
    prev = 0
    #global models
    #models = {}
    #for name in names:
    #    models[name] = create_models(training_data,name, num_iterations=1000, regulated = 0, learning_rate =.1, weights = weights)
    for d in test_data:  #for each period.
        bought = {}  #make sure I don't buy more than 1 of each.
        for name in names:
            #print(test_data[d])
            if not name in test_data[d]:
                continue
            bought[name] = {}
            for epoch in test_data[d][name]:
                if prev > epoch:
                    print("out of order", prev, epoch)
                    exit(0)
                else:
                    prev = epoch
                dic = test_data[d][name][epoch]
                
                for tick in range(-2,3):
                    if not tick in bought[name]:
                        bought[name][tick] = 0
                    if epoch < wait_for:
                        break
                    model = models[name][tick]
                    (buy, details) = should_buy_sell(name,dic, epoch,tick, threshold)
                    
                    if buy != 0:
                        if bought[name][tick] >0 and buy ==1:
                            continue  #already bought it
                        if bought[name][tick] < 0 and buy == -1:
                            continue
                        #print("iterval is: ", interval)
                        #wait_for = epoch + 5  #assume it takes 5 seconds for it to finish.
                        (buy, details, t) = second_attempt_buy(name,test_data[d][name],epoch,tick,threshold) #2 for second attempt.
                        wait_for = t+5
                        if buy !=0:
                            bought[name][tick] += buy
                           
                            #print_custom(buy, details)
                            total_profit += details["profit"]
                            num+=1
                    else:
                        #print("skip")
                        pass
    #print("total bought:", num)
    return total_profit
def load_formatted_dates(files):

    test_data = {}
    for f in files:
        test_data.update(load_formatted_data("data/" + f + ".json"))
    return test_data
           
def do_best_known_run(name):  #not really used.  Just saved the code.
    training_file = "data/data_27_7_2023.json"
    testing_file = "data/data_28_7_2023.json"
    test_data = load_formatted_data(testing_file)
    #test_data = load_formatted_dates(["data_27_7_2023","data_28_7_2023"])
    print("good periods", len(test_data))
    training_data = load_formatted_data(training_file)
    for d in test_data:
        d2 = {}
        d2[d] = test_data[d]
        break
    test_data = d2

        

    t1 = time.time()
    print("starting at :", t1)
    #profit = run_debug_test(test_data, models, names = ["EUR/USD"], threshold = 30)
    profit = run_debug_test(test_data, names = ["USD/JPY"], threshold = 30, weights = my_weights)
    print(profit)
    print("ending at :", time.time() -t1)

    exit(0)



interval = 5*60
#weights = np.random.randn(2)
