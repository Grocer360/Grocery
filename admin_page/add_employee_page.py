from base_page import BasePage

class AddEmployeePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.add_label("Add Employees Page")
        # Add more widgets for the add employees page here


