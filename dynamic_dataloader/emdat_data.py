"""
Metadata:
--------
Country                              object
ISO                                  object
Location                             object
Latitude                            float64
Longitude                           float64

df.ISO can be used to join to NaturalEarth country data
df.Location has the sub-national information of where they occured
df['Disaster name'] is all nan

Magnitude value                     float64
Magnitude scale                      object
df['Magnitude value'] is Km2 (area of the drought)

Impacts:
-------
Disaster type                        object
Disaster subtype                     object
Associated disaster                  object
Associated disaster2                 object
df['Associated disaster'] has the effects of drought
(e.g. 'Food shortage', '--', 'Water shortage', 'Famine', ..)

Total deaths                        float64
Total affected                      float64
Total damage ('000 US$)             float64
Insured losses ('000 US$)           float64
"""
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib

df = pd.read_csv(Path('/Users/tommylees/Downloads/Thomas_Lees_2020-04-06.csv'),
                 encoding="ISO-8859-1", skiprows=1)
df = df.iloc[:745]
df = df.rename(columns=dict(
    zip(df.columns, [c.lower().replace(' ', '_') for c in df.columns])))
df = df.rename(
    columns={
        "total_damage_('000_us$)": "total_damage",
        "insured_losses_('000_us$)": "insured_losses",
    }
)

df['start_date'] = (
    df['start_date']
    .str.split('/')
    .apply(
        lambda x: pd.to_datetime(
            f"01-{x[-2] if x[-2] != '' else '01'}-{x[-1]}"
        )
    )
)
df['end_date'] = (
    df['end_date']
    .str.split('/')
    .apply(
        lambda x: pd.to_datetime(
            f"01-{x[-2] if x[-2] != '' else '01'}-{x[-1]}"
        )
    )
)

ts = df.set_index('start_date')
ts = ts.sort_index()

# Number of events
fig, ax = plt.subplots()
ts['total_damage'].resample('Y').count().plot(ax=ax, label='Number of Drought Events')  #  .loc['1900':]


# smooth
counts = ts['total_damage'].resample('Y').count()

fig, ax = plt.subplots()
sns.regplot(
    x=[_ for _ in range(len(counts.index))], y=counts, ci=None, order=2,
    ax=ax
)
ax.set_ylabel("Total Damage [US$]")
ax.set_xlabel("Time")
ax.set_title("Disasters of Disaster Type 'Drought'\n[EM-DAT, 2020]")

ax.set_xticklabels(['n'] + [y for y in counts.index.year][::20] + [2020, 'n'])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks('off')
ax.set_xlim([1905, ax.get_xlim()[-1]])


 # Total damage per year
fig, ax = plt.subplots()
ts['total_damage'].loc['1970':].resample('Y').sum().plot(
    ax=ax, label='Total Damage', color='grey', alpha=0.7
)
ax.set_ylabel("'000 US$")
ax.set_xlabel("Date")
ax.legend()

plt.close('all')


# autocorrelation plot
data = array([0.68907819,  1.14908341,  0.74573044,  1.99786822,  2.08387388,
       0.86520613,  0.8681725,  1.25112751,  0.77855304,  0.30546729,
       -0.40697673,  0.94476062,  0.97069661,  1.54981376,  1.07923896,
       -0.71829616,  1.97347818, -0.54002537,  1.18943004, -0.43593158,
       -0.21411656, -0.62018154, -1.36119084, -0.60269301, -0.60087269,
       -1.08884941, -1.52359836, -1.40371103])
data.index = pd.date_range('2000', periods=28, freq='M')
data.loc[pd.to_datetime('2002-05-31')] = -1.5
data = data.rename(columns={'value': 'VCI'})

fig, ax = plt.subplots(figsize=(12, 8))
# (data).resample('D').interpolate()
data.plot(ax=ax)
ax.axhline(-1, color='k', ls='--', alpha=0.7, label='Payment Threshold')

ax.set_title('Wajir - Vegetation Condition Index')

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.legend(loc='upper right', fontsize=14)
ax.set_yticklabels(np.arange(0, 100, 10))
ax.set_ylabel('Vegetation Condition Index')
ax.set_xlabel('Time')

for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]
             + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(16)

# add in future scenarios?
pd.DataFrame({
    'Scenario 1': np.array([data.iloc[-1].values[0], -1.0, -0.8]),
    'Scenario 2': np.array([data.iloc[-1].values[0], -0.5, -0.2]),
    'Scenario 3': np.array([data.iloc[-1].values[0], -1.5, -1.3]),
    'Scenario 4': np.array([data.iloc[-1].values[0], -1.8, -2.1]), },
    index=pd.date_range('2002-05-31', '2002-07-31', freq='M')).plot(ax=ax)
