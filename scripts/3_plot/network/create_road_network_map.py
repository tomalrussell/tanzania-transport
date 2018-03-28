"""Generate detailed road network map of Tanzania
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from utils import plot_pop, plot_countries, plot_regions

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

states_filename = os.path.join(data_path, 'Infrastructure', 'Boundaries',
                               'ne_10m_admin_0_countries_lakes.shp')

# Roads
all_road_filename = os.path.join(
    data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')

# Create figure
plt.figure(figsize=(6, 6), dpi=150)

proj_lat_lon = ccrs.PlateCarree()
proj_3857 = ccrs.epsg(3857)
ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)
x0 = 28.6
x1 = 41.4
y0 = 0.5
y1 = -12.5
ax.set_extent([x0, x1, y0, y1], crs=proj_lat_lon)

# Background
plot_countries(ax, data_path)
plot_pop(plt, ax, data_path)
plot_regions(ax, data_path)

# All roads, including trunk
all_road_geoms = [
    record.geometry
    for record in shpreader.Reader(all_road_filename).records()
]

ax.add_geometries(
    all_road_geoms,
    crs=proj_lat_lon,
    linewidth=1,
    edgecolor='#d1170a',
    facecolor='none',
    zorder=2)

# Legend
legend_handles = [
    mpatches.Patch(color='#d1170a', label='TANROADS Trunk and Regional Roads'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)
plt.title('Trunk and Regional Roads in Tanzania')


output_filename = os.path.join(
    base_path,
    'figures',
    'road_network_map_all.png'
)
plt.savefig(output_filename)