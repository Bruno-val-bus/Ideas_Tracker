import pywhatkit as w_a
import random
import GoogleSheets_API as gs_api
import time
import os
from datetime import datetime, timedelta

class Concepts_Reminder:
    concepts = gs_api.Concepts_API()
    my_phone_number = "+4917662048997"
    total_no_messages: int
    messaging_time: int
    messaging_frequency_hrs: float

    def __init__(self):
        self.message_times = []

    def start_reminder(self):
        for message_time in self.message_times:
            message = self._get_random_concept()
            self._send_message(message, message_time)  # "17:00"
            print(f"Message sent at {message_time}")

    def _get_random_concept(self):
        messages = []
        for concept, usage_count in self.concepts.initial_concepts.items():
            if usage_count == self.concepts.min_usage_count:
                # only interested in sending concepts as message that have not been sent too often
                messages.append(concept)
        random_key = random.randint(0, len(messages) - 1)
        concept = messages[random_key]
        self.concepts.increase_concept_usage(concept)
        return concept

    def _send_message(self, message: str, time: str):
        time_hour = int(time.split(":")[0])
        time_min = int(time.split(":")[1])
        w_a.sendwhatmsg(phone_no=self.my_phone_number, message=message, time_hour=time_hour, time_min=time_min)

    def set_concept_messaging_frequency(self):
        user_input = input("Input frequency of concepts messagin (hrs):")
        self.messaging_frequency_hrs = float(user_input)
        # create list of times based on frequency for the next 24 hours
        self.messaging_time = 24
        self.total_no_messages = int(self.messaging_time / self.messaging_frequency_hrs)
        (datetime.now() + timedelta(hours=0.5)).strftime("%H:%M")
        now = datetime.now()
        for message_no in range(1, self.total_no_messages):
            delta = message_no*self.messaging_frequency_hrs  # add some extra time for debugging
            message_time = (now + timedelta(hours=delta)).strftime("%H:%M")
            self.message_times.append(message_time)


class Books_Reminder:
    pass

if __name__ == "__main__":
    reminder = Concepts_Reminder()
    reminder.set_concept_messaging_frequency()
    reminder.start_reminder()
