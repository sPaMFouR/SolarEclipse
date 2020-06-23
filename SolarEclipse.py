#!/usr/bin/env python
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx #
# xxxxxxxxxxxxxxxxxxx--------------------COMPUTE POSITION ANGLE OF THE MOON----------------------xxxxxxxxxxxxxxxxxxxx #
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx #

# ------------------------------------------------------------------------------------------------------------------- #
# Import Required Libraries
# ------------------------------------------------------------------------------------------------------------------- #
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import Distance
from astropy.time import Time, TimeDelta
from astropy.coordinates import get_body, Longitude, Latitude, EarthLocation, AltAz
# ------------------------------------------------------------------------------------------------------------------- #


# ------------------------------------------------------------------------------------------------------------------- #
# Global Variables [Location = Bengaluru]
# ------------------------------------------------------------------------------------------------------------------- #
sun_radius = 6.957e10 * u.cm
moon_radius = 1.737e8 * u.cm

DATE = '2020-06-21'
LAT = 12.9352
LON = 77.6245
TIMEZONE = +5.5

lon = Longitude('{0} deg'.format(LON))
lat = Latitude('{0} deg'.format(LAT))
loc = EarthLocation.from_geodetic(lon, lat)

File_EXIF = 'AnnularSolarEclipse_June21.csv'
data_exif = pd.read_csv(File_EXIF, comment='#')

time_arr = data_exif['Time'].values
timearr_local = [Time("{0} {1}".format(DATE, time), format='iso') for time in time_arr]
timearr_utc = [timelocal - TIMEZONE * u.hour for timelocal in timearr_local]
# ------------------------------------------------------------------------------------------------------------------- #


# ------------------------------------------------------------------------------------------------------------------- #
# Animating the Partial Eclipse in Bengaluru
# ------------------------------------------------------------------------------------------------------------------- #
start_time = '10:00:00'
end_time = '10:20:00'

timestart_local = Time("{0} {1}".format(DATE, start_time), format='iso')
timeend_local = Time("{0} {1}".format(DATE, end_time), format='iso')
timestart_utc = timestart_local - TIMEZONE * u.hour
timeend_utc = timeend_local - TIMEZONE * u.hour

data = pd.DataFrame()

index = 0
time = timestart_utc
while time <= timeend_utc:
    sun = get_body('sun', time, loc, ephemeris='builtin')
    moon = get_body('moon', time, loc, ephemeris='builtin')
    pa = sun.position_angle(moon).degree
    altaz_sun = sun.transform_to(AltAz(location=loc, obstime=time))
    altaz_moon = moon.transform_to(AltAz(location=loc, obstime=time))
    sun_dist = Distance(sun.distance, unit=u.cm)
    moon_dist = Distance(moon.distance, unit=u.cm)
    sun_size = 2 * sun_radius * 60 * 180 / (np.pi * sun_dist)
    moon_size = 2 * moon_radius * 60 * 180 / (np.pi * moon_dist)

    data.loc[index, 'UT'] = time
    data.loc[index, 'PA'] = round(sun.position_angle(moon).degree, 3)
    data.loc[index, 'SunALT'] = round(altaz_sun.alt.degree, 3)
    data.loc[index, 'SunAZ'] = round(altaz_sun.az.degree, 3)
    data.loc[index, 'SunAZ'] = round(altaz_sun.az.degree, 3)
    data.loc[index, 'SunSize'] = round(float(sun_size), 3)
    data.loc[index, 'MoonALT'] = round(altaz_moon.alt.degree, 3)
    data.loc[index, 'MoonAZ'] = round(altaz_moon.az.degree, 3)
    data.loc[index, 'MoonSize'] = round(float(moon_size), 3)

    index += 1
    time += TimeDelta(60 * u.s)



import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DateFormatter, MinuteLocator, HourLocator
from matplotlib.ticker import MultipleLocator
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111)

time = [(time + TIMEZONE * u.hour).utc.datetime for time in data['UT'].values]
sunalt = data['SunALT'].values
sunsize = data['SunSize'].values
moonalt = data['MoonALT'].values
moonsize = data['MoonSize'].values

plots = [ax.plot(time, obj, c=['orange', 'k'][idx])[0] for idx, obj in enumerate([sunalt, moonalt])]

def initialize():
    global time, sunalt, moonalt
    plots[0].set_data(time[0], sunalt[0])
    plots[1].set_data(time[0], moonalt[0])
#     sun = plt.Circle((time[0], sunalt[0]), sunsize[0])
#     moon = plt.Circle((time[0], moonalt[0]), moonsize[0])
#     ax.add_artist(sun)
#     ax.add_artist(moon)
    
    return plots

def animate(i):
    global time, sunalt, moonalt
    plots[0].set_data(time[i], sunalt[i])
    plots[1].set_data(time[i], moonalt[i])
#     sun = plt.Circle((time[i], sunalt[i]), sunsize[i])
#     moon = plt.Circle((time[i], moonalt[i]), moonsize[i])
#     ax.add_artist(sun)
#     ax.add_artist(moon)
    
    return plots

ax.xaxis.set_ticks_position('both')
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.xaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 15)))
ax.xaxis.set_minor_locator(MinuteLocator(byminute=range(0, 60, 5)))
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
ax.tick_params(axis='both', which='major', direction='in', width=1.6, length=9, labelsize=12)
ax.tick_params(axis='both', which='minor', direction='in', width=0.9, length=5, labelsize=12)

anim = animation.FuncAnimation(fig, animate, frames=len(time), init_func=initialize, interval=24, blit=False)
anim.save('AnnularSolarEclipseJune21_Bengaluru.gif', writer='imagemagick')
