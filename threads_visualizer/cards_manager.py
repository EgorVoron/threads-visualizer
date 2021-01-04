from h2o_wave import site


class CardsManager:
    def __init__(self, route: str):
        self.page = site[route]
        self.rows_of_type = {}

    def get_free_row(self):
        return max(self.rows_of_type.values(), key=lambda x: x["end"])["end"] + 1 if self.rows_of_type else 1
