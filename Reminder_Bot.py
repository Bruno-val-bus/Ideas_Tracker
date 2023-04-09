import random
import GoogleSheets_API as gs_api
import abc
from datetime import datetime, timedelta
import smtplib


class ConceptsReminder:

    def __init__(self):
        self.message_times = []
        self.concepts = gs_api.ConceptsAPI()
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
        import pywhatkit as w_a
        time_hour = int(msg_time.split(":")[0])
        time_min = int(msg_time.split(":")[1])
        w_a.sendwhatmsg(phone_no=self.my_phone_number, message=message, time_hour=time_hour, time_min=time_min)


class EmailReminder(ConceptsReminder):
    def __init__(self):
        super(EmailReminder, self).__init__()
        self._smtp_server: str = "smtp.gmail.com"
        self._port: int = 587
        self._sender_email: str = "bruno.valverde.bustamante.95@gmail.com"
        self._receiver_email: str = self._sender_email
        self._password: str = "cessna421ER"
        self._subject: str = "Your daily friendly reminder"

    def _send_message(self, message: str, msg_time: str):
        template: str = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

        %s
        """ % (self._sender_email, self._receiver_email, self._subject, message)
        # FIXME: current error OSError: [Errno 101] Network is unreachable. Might be solvable using gmail email provider. Although currently not working here because of authentication error (email and password are correct!!)

        #   s. Traceback very similar to traceback tail in https://www.pythonanywhere.com/forums/topic/27561/
        with smtplib.SMTP(self._smtp_server, self._port) as server:
            server.starttls()
            server.login(self._sender_email, self._password)
            server.sendmail(from_addr=self._sender_email, to_addrs=self._receiver_email, msg=template)


class BooksReminder:
    pass


if __name__ == "__main__":
    reminder = EmailReminder()
    reminder.set_concept_messaging_frequency()
    reminder.start_reminder()
