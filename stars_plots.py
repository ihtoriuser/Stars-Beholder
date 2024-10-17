import numpy as np
from PyQt5 import QtGui
import matplotlib.pyplot as plt

from astropy.timeseries import LombScargle
from convert_dates import *

def built_plots(time, magnitude, errormag,starname):
    # Добавления стиля
    plt.style.use('seaborn-whitegrid')
    
    # Удаление шумов/аномалий
    q1 = np.percentile(magnitude, 25) # первый квартиль
    q3 = np.percentile(magnitude, 75) # третий квартиль
    iqr = q3 - q1 # межквартильный размах

    lower_bound = q1 - 1.5 * iqr # нижняя граница нормальных значений
    upper_bound = q3 + 1.5 * iqr # верхняя граница нормальных значений

    # удаление аномальных значений
    magnitude_filtered = magnitude[(magnitude >= lower_bound) & (magnitude <= upper_bound)]
    time_filtered = time[(magnitude >= lower_bound) & (magnitude <= upper_bound)]
    errormag_filtered = errormag[(magnitude >= lower_bound) & (magnitude <= upper_bound)]
    
    # Настройки кона
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12, 6))
    ax[0][0].set_position([0.1, 0.6, 0.4, 0.3])
    ax[0][1].set_position([0.55, 0.6, 0.4, 0.3])
    ax[1][0].set_position([0.1, 0.1, 0.85, 0.4])

    fig.delaxes(ax[1][1])

    fig.canvas.manager.window.setWindowTitle(f"Plots for '{starname}' with your records:")
    icon = QtGui.QIcon('ui/Stars Beholder.ico')
    fig.canvas.manager.window.setWindowIcon(icon)

    # Вызов функции Ломба-Скаргла
    ls = LombScargle(time_filtered, magnitude_filtered)
    without_err = (errormag_filtered == 0).all()
    if without_err:
        frequency, power = LombScargle(time_filtered, magnitude_filtered).autopower(nyquist_factor=500, minimum_frequency=0.2)
    else:
        frequency, power = LombScargle(time_filtered, magnitude_filtered, errormag_filtered).autopower(nyquist_factor=500, minimum_frequency=0.2)
    
    period = 1. / frequency
    best_period = period[np.argmax(power)]
    phase = (time_filtered / best_period) % 1
  
    # Аппроксимация значений
    phase_model = np.linspace(-0.5, 1.5, 100)
    best_frequency = frequency[np.argmax(power)]
    
    mag_model = ls.model(phase_model / best_frequency, best_frequency)

    period_days = 1. / frequency
    period_hours = period_days * 24

    # Вывод периодограммы
    ax[0][0].plot(period_days, power, '-k', rasterized=True)
    ax[0][0].set(xlim=(0, 7), ylim=(0, 0.8),
          xlabel='Period (days)',
          ylabel='Lomb-Scargle Power',
          title='Lomb-Scargle Periodogram')
    
    inset = fig.add_axes([0.3, 0.75, 0.19, 0.13])
    inset.plot(period_hours, power, '-k', rasterized=True)
    inset.xaxis.set_major_locator(plt.MultipleLocator(1))
    inset.yaxis.set_major_locator(plt.MultipleLocator(0.2))
    inset.set(xlim=(1, 5),
          xlabel='Period (hours)',
          ylabel='power')

    # Построение кривой блеска
    ax[0][1].errorbar(time, magnitude, errormag, color='black',
               fmt='.', ecolor='lightgray', capsize=1)
    ax[0][1].set(xlabel='time (JD/MJD)', ylabel='mag', title='Light Curve')
  
   
    # Фазовая диаграмма
    amplitude = max(magnitude) - min(magnitude)
    for offset in [-1, 0, 1]:
        ax[1][0].errorbar(phase + offset, magnitude_filtered, errormag_filtered, fmt='.',
                   color='black', ecolor='lightgray', capsize=1)
        ax[1][0].plot(phase_model, mag_model, lw=1, color='red')
    ax[1][0].set(xlim=(-0.5, 1.5), xlabel='phase',
          ylabel='mag', title='Phase Diagram')
    ax[1][0].text(0.02, 0.03, "Period = {0:.2f} hours  Amplitude= {1:.3f}".format(24*best_period, amplitude), transform=ax[1][0].transAxes)

    # Инвертация осей
    ax[0][1].invert_yaxis()
    ax[1][0].invert_yaxis()
    plt.show()
    return 24*best_period, amplitude
