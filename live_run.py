import time
#print("T1")
from prediction import *
#print("T2")
from drivers import *
#print("T3")
import numpy as np  #just for debug run loop with random value.
from calculations import *

#data = {}
#data = format_single_data(data)
#exit(0)


simu_run = False #do I open websites?
debug_run = False #do I use live or debug data?
print(simu_run)
if not simu_run:
    open_browser("https://platform.nadex.com", profile, path, headless)  #assume that it is already logged in.
    open_stocks()
    print("stocks opened")
#need to get the most recent data for each.
training_file = "data/data_27_7_2023.json"
testing_file = "data/data_28_7_2023.json"



training_data = load_formatted_data(training_file)


print("training_data", training_file)


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
    
#parameters of models
names =["EUR/USD"]  #"USD/JPY"
num_iterations = 1000
regulated = 0
learning_rate = .1
weights = my_weights


if debug_run:
#debug run on data
    testing_data = load_formatted_data(testing_file)
    print("testing_data", testing_file)
    max_profit = -10000
    
    for i in range(100):
        weights = {}
        for k in [-2,-1,0,1,2]:
            weights[k] = np.random.randn(2)
        #print(weights)
        #create_models(training_data,name = "EUR/USD", num_iterations=1000, regulated = 0, learning_rate =.1, weights = weights)
        #print("In the loop now", i)
        setup_models(training_data, names, num_iterations, regulated, learning_rate,weights)
        profit = run_debug_test(testing_data, names , threshold = 30, weights = weights)
        #print(profit, weights)
        if profit > max_profit:
            print(profit)
            for k in weights:
                print(k, ": ", weights[k], ",")
            max_profit = profit


#live run.
if not debug_run:
    total_profit = 0
    setup_models(training_data, names, num_iterations, regulated, learning_rate,my_weights)
    bought = {}
    
    while 1:
        data = check_prices()
        profit = 0
        curr_profit = 0
        #print(data)
        #data = {}
        threshold = 30  #want to buy a lot for now.
        data = format_single_data(data)
        if data == {}:
            curr_profit += determine_win_lose(data, bought)  #take the name and tick values along with current data.  Return amount won.
            total_profit += curr_profit
            if(curr_profit!=0):
                print(get_time(), "Total: ", total_profit, "Current: ", profit)
        
        
        
            print("resetting period bought")
            
            bought = {}
        for d in data:  #I have these loops for ease.  They each only have one key except for name and tick
            #for name in data[d]:
                name = "EUR/USD"
                if not name in bought:
                    
                    bought[name] = {}
                    
                if not name in data[d]:
                    continue
                for t in data[d][name]:
                    for tick in range(-2,3):
                        if not tick in bought[name]:
                            bought[name][tick] = 0
                        (buy, details) = should_buy_sell(name, data[d][name][t], t, tick, threshold)
                        #print(buy, details)
                        if buy:
                            if buy ==-1 and bought[name][tick] <0:
                                continue
                            if buy ==1 and bought[name][tick] > 0:
                                continue
                            temp = bought[name][tick]
                            #print(bought[name][tick], name, tick)
                            bought[name][tick] += buy
                            t1 = time.time()
                            v = get_second_level_price(buy, name, tick) #opens the stock and waits to just click on it.
                            t2 = time.time()
                            if v ==-1:
                                bought[name][tick] -= buy
                                break
                            curr_profit -= float(v)
                            print("")
                            print("it took", t2-t1)
                            print("price: ",  v, "func: ",buy, "name: ", name, "tick: ", tick,  "bought: ", bought[name][tick], "temp: ", temp)
                            time.sleep(1)
                            break

                            #live_buy_stock(buy, name, tick)

        #profit = live_single_data_run()  #make a decision 
    
    