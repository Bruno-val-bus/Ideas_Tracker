import pywhatkit as w_a
import random
import GoogleSheets_API as gs_api
import time
import abc
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ConceptsReminder:

    def __init__(self):
        self.message_times = []
        self.concepts = gs_api.Concepts_API()
        self.my_phone_number: str = "+4917662048997"
        self.total_no_messages: int = 0
        self.messaging_time: int = 0
        self.messaging_frequency_hrs: float = 0.0

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

    @abc.abstractmethod
    def _send_message(self, message: str, msg_time: str):
        return

    def set_concept_messaging_frequency(self):
        user_input = input("Input frequency of concepts messaging (hrs/day):")
        self.messaging_frequency_hrs = float(user_input)
        # create list of times based on frequency for the next 24 hours
        self.messaging_time = 24
        self.total_no_messages = int(self.messaging_time / self.messaging_frequency_hrs)
        now = datetime.now()
        self.message_times.append((now + timedelta(hours=0.05)).strftime("%H:%M"))
        for message_no in range(1, self.total_no_messages):
            delta = message_no * self.messaging_frequency_hrs  # add some extra time for debugging
            message_time = (now + timedelta(hours=delta)).strftime("%H:%M")
            self.message_times.append(message_time)
        print("Messages will be sent at:")
        for msg_time in self.message_times:
            print(msg_time)


class WhatsAppReminder(ConceptsReminder):
    def __init__(self):
        super(WhatsAppReminder, self).__init__()

    def _send_message(self, message: str, msg_time: str):
        time_hour = int(msg_time.split(":")[0])
        time_min = int(msg_time.split(":")[1])
        w_a.sendwhatmsg(phone_no=self.my_phone_number, message=message, time_hour=time_hour, time_min=time_min)


class EmailReminder(ConceptsReminder):
    def __init__(self):
        # super(EmailReminder, self).__init__()
        self._smtp_server = "smtp-mail.outlook.com"
        self._subject = "SMTP e-mail Test"
        self._port = 587
        self._sender_email = "bruno.valverde.95@outlook.es"
        self._receiver_email = self._sender_email
        self._password = "cessna421ER"

    def _send_message(self, message: str, msg_time: str):
        with smtplib.SMTP(self._smtp_server, self._port) as server:
            server.starttls()
            server.login(self._sender_email, self._password)
            server.sendmail(from_addr=self._sender_email, to_addrs=self._receiver_email, msg=message)


class BooksReminder:
    pass


if __name__ == "__main__":
    reminder = EmailReminder()
    reminder._send_message(message="TEST message", msg_time=None)
    reminder.set_concept_messaging_frequency()
    reminder.start_reminder()
