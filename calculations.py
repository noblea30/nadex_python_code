from datetime import datetime, timedelta, timezone

def parse_data(s,name,data):
  #print(s)
  sp = name.split()
  st = sp[0].strip()
  ind = float(sp[1].strip())
  lines = s.split()
  #print(lines)

  data[st] = {}
  data[st]["ind"] = ind
  for i in range(0,int(len(lines)/3)):
    t = float(lines[i*3][1:])
    l = lines[i*3+1]
    h = lines[i*3+2]
    if l == "-":
      l = 0
    else:
      l= float(l)
    if h == "-":
      h = 100
    else:
      h = float(h)
    data[st]["tick" + str(i)] = t
    data[st]["t" + str(i) + "low"] = l
    data[st]["t" + str(i) + "high"] = h

  #print(data)

  return data
def convert_time_to_epoch_old(time_str):
    # Get the current date in Eastern Timezone
    eastern_offset = timedelta(hours=-5)  # Eastern Time is UTC-5 during Standard Time (UTC-4 during Daylight Saving Time)
    current_datetime = datetime.utcnow() + eastern_offset

    # Parse the time string to get hours, minutes, and seconds
    time_parts = time_str.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1].split()[0])
    seconds = int(time_parts[2].split()[0])

    # Set the current date with the parsed time
    current_datetime = current_datetime.replace(hour=hours, minute=minutes, second=seconds)

    # Convert the datetime object to epoch time
    epoch_time = int(current_datetime.timestamp())
    return epoch_time




def is_daylight_saving_time(date):
    # Function to check if a given date is within Daylight Saving Time (DST) in Eastern Time (ET)
    # DST starts on the second Sunday of March and ends on the first Sunday of November
    
    # Define the Eastern Time (ET) time zone
    et_tz = timezone(timedelta(hours=-5))  # Eastern Time is UTC-5 (or UTC-4 during DST)

    # Get the year for the provided date to determine the DST start and end dates
    year = date.year

    # DST starts on the second Sunday of March
    dst_start = datetime(year, 3, 8) + timedelta(6 - datetime(year, 3, 8).weekday())
    dst_start = dst_start.replace(tzinfo=et_tz)

    # DST ends on the first Sunday of November
    dst_end = datetime(year, 11, 1) + timedelta(6 - datetime(year, 11, 1).weekday())
    dst_end = dst_end.replace(tzinfo=et_tz)

    return dst_start <= date < dst_end

def convert_time_to_epoch(input_string):
    #print(input_string)
    # Parse the input string to extract time information and determine if it's AM or PM
    time_str, am_pm = input_string.split('(')[0].strip().split()
    hour, minute, second = map(int, time_str.split(':'))
    is_pm = am_pm.lower() == 'pm'
    current_gmt_time = datetime.now(timezone.utc)
    if hour ==12:
        hour = 0 #if PM, needs to be 0 + 12.  IF AM, needs to be 0.  next line only adds 12 if PM.
    # Calculate the corresponding GMT time for the provided ET time
    et_datetime = current_gmt_time.replace(hour=hour + 12 if is_pm else hour, minute=minute, second=second)

    # Check if it's Daylight Saving Time (DST) for the determined date
    is_dst = is_daylight_saving_time(et_datetime)

    # Define the Eastern Time (ET) time zone
    et_offset = timedelta(hours=-5)  # Eastern Time is UTC-5 (or UTC-4 during DST)

    # Convert the datetime from ET to UTC
    utc_datetime = et_datetime - et_offset - timedelta(hours=is_dst)

    # Convert the UTC datetime to epoch time (seconds since January 1, 1970)
    epoch_time = int((utc_datetime - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    return epoch_time


def get_current_day_month_year():
    # Get the current datetime in GMT (UTC)
    current_gmt_time = datetime.now(timezone.utc)

    # Extract the day, month, and year from the current datetime
    current_day = current_gmt_time.day  # Day of the month (1 to 31)
    current_month = current_gmt_time.month  # Month of the year (1 to 12)
    current_year = current_gmt_time.year

    return current_day, current_month, current_year

#print(get_current_day_month_year())

def determine_win_loose(data, bought):
    ret = 0
    for d in data:
        for name in bought:
            for t in data[d][name]:
                final = data[d][name][t]["values"][0]
                for tick in bought[name]:
                    num = bought[name][tick]
                    result = 0
                    if (num >0 and final > tick) or (num<0 and final < tick):
                        ret += num*99
                        print("won 2")
    return ret
  
                    
                    
                    
                        
   
       