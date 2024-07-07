from base_page import BasePage

class SearchProductPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.add_label("Search Product Page")
        # Add more widgets for the search product page here


