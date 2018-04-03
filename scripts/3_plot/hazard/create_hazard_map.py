"""Generate maps of flood hazards
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import shapely.geometry

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

hazard_base_path = os.path.join(
    data_path,
    'tanzania_flood'
)

output_filename = os.path.join(
    figures_path,
    'hazard_map.png'
)

# List of dicts, each with {return_period, filename, model, period}
hazard_file_details = []

# Return periods of interest
return_periods = [5, 1000]

# Global climate models
models = [
    'GFDL-ESM2M',
    'HadGEM2-ES',
    'IPSL-CM5A-LR',
    'MIROC-ESM-CHEM',
    'NorESM1-M',
]

# Current hazards
for return_period in return_periods:
    hazard_file_details.append({
        "return_period": return_period,
        "filename": os.path.join(
            hazard_base_path,
            'EUWATCH',
            'inun_dynRout_RP_{:05d}_Tanzania'.format(return_period),
            'inun_dynRout_RP_{:05d}_contour_Tanzania.tif'.format(return_period)
        ),
        "model": "Current",
        "period": "Current"
    })

# Modelled future hazards (under different GCMs)
for model in models:
    for return_period in return_periods:
        hazard_file_details.append({
            "return_period": return_period,
            "filename": os.path.join(
                hazard_base_path,
                model,
                'rcp6p0',
                '2030-2069',
                'inun_dynRout_RP_{:05d}_bias_corr_masked_Tanzania'.format(return_period),
                'inun_dynRout_RP_{:05d}_bias_corr_contour_Tanzania.tif'.format(return_period)
            ),
            "model": model,
            "period": "2030-2069"
        })


def _plot_labels(ax):
    proj = ccrs.PlateCarree()
    labels = [
        ('Dar-Es-Salaam', 39.1, -6.91),
        ('Pwani', 38.52, -7.43),
        ('Indian', 39.69, -7.68),
        ('Ocean', 39.69, -7.88)
    ]
    for name, cx, cy in labels:
        ax.text(
            cx,
            cy,
            name,
            alpha=0.7,
            size=7,
            horizontalalignment='left',
            transform=proj)

proj = ccrs.PlateCarree()

# Create figure
fig, axes = plt.subplots(
    nrows=2+len(models),
    ncols=len(return_periods),
    subplot_kw=dict(projection=proj),
    figsize=(4, 9),
    dpi=300)

data_with_lat_lon = [get_data(details["filename"]) for details in hazard_file_details]

# Set up colormap and norm
cmap, norm = get_hazard_cmap_norm()

# Extent of area to focus on
zoom_extent = (37.8, 39.6, -8.5, -6.7)

# Plot data to axes
for (ax_num, ax), (data, lat_lon_extent), details in zip(enumerate(axes.flat), data_with_lat_lon, hazard_file_details):
    ax.locator_params(tight=True)
    ax.outline_patch.set_visible(False)

    # x/y labels
    if ax_num < len(return_periods):
        ax.set_title("{}y return".format(details["return_period"]))
    if ax_num % len(return_periods) == 0:
        ax.text(
            -0.07,
            0.55,
            details["model"],
            va='bottom',
            ha='center',
            rotation='vertical',
            rotation_mode='anchor',
            transform=ax.transAxes)

    ax.set_extent(zoom_extent, crs=proj)
    plot_basemap(ax, data_path)
    im = ax.imshow(data, extent=lat_lon_extent, cmap=cmap, norm=norm, zorder=1)
    _plot_labels(ax)

# Add context
for ax_num, ax in enumerate(axes.flat):
    if ax_num == len(hazard_file_details):
        ax.locator_params(tight=True)
        tz_extent = (28.6, 41.4, -0.1, -13.2)
        ax.set_extent(tz_extent, crs=proj)

        plot_basemap(ax, data_path)

        # Zoom extent: (37.5, 39.5, -8.25, -6.25)
        x0, x1, y0, y1 = zoom_extent
        box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
        ax.add_geometries([box], crs=proj, edgecolor='#000000', facecolor='none')

    elif ax_num > len(hazard_file_details):
        ax.locator_params(tight=True)
        ax.outline_patch.set_visible(False)

# Adjust layout
ax_list = list(axes.flat)
plt.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.02, rect=(0, 0.02, 0.98, 1))

hazard_legend(im, ax_list)

# Save
save_fig(output_filename)
