import csv
import math
from datetime import datetime
from datetime import timedelta

import csv
import datetime
import time

from gpiozero import MotionSensor

#get sensor input and write it to csv file
try:
    pir = MotionSensor(pin = 4, threshold = 0.3, queue_len = 1, sample_rate = 100)
    counter = 0

    columns = [["Hour","Minute","Motion_count"]]

    with open('test.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(columns)

    while True:
        print("Still running")
        hour = datetime.datetime.now().hour
        minute=datetime.datetime.now().minute


        hour = datetime.datetime.now().hour
        minute=datetime.datetime.now().minute

        cur_time=datetime.datetime.now().minute
        counter = 0

        while(cur_time==minute):
            if pir.motion_detected:
                print("Motion Detected!")
                counter = counter + 1
                print(counter)
                time.sleep(2)

            minute = datetime.datetime.now().minute

        hour = datetime.datetime.now().hour
        with open('test.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([hour,minute, counter])

except KeyboardInterrupt:

    #on keyboardinterrupt, analyse file for time to fall asleep

    no_motion_threshold = 15
    no_consecutive_motion_events = 0
    hour_you_fell_asleep = 0
    minute_you_fell_asleep = 0
    line_you_fell_asleep = 0

    hour_you_woke_up =0
    minute_you_woke_up =0

    number_of_interruptions =0

    sleep_duration=0

    system_start_hour =0
    system_start_minute =0

    with open("test.csv") as fp:

        time =1
        curr_time =1

        csv_reader = csv.reader(fp, delimiter=',')

        line_count = -1
        curr_time = line_count


        #Getting time to fall asleep
        for row in csv_reader:
            line_count = line_count + 1
            curr_time = line_count

            if line_count == 1:
                starting_hour = int(row[0])
                starting_minute = int(row[1])

            if row[2] == "0":
                no_consecutive_motion_events = no_consecutive_motion_events + 1

            elif row[2] != "0":
                no_consecutive_motion_events = 0
                time = line_count
                line_you_fell_asleep = time+1
                hour_you_fell_asleep = row[0]
                minute_you_fell_asleep = row[1]
                curr_time = line_count

            if no_consecutive_motion_events == no_motion_threshold:
                curr_time = line_count
                current_hour = row[0]
                current_minute = row[1]
                break;

    print("\n\n**********finished*******************\n")
    time_you_fell_asleep = hour_you_fell_asleep + ":" + minute_you_fell_asleep


    sleep_interruption_threshold_minutes = 6
    motion_event_threshold = 4
    consecutive_motion_events = 0
    hour_you_woke_up = 0
    minute_you_woke_up = 0

    rows = []
	
	
	
	#adding all rows to an array to allow for easier analysis on sleep interruptions
    with open("test.csv") as fp:

        time =1
        curr_time =1

        csv_reader = csv.reader(fp, delimiter=',')

        line_count = -1
        curr_time = line_count

        for row in csv_reader:
            rows.append(row)


        line_counter = line_you_fell_asleep
        size = len(rows) - 5
        current_line = line_counter


        #start analysis from time fallen asleep onwards
        while current_line <= size:
            motion_count = rows[current_line-1][2]
            motion_count = motion_count
            if motion_count != '0':
                consecutive_motion_events = consecutive_motion_events + 1

                for i in range(5):
                    index = current_line +i
                    current = rows[index][2]

                    if current != '0':
                        consecutive_motion_events = consecutive_motion_events + 1

            else:
                consecutive_motion_events = 0

            if consecutive_motion_events >= 4:
                number_of_interruptions = number_of_interruptions + 1
                consecutive_motion_events = 0
                current_line = current_line + 5
            consecutive_motion_events = 0

            current_line = current_line+1


        hour_you_woke_up = rows[len(rows)-1][0]
        minute_you_woke_up = rows[len(rows)-1][1]


    #putting bed time in correct format
    time_you_went_to_bed = str(starting_hour) + ":" + str(starting_minute)


    #formatting wake up time
    time_you_woke_up = hour_you_woke_up + ":" + minute_you_woke_up


    #calculate time in bed
    FMT = '%H:%M'
    total_time_in_bed = datetime.datetime.strptime(time_you_woke_up, FMT) - datetime.datetime.strptime(time_you_went_to_bed, FMT)
    if total_time_in_bed.days < 0:
        total_time_in_bed = timedelta(
            days=0,
            seconds=total_time_in_bed.seconds,
            microseconds=total_time_in_bed.microseconds
        )

    #Calculate duration asleep
    sleep_duration = datetime.datetime.strptime(time_you_woke_up, FMT) - datetime.datetime.strptime(time_you_fell_asleep, FMT)
    if sleep_duration.days < 0:
        sleep_duration = timedelta(
            days=0,
            seconds=sleep_duration.seconds,
            microseconds=sleep_duration.microseconds
        )


    #subtract the time spent interrupted from sleep
    interruption_time = datetime.timedelta(minutes = 6*number_of_interruptions)
    sleep_duration_less_interruptions = sleep_duration - interruption_time


    #calculate the total time spent asleep (sleep efficiency)
    sleep_efficiency = (sleep_duration_less_interruptions.total_seconds() / total_time_in_bed.total_seconds()) * 100
    sleep_efficiency = round(sleep_efficiency, 2)


    #calculating sleep latency
    sleep_latency = datetime.datetime.strptime(time_you_fell_asleep, FMT) - datetime.datetime.strptime(time_you_went_to_bed, FMT)
    if sleep_latency.days < 0:
        sleep_latency = timedelta(
            days=0,
            seconds=sleep_latency.seconds,
            microseconds=sleep_latency.microseconds
        )


    #email message body with sleep stats
    message_body = "You fell asleep at " + time_you_fell_asleep
    message_body = message_body + "\nYou woke up at " + time_you_woke_up
    message_body = message_body + "\nYou had " + str(number_of_interruptions) + " interruption(s)"
    message_body = message_body + "\nYou slept for " + str(sleep_duration_less_interruptions)
    message_body = message_body + "\nYour sleep effiency score is " + str(sleep_efficiency) + "%"
    message_body = message_body + "\nSleep latency (How long it took you to fall asleep) is " + str(sleep_latency)
    print(message_body)


    #email sleep csv file to user along with sleep stats
    import smtplib
    from email.message import EmailMessage


    emailfrom = "ENTER YOUR EMAIL"
    emailto = "DESTINATION EMAIL"
    fileToSend = "test.csv"
    username = "ENTER YOUR EMAIL HERE"
    password = "ENTER YOUR PASSWORD HERE"
		
		
    msg = EmailMessage()
    msg["From"] = emailfrom
    msg["Subject"] = "Your sleep stats"
    msg["To"] = emailto
    msg.set_content(message_body)
    msg.add_attachment(open("test.csv", "r").read(), filename="test.csv")


    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()
