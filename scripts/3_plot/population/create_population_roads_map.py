"""Generate map of population with access to roads
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import shapely.geometry

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

states_filename = os.path.join(data_path, 'Infrastructure', 'Boundaries', 'ne_10m_admin_0_countries_lakes.shp')

# WorldPop TZA_popmap15adj_v2b
population_filename = os.path.join(data_path, 'Infrastructure', 'Population', 'TZA_popmap15adj_v2b_cropped.tif')

# TZ_TransNet_Roads, clipped to Tanzania
trunk_road_filename = os.path.join(data_path, 'Infrastructure', 'Roads', 'Tanroads_flow_shapefiles', 'trunk_roads_2017.shp')
# PMO_TanRoads
regional_road_filename = os.path.join(data_path, 'Infrastructure', 'Roads', 'Tanroads_flow_shapefiles', 'region_roads_2017.shp')

# Route to highlight
route_filename = os.path.join(data_path, 'Infrastructure', 'Roads', 'highlight_route_mwanza.shp')

output_filename = os.path.join(figures_path, 'population_roads_map.png')

# Create figure
plt.figure(figsize=(6, 6), dpi=72)

proj_lat_lon = ccrs.PlateCarree()
ax = plt.axes([0.025, 0, 0.95, 0.95], projection=proj_lat_lon)
x0 = 32.75
x1 = 33.2
y0 = -2.4
y1 = -2.75
zoom_extent = [x0, x1, y0, y1]
ax.set_extent(zoom_extent, crs=proj_lat_lon)
plot_basemap(ax, data_path)

# Read in raster data
data, lat_lon_extent = get_data(population_filename)

# Create color map
colors = plt.get_cmap('viridis_r')
colors.colors[0] = (1, 1, 1, 0)

# Plot population data
im = ax.imshow(data, extent=lat_lon_extent, cmap=colors, zorder=1)

# Add colorbar
cbar = plt.colorbar(im, ax=[ax], drawedges=False, orientation='horizontal')
cbar.outline.set_color("none")
cbar.ax.set_xlabel('Population density (people per grid square)')

# Regional roads
for record in shpreader.Reader(regional_road_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#c4c4c4',
        facecolor='none',
        zorder=3)

# Major roads
for record in shpreader.Reader(trunk_road_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        linewidth=1,
        edgecolor='#1f78b4',
        facecolor='none',
        zorder=4)

# Highlight
for record in shpreader.Reader(route_filename).records():
    geom = record.geometry
    outline = geom.buffer(0.006)
    ax.add_geometries(
        [outline],
        crs=proj_lat_lon,
        linewidth=1,
        edgecolor=(1, 0.7, 0.7, 0),
        facecolor=(1, 0.7, 0.7, 0.4),
        zorder=5)

# Legend
legend_handles = [
    mpatches.Patch(color='#1f78b4', label='Major Roads'),
    mpatches.Patch(color='#c4c4c4', label='Regional Roads'),
    mpatches.Patch(color=(1, 0.7, 0.7, 0.4), label='Route to major node'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

# Add context
ax = plt.axes([0.65, 0.25, 0.35, 0.25], projection=proj_lat_lon)
tz_extent = (28.6, 41.4, -0.1, -13.2)
ax.set_extent(tz_extent, crs=proj_lat_lon)

plot_basemap(ax, data_path)

# Zoom extent: (37.5, 39.5, -8.25, -6.25)
x0, x1, y0, y1 = zoom_extent
box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
ax.add_geometries([box], crs=proj_lat_lon, edgecolor='#000000', facecolor='#d7d7d700')


# Save
plt.savefig(output_filename)
