import calendar


# ------ FUNCTIONS ------
def plot_annual_maps(
    month_ds: xr.Dataset, variable: str, time_str: str = "time", **kwargs
) -> None:
    fig, axs = plt.subplots(3, 4, figsize=(12, 8))
    for i in range(0, 12):
        da = month_ds.isel({time_str: i})[variable]
        ax_ix = np.unravel_index(i, (3, 4))
        ax = axs[ax_ix]
        da.plot(ax=ax, **kwargs)

        ax.set_title(calendar.month_abbr[i + 1])
        ax.set_axis_off()

    return fig, ax


def plot_year(year: str, ds: xr.Dataset, variable: str = "VCI"):
    fig, ax = plot_annual_maps(
        month_ds=ds.sel(time=year),
        time_str="time",
        variable=variable,
        **dict(add_colorbar=False, cmap="RdBu_r", vmin=0, vmax=100),
    )

    fig.suptitle(f"{variable} [{year}]")


# ------ SCRIPT ------
savefig = False


fig, ax = plt.subplots(figsize=(12, 8))

sns.distplot(
    drop_nans_and_flatten(y_train.VCI),
    label="Train Data [1980-2010]",
    kde=False,
    norm_hist=True,
)
sns.distplot(
    drop_nans_and_flatten(y_test.VCI),
    label="Test Data [2011-2018]",
    kde=False,
    norm_hist=True,
)

plt.legend()
ax.set_title("Train vs. Test Data (12 month VCI Predictions)")

if savefig:
    fig = plt.gcf()
    fig.savefig(plot_dir / "train_test_histogram.png")


plot_year("2011", y_train)
if savefig:
    fig = plt.gcf()
    fig.savefig(plot_dir / "2011_spatial_vci_maps.png")

plot_year("1985", y_train)
if savefig:
    fig = plt.gcf()
    fig.savefig(plot_dir / "1985_spatial_vci_maps.png")
