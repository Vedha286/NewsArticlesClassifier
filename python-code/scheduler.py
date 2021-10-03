# pip install schedule
import schedule
import time

# calling events


def train():
    print("hi this is training event")


def predict():
    print("hi this is predict event")


# Task scheduling
# After every 10mins geeks() is called.
schedule.every(10).seconds.do(train)
schedule.every(20).seconds.do(predict)

while True:
    schedule.run_pending()
    time.sleep(1)
