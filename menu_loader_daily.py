import openpyxl

class MenuLoaderDaily:
    def __init__(self, filepath):
        self.filepath = filepath
        self.menu_data = self.load_menu_data()

    def load_menu_data(self):
        wb = openpyxl.load_workbook(self.filepath)
        ws = wb.active

        menu_data = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            week = row[0]
            day = row[1]
            menu = row[2]
            if week not in menu_data:
                menu_data[week] = {}
            menu_data[week][day] = menu

        return menu_data

    def get_menu_for_day(self, week, day):
        return self.menu_data.get(week, {}).get(day, "Извините, меню на сегодня не найдено.")

    def get_menu_for_week(self, week):
        return self.menu_data.get(week, "Извините, меню на эту неделю не найдено.")

if __name__ == "__main__":
    loader = MenuLoaderDaily('optimized_menu.xlsx')
    print(loader.get_menu_for_day(1, 'Понедельник'))
    print(loader.get_menu_for_week(1))
