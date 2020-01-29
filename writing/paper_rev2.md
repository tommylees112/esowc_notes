Introduction


Figures
- separate a little bit in the middle
- using tabular package? There is the `hspace` command and the `&&`



Table
- Does the Adede et al work encode region specific data (NO)
- Adede doesnt have region specific information in the model and their Turkana performance is better so how can we say that the lack of region speciifc information is the cause of our poor performance
- (good point but the landcover performance is still an open area)

Results and Analysis
- Shapley values comparison to the baseline
    - make it clearer that the Shapley value is relative to a baseline
    - Steve felt it was implied that there are a baseline set of gradients that we are comparing the model to (this isn't true is it? Its only the mean prediction we are comparing to not a mean set of gradients that we differ from?)
- REJIG relative to the Lundberg Paper (Tommy to read lundberg paper closely to try and write a clear)

Conclusions
- "fold in hydro-meteorological forecasts to improve vegetation health predictions"

Acknowledgements (???)
Primarily supported by ECMWF's Summer of Weather Code project. S Reece is funded by the Alan Turing Institute’s Data Centric Engineering programme and, with O Isupova, through the UKSA's International Partnerships Programme.

<!-- Done -->
Introduction
- Kogan et al drought monitoring
- citation of the paper
- Why will it be an 'important' hazard in future decades?
    - With climate change drought becoming more prolific with intensity
- why is it challenging to model in E africa?
    - modelling, getting the data, understanding, complex interrelationships
- example crop yield, malnutrition etc.
- (humanitarian)

Data and methods
- Kogan et al drought monitoring
- citation of the paper

- final paragraph of EALSTM model
- "we track the vegetation health trend, i.e. mean veg health over the entire region, and also model the local deviations from that trend"
- input comprises the
- due to the seasonal cycle, our predictions are month specific. Therefore we used one hot encoded ...
- Input includes the mean vegetation health across the entire region and for each month.  Also,  a map showing monthly averaged local deviations about the spatial mean is input.


Results and Analysis

table
- BOLD font best results per row
- Aggregated / unaggregated in the column headers

Conclusions



<!-- bibtex -->

@techreport{Kogan2001,
abstract = {The main goal of global agriculture and the grain sector is to feed 6 billion people. Frequent droughts causing grain shortages, economic disturbances, famine, and losses of life limit the ability to fulfill this goal. To mitigate drought consequences requires a sound early warning system. The National Oceanic and Atmospheric Administration (NOAA) has recently developed a new numerical method of drought detection and impact assessment from the NOAA operational environmental satellites. The method was tested during the past eight years, adjusted based on users' responses , validated against conventional data in 20 countries, including all major agricultural producers, and was accepted as a tool for the diagnosis of grain production. Now, drought can be detected 4-6 weeks earlier than before, outlined more accurately, and the impact on grain reduction can be predicted long in advance of harvest, which is most vital for global food security and trade. This paper addresses all these issues and also discusses ENSO impacts on agriculture.},
author = {Kogan, Felix N},
file = {:Users/tommylees/Library/Application Support/Mendeley Desktop/Downloaded/Kogan - Unknown - Operational Space Technology for Global Vegetation Assessment.pdf:pdf},
mendeley-groups = {ESoWC},
title = {{Operational Space Technology for Global Vegetation Assessment}},
url = {https://journals.ametsoc.org/doi/pdf/10.1175/1520-0477{\%}282001{\%}29082{\%}3C1949{\%}3AOSTFGV{\%}3E2.3.CO{\%}3B2}
}

@misc{AghaKouchak2015,
abstract = {This review surveys current and emerging drought monitoring approaches using satellite remote sensing observations from climatological and ecosystem perspectives. We argue that satellite observations not currently used for operational drought monitoring, such as near-surface air relative humidity data from the Atmospheric Infrared Sounder mission, provide opportunities to improve early drought warning. Current and future satellite missions offer opportunities to develop composite and multi-indicator drought models. While there are immense opportunities, there are major challenges including data continuity, unquantified uncertainty, sensor changes, and community acceptability. One of the major limitations of many of the currently available satellite observations is their short length of record. A number of relevant satellite missions and sensors (e.g., the Gravity Recovery and Climate Experiment) provide only a decade of data, which may not be sufficient to study droughts from a climate perspective. However, they still provide valuable information about relevant hydrologic and ecological processes linked to this natural hazard. Therefore, there is a need for models and algorithms that combine multiple data sets and/or assimilate satellite observations into model simulations to generate long-term climate data records. Finally, the study identifies a major gap in indicators for describing drought impacts on the carbon and nitrogen cycle, which are fundamental to assessing drought impacts on ecosystems.},
author = {AghaKouchak, A. and Farahmand, A. and Melton, F. S. and Teixeira, J. and Anderson, M. C. and Wardlow, B. D. and Hain, C. R.},
booktitle = {Reviews of Geophysics},
doi = {10.1002/2014RG000456},
file = {:Users/tommylees/Library/Application Support/Mendeley Desktop/Downloaded/AghaKouchak et al. - 2015 - Remote sensing of drought Progress, challenges and opportunities.pdf:pdf},
isbn = {1944-9208},
issn = {19449208},
keywords = {drought,remote sensing},
mendeley-groups = {Drought Remote Sensing},
month = {jun},
number = {2},
pages = {452--480},
title = {{Remote sensing of drought: Progress, challenges and opportunities}},
url = {http://doi.wiley.com/10.1002/2014RG000456},
volume = {53},
year = {2015}
}

Carrer del Corb Marí, 4, 07470 Port de Pollença, Illes Balears, Spain

<!-- REmoved -->
Abstract
Vegetation health (and therefore agricultural drought) prediction remains challenging, especially in East Africa. Agricultural droughts can exacerbate poverty, lead to famine, and ultimately starvation. Timely distribution of disaster relief funds is essential to help minimise the impact of drought. Furthermore, the relative contribution of different climate variables to drought extent and severity is poorly understood. Current methods predict vegetation health averaged over large areas. We develop an Entity-Aware LSTM to forecast pixel-wise vegetation health, and use machine learning interpretability tools to explore the relationships between climate variables and vegetation health.


Introduction
Our contribution is twofold. First, we apply the entity-aware long short term memory network (EA-LSTM) to predict drought conditions, defined by VCI \citep{vhi}. Second, we leverage tools from interpretable machine-learning to investigate the patterns the models are learning and use these insights to better understand the drivers of drought. We chose an agricultural drought index because it is closer to the human impacts of drought, such as damaged crop yields, than hydro-meteorological indices \citep{AghaKouchak2015}.

We apply the entity-aware long short term memory network (EA-LSTM) to predict drought conditions, defined by VCI. EA-LSTMs were first used for rainfall-runoff modelling by \citet{ealstm}. They allow for the processing of dynamic data to be conditioned on a static input and are thus well suited to drought prediction, where both dynamic information (e.g. precipitation, temperature) and static information (e.g. topography) are important.


Data and methods

Results and Analysis

Climate change is expected to make droughts more frequent, as variability of precipitation and temperature extremes increases \citep{IPCC2013}.

Understanding features in this way has two advantages. Firstly, they allow us to validate the basic patterns being learnt by the model. For instance, plotting shap values in Figure \ref{shap_values_plot}(b) allows us to confirm our intuitions that more recent information is more relevant. Secondly, relationships between climate variables and drought are still poorly understood (\citep{Haile2019}) - such techniques may allow us to better understand the relationships between these climate variables and drought.


Conclusions

To communicate regional trends to the model  (in addition to the local trends being communicated by the pixel-wise input data), all variables were aggregated spatially for each month (added to the dynamic data) and spatially across all timesteps (added to the static data). In addition, large differences in the overall distribution of VCI values were observed from month to month. A one hot encoding of the month being predicted is therefore also passed to the model, as a static variable, to allow month-specific patterns to be learned.
