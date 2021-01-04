from threads_visualizer import CardsManager, GeneralCard, ThreadPairCard
import time
from random import randint
import threading as th

cards_manager = CardsManager('/test')
general_card = GeneralCard(cards_manager, update_period=1)


def thread_implementation1(thread_num):
    max_value = 20
    card = ThreadPairCard(thread_num, max_value, cards_manager)
    st_time = time.time()
    for i in range(max_value + 1):
        u = 2 if thread_num == 1 else (randint(4, 10) / 10)
        time.sleep(u)
        if i and i % 1 == 0:
            curr_time = time.time()
            iter_sec = round(10 / (curr_time - st_time), 2)  # count effectiveness (iters per sec)
            card.update_stats(i, iter_sec, i)  # update card stats
            general_card.update_stats(i, 10)
            st_time = curr_time


class MyThread1(th.Thread):
    def __init__(self, num):
        th.Thread.__init__(self)
        self.num = num

    def run(self):
        thread_implementation1(self.num)


for _ in range(3):
    my_thread = MyThread1(_)
    my_thread.start()

print(cards_manager.rows_of_type)
