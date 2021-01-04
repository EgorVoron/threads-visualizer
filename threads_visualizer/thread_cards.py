from threads_visualizer.card import Card
from threads_visualizer.cards_manager import CardsManager
from h2o_wave import ui, data


class ThreadCard(Card):
    def __init__(self, thread_num, max_boxes_in_line, width, height, cards_manager: CardsManager):
        super(ThreadCard, self).__init__(width, height)
        self.thread_num = thread_num
        self.boxes_in_line = max_boxes_in_line // self.width
        self.cards_manager = cards_manager

    def get_row(self, manager: CardsManager):
        class_name = self.__class__.__name__
        if class_name not in manager.rows_of_type.keys():
            free_row = manager.get_free_row()
            manager.rows_of_type[class_name] = {"start": free_row,
                                                "end": free_row + self.height - 1}
        row = manager.rows_of_type[class_name]["start"] + (self.thread_num // self.boxes_in_line) * self.height
        manager.rows_of_type[class_name]["end"] = max(manager.rows_of_type[class_name]["end"], row)
        return row


class ThreadSeriesCard(ThreadCard):
    def __init__(self, thread_num, cards_manager, buffer_rows=15, expected_value=None,
                 max_boxes_in_line=10, width=2, height=1):
        super(ThreadSeriesCard, self).__init__(thread_num, max_boxes_in_line, width, height, cards_manager)
        self.expected_value = expected_value

        self.card = cards_manager.page.add(f'thread_{thread_num}_series', ui.wide_series_stat_card(
            box=self.gen_box(),
            title=f'Thread #{thread_num}',
            value='={{iter_sec}}',
            aux_value='',
            data=dict(iter_sec=0.0),
            plot_data=data('tick usage', -buffer_rows),
            plot_category='tick',
            plot_value='usage',
            plot_zero_value=0,
            plot_color='$green',
            plot_curve='smooth'
        ))
        self.card.data.iter_sec = "No data"

    def gen_box(self):
        return f'{1 + (self.thread_num % self.boxes_in_line) * self.width}' \
            f' {self.get_row(self.cards_manager)} {self.width} {self.height}'

    def update_stats(self, iteration, series_stats):
        self.card.plot_color = '$green' if not self.expected_value or series_stats >= self.expected_value else '$red'
        self.card.data.iter_sec = series_stats
        self.card.plot_data[-1] = [iteration, series_stats]
        self.cards_manager.page.save()


class ThreadBarCard(ThreadCard):
    def __init__(self, thread_num, max_value, cards_manager: CardsManager, max_boxes_in_line=10, width=2, height=1):
        super(ThreadBarCard, self).__init__(thread_num, max_boxes_in_line, width, height, cards_manager)
        self.max_value = max_value

        self.card = self.cards_manager.page.add(f'thread_{thread_num}_bar', ui.wide_bar_stat_card(
            box=self.gen_box(),
            title=f'Thread #{thread_num}',
            value='={{value}}',
            aux_value='={{pc}}%',
            plot_color='$green',
            progress=0,
            data={'value': 0, 'pc': 0},
        ))

    def gen_box(self):
        return f'{1 + (self.thread_num % self.boxes_in_line) * self.width} ' \
            f'{self.get_row(self.cards_manager)} {self.width} {self.height}'

    def update_stats(self, bar_value):
        fraction = round(bar_value / self.max_value, 4)
        percent = round(fraction * 100, 2)
        self.card.data.value = bar_value
        self.card.data.pc = percent
        self.card.progress = fraction
        self.cards_manager.page.save()


class ThreadPairCard(ThreadCard):
    def __init__(self, thread_num, max_value, cards_manager: CardsManager, buffer_rows=15, expected_value=None,
                 max_boxes_in_line=10):
        super(ThreadPairCard, self).__init__(thread_num, width=2, height=3, max_boxes_in_line=max_boxes_in_line,
                                             cards_manager=cards_manager)
        self.max_value = max_value
        self.expected_value = expected_value
        box_1 = self.gen_box()
        box_1_list = [int(i) for i in box_1.split()]
        box_2 = f'{box_1_list[0]} {box_1_list[1] + 1} {box_1_list[2]} {box_1_list[3]}'

        self.series_card = self.cards_manager.page.add(f'thread_{thread_num}_series_paired', ui.wide_series_stat_card(
            box=box_1,
            title=f'Thread #{thread_num}',
            value='={{iter_sec}}',
            aux_value='',
            data=dict(iter_sec=0.0),
            plot_data=data('tick usage', -buffer_rows),
            plot_category='tick',
            plot_value='usage',
            plot_zero_value=0,
            plot_color='$green',
            plot_curve='smooth'
        ))
        self.series_card.data.iter_sec = "No data"

        self.bar_card = self.cards_manager.page.add(f'thread_{thread_num}_bar_paired', ui.wide_bar_stat_card(
            box=box_2,
            title=f'Thread #{thread_num}',
            value='={{value}}',
            aux_value='={{pc}}%',
            plot_color='$green',
            progress=0,
            data={'value': 0, 'pc': 0},
        ))

    def gen_box(self):
        return f'{1 + (self.thread_num % self.boxes_in_line) * self.width} ' \
            f'{self.get_row(self.cards_manager)} {self.width} 1'

    def update_stats(self, iteration, series_stats, bar_value):
        if (not self.expected_value and series_stats > 0) or series_stats >= self.expected_value:
            color = '$green'
        else:
            color = '$red'
        self.series_card.plot_color, self.bar_card.plot_color = color, color
        self.series_card.data.iter_sec = series_stats
        self.series_card.plot_data[-1] = [iteration, series_stats]

        fraction = round(bar_value / self.max_value, 4)
        percent = round(fraction * 100, 2)
        self.bar_card.data.value = bar_value
        self.bar_card.data.pc = percent
        self.bar_card.progress = fraction

        self.cards_manager.page.save()
