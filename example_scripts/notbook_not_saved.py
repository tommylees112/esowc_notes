df = e.exceedences.sum(dim=['lat','lon']).to_dataframe()

fig, ax = plt.subplots(1, 2, figsize=(16, 4))
df.plot(ax=ax[0])
df.rolling(window=24).mean().rename(columns={'SPI3': 'SPI3 2yr rolling average'}).plot(ax=ax[0])
ax[0].set_title('Sum of Pixels Flagged at each timestep')

df2 = chirps.rolling(time=3).mean(dim=['lat', 'lon']).to_dataframe()
df2.plot(ax=ax[1])
df2.rolling(window=24).mean().rename(columns={'precip': '2yr rolling average mean precip'}).plot(ax=ax[1])
ax[1].set_title('Mean Precip (ov
er space)')
