ESoWC: Predicting Vegetation Health in Kenya using Machine Learning and Climate data.

**Thomas Lees1**, Gabriel Tseng2, Steven Reece1, Simon Dadson1
1 University of Oxford
2 Okra Solar

As part of the ECMWF Summer of Weather Code we have developed a machine learning pipeline for working with climate and hydrological data. The pipeline uses data from the Climate Data Store, the Copernicus-ECMWF service for accessing weather and climate data. For our application of the pipeline we focused on providing predictions of agricultural drought one month ahead. In Kenya, the National Drought Management Authority (NDMA) distributes emergency funds through the Drought Contingency Fund. These funds are distributed based on a threshold value of a vegetation health index. For this work we use the same index to demonstrate the potential for predicting vegetation health prior to observations. This offers the potential to reduce the impacts of droughts by allowing disaster response mechanisms to act proactively. We first compared multiple machine learning algorithms. Once we selected the best performing model (the EALSTM - Kratzert et al. 2019) we then completed a deeper comparison against a persistence baseline and to a recent paper implementing Vegetation Health predictions (Adede et al 2019).

Adede, C., Oboko, R., Wagacha, P. W., & Atzberger, C. (2019). A mixed model approach to vegetation condition prediction using Artificial Neural Networks (ANN): Case of Kenya’s operational drought monitoring. Remote Sensing, 11(9). https://doi.org/10.3390/rs11091099

Kratzert, F., Klotz, D., Shalev, G., Klambauer, G., Hochreiter, S., Nearing, G., "Benchmarking
a Catchment-Aware Long Short-Term Memory Network (LSTM) for Large-Scale Hydrological Modeling".
submitted to Hydrol. Earth Syst. Sci. Discussions (2019)
