#!/usr/bin/python

import collections
import csv

from cartopy import crs
from cartopy.io import shapereader
from matplotlib import patches
from matplotlib import pyplot
from shapely.geometry import point

COLORS = collections.OrderedDict(
    [('smith', '#d4d7d9'),
     ('miller', '#f3e7a9'),
     ('priest', '#606060'),
     ('imam', '#009000'),
     ('landowner', '#66cc00'),
     ('baker', '#fcd59c'),
     ('hunter', '#927b51'),
     ('sea-warrior', '#006994'),
     ('shepherd', '#165b31'),
     ('skinner', '#dc143c'),
    ])

DEFAULT_COLOR = '#fffff7'
BORDER_COLOR = '#B0B0B0'


class Europe(crs.TransverseMercator):

  def __init__(self):
    super(Europe, self).__init__(
        central_longitude=13,
        central_latitude=49,
        false_easting=self.x_limits[1] / 2.0,
        false_northing=self.y_limits[1] / 2.0)
  
  @property
  def x_limits(self):
    return (0, +4.1e6)
  
  @property
  def y_limits(self):
    return (0, +3.1e6)


def read_surnames():
  result = {}
  with open('surnames.csv') as surnames:
    for row in csv.reader(surnames):
      result[row[0]] = (row[1].decode('utf-8'), row[2])
  return result


def main():
  surnames = read_surnames()
  europe = Europe()
  projection = crs.PlateCarree()
  ax = pyplot.axes(projection=europe)
  kosovo_geometry = None
  for country in shapereader.Reader('ne_110m_admin_0_countries').records():
    country_geometry = country.geometry
    geometry = europe.project_geometry(
        projection.project_geometry(country_geometry))
    if geometry.is_empty:
      continue
    centroid = geometry.centroid
    name = country.attributes['name_long']
    if name == 'Russian Federation':  # Workaround.
      centroid = point.Point(3.6e6, 2.6e6)
    elif name == 'Albania':
      centroid = point.Point(centroid.x, centroid.y - 25e3)
    elif name == 'Bosnia and Herzegovina':
      centroid = point.Point(centroid.x, centroid.y - 67e3)
    elif name == 'Croatia':
      centroid = point.Point(centroid.x, centroid.y + 25e3)
    elif name == 'Kosovo':
      kosovo_geometry = country_geometry
      continue
    elif name == 'Macedonia':
      centroid = point.Point(centroid.x + 100e3, centroid.y)
    elif name == 'Montenegro':
      centroid = point.Point(centroid.x - 100e3, centroid.y)
    elif name == 'Serbia':
      country_geometry = (country_geometry.union(kosovo_geometry),)
    try:
      surname = surnames[name]
      ax.add_geometries(
          country_geometry,
          projection,
          facecolor=COLORS[surname[1]],
          edgecolor=BORDER_COLOR)
      ax.text(
          centroid.x,
          centroid.y,
          surname[0],
          ha='center',
          va='center',
          size=10)
    except KeyError:
      ax.add_geometries(
          country_geometry,
          projection,
          facecolor=DEFAULT_COLOR,
          edgecolor=BORDER_COLOR)
  # Workaround for Catalonia and Kosovo.
  ax.text(1100e3, 800e3, '(Ferrer)', ha='center', va='center', size=9)
  ax.text(2800e3, 850e3, '(Hoxha)', ha='center', va='center', size=9)
  legend_handles = [
      patches.Circle((0.5, 0.5), color=COLORS[k]) for k in COLORS]
  pyplot.figlegend(legend_handles, COLORS.keys(), 'upper left', fontsize=10)
  pyplot.savefig('surnames.png')


if __name__ == '__main__':
  main()
