from base_page import BasePage

class ViewProductPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.add_label("View Products Page")
        # Add more widgets for the view products page here

