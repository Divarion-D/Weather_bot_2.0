import matplotlib.pyplot as plt
import numpy as np

'''
The class Diagram is used to create a diagram of the temperature and humidity for a given number of days.
'''


class Diagram:
    def __init__(self):
        self.temperature_key = np.arange(-50, 50, 10)
        self.humadity_key = np.arange(0, 100, 10)
        self.gridsize = (2, 1)
        self.fig = plt.figure(figsize=(10, 6))
        self.ax1 = plt.subplot2grid(self.gridsize, (0, 0))
        self.ax2 = plt.subplot2grid(self.gridsize, (1, 0))

    def set_data(self, days, humaditys, temperatures):
        '''
        Set the data for the diagram.

        Parameters:
            days: An array listing the days of the month.
            temperatures: An array listing the temperatures for each day.
            humaditys: An array listing the humidity for each day.
        '''
        self.days = days
        self.humaditys = humaditys
        self.temperatures = temperatures
        self.max_temperature = np.max(self.temperatures)
        self.min_temperature = np.min(self.temperatures)

    def draw_diagram(self):
        '''
        Draw the diagram.
        '''
        self.ax1.vlines(x=self.days, ymin=0, ymax=self.humaditys,
                        color='#89CFF0', linewidth=20)  # Вертикальные линии
        self.ax1.set_ylim(0, 107)  # Установка границ по оси Y
        self.ax1.set_title('Влажность')  # Заголовок графика
        self.ax1.set_ylabel('Влажность (%)')  # Название оси y
        self.ax1.set_xlabel('День')  # Название оси Х
        self.ax1.set_yticks(self.humadity_key)  # Установка осей для влажности
        self.ax1.set_xticks(self.days)  # Установка отступов для дней
        self.ax1.set_xticklabels(self.days)  # Подписи дней
        self.ax1.grid(True)  # Включаем сетку

        # Установка подписей для графика влажности
        for i, self.humaditys in enumerate(self.humaditys):
            self.ax1.text(i+1, self.humaditys+0.5,
                          round(self.humaditys, 1), horizontalalignment='center')

        self.ax2.vlines(x=self.days, ymin=0, ymax=self.temperatures,
                        color='#FF0000', linewidth=20)  # Вертикальные линии
        # Установка границ по оси Y
        self.ax2.set_ylim(self.min_temperature-10, self.max_temperature+10)
        self.ax2.set_title('Температура')  # Заголовок графика
        self.ax2.set_ylabel('Температура (°C)')  # Название оси y
        self.ax2.set_xlabel('День')  # Название оси Х
        # Установка осей для температуры
        self.ax2.set_yticks(self.temperature_key)
        self.ax2.set_xticks(self.days)  # Установка отступов для дней
        self.ax2.set_xticklabels(self.days)  # Подписи дней
        self.ax2.grid(True)  # Включаем сетку

        # Установка подписей для графика температуры
        for i, self.temperatures in enumerate(self.temperatures):
            if self.temperatures > 0:
                # Если температура больше 0, то показываем ее вверху
                self.ax2.text(i+1, -8, round(self.temperatures, 1),
                              horizontalalignment='center')
            else:
                # Если температура меньше 0, то показываем ее внизу
                self.ax2.text(i+1, 2, round(self.temperatures, 1),
                              horizontalalignment='center')
        self.fig.tight_layout()  # Убираем лишние отступы

    def show(self):
        '''
        Show the diagram on the screen.
        '''
        plt.show()

    def close(self):
        '''
        Close the diagram window.
        '''
        plt.close()

    def save(self, filename):
        '''
        Save the diagram.
        '''
        self.fig.savefig(filename)


if __name__ == '__main__':
    from calendar import monthrange
    from datetime import datetime

    np.random.seed(444)

    current_year = datetime.now().year  # Текущий год
    month = datetime.now().month  # Текущий месяц
    day = monthrange(current_year, month)[1]  # Количество дней в месяце
    days = np.arange(1, day + 1)  # Массив дней
    # days_key = np.arange(day) # Массив ключей дней

    humaditys = np.random.randint(0, 100, size=31)  # Массив случайных чисел
    # Массив случайных чисел
    temperatures = np.random.randint(-50, 50, size=31)

    diagram = Diagram()
    diagram.set_data(days, humaditys, temperatures)
    diagram.draw_diagram()
    diagram.show()
