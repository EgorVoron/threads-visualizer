from threads_visualizer.thread_cards import CardsManager, Card
import time
from h2o_wave import ui, data


class GeneralCard(Card):
    def __init__(self, cards_manager: CardsManager, buffer_rows=15, expected_value=None, update_period=3):
        super(GeneralCard, self).__init__(width=2, height=1)
        self.last_update = time.time()
        self.general_stats = 0.0
        self.update_period = update_period
        self.expected_value = expected_value
        self.cards_manager = cards_manager
        self.card = cards_manager.page.add(f'general_stats', ui.wide_series_stat_card(
            box=self.gen_box(),
            title=f'General',
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
        if "general" not in self.cards_manager.rows_of_type.keys():
            free_row = self.cards_manager.get_free_row()
            self.cards_manager.rows_of_type["general"] = {"start": free_row,
                                                          "end": free_row}
        return f'1 {self.cards_manager.rows_of_type["general"]["end"]} {self.width} {self.height}'

    def update_stats(self, iteration, thread_stats):
        self.general_stats += thread_stats
        curr_update = time.time()
        dt = curr_update - self.last_update
        if dt > self.update_period:
            output_stats = round(self.general_stats / dt, 2)
            self.card.plot_color = '$green' if not self.expected_value or output_stats >= self.expected_value \
                else '$red'
            self.card.data.iter_sec = output_stats
            self.card.plot_data[-1] = [iteration, output_stats]
            self.cards_manager.page.save()
            self.general_stats = 0
            self.last_update = curr_update
