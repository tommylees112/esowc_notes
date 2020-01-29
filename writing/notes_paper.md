These tools have the potential to improve the timeliness of emergency fund distribution. Existing methods use near-real time .
False positives are determined to be less severe than false negatives.

The Kenyan National Drought Management Authority (NDMA) distributes emergency funds through the Drought Contingency Fund. These funds are help available to counties in Kenya and have been distributed since 2014 \citep{Klisch2016}. Timeliness is key to the successful mitigation of a drought event. Near real time information is useful, however, a pre-emptive approach is

We compare our results to a commonly used baseline model (persistence) and to the current state of the art reported by \citet{kenya_operational}.
================================================================================

• emphasise the impact
• rewording to the SOTA
• decide whether to discuss shap results

Tommy, Gabi, Jian, Olga, Simon, Steve

- changing the title to reflect the call
- Mitigating the impact of drought on vegetation health: an ML based approach
- title and abstract using the information from the call more explicitly.

building a model vs. existing approaches that have to observe the current status
- take future hydrological scenarios which can then derive what vegetation health might be
- multi-disciplinary envrionment is critical // background in geography and now working with ML envrionment to transfer the technology to use cases
- Reference the IPP: as an example of that we're working with commercial partners etc. to achieve impact (participatory design)


- relevance of different features
- need some results or plots etc.

- Give results in terms of the features that are relevant / important
- One of the key contributions of this approach so make sure it's actually included and written about.



<!-- taken out -->
@misc{era5,
  author={Copernicus Climate Change Service (C3S)},
  title={ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate},
  year={2017},
  howpublished={\url{https://cds.climate.copernicus.eu/cdsapp#!/home}}
}


<!-- Done -->
Abstract
all / abstract
- focus more on adaptation
- providing a model that might use a stronger implementation (ABSTRACT)
- crop health linked with people's welfare / famines / starvation etc.

Introduction
comparison to sota
- include references of in country current SOTA that they use for climate change adaptation
- an existing method in country
- payments early vs. payments now
- find someone saying that these payments going out way too late
- (VIVID?)
- share with Airbus? (speak with Simon)


Data and Methods
- move the sentence after to the end.

- what is the difference with the EALSTM
- moderates the input data which dynamic data is kept by the long term memory (Cell State $C$)
- what differs with your implmentation of our model and the Kratzert 2019 model
- (add dropout)
- changing input data (which bits are important?)
- generating adaptation maps (what will they look like in future conditions?)
- SPEI etc.

- Which cost function does our model use?
- use the cost function that we are validating the scores on to get better results
- if using RMSE as cost function
- mention the cost function that we're using
- "this method uses an RMSE cost function"

- if simpler model
- use a Kalman Filter / Random Forest / GP ...
- any regression model
- "we chose the LSTM because it had better performance compared to ..."
- cite specific implementations of these methods (plot of intercomparison of methods)

- "LINEAR LAYER" -> through a RELU (remove the )
- final sentence at the start of the paper!


Results


Conclusion
- present a new method with significant improvemnet over existing
- vegetation health which can be used for adaptation to climate change
- conditioned on ability to make climate scenarios in the future

Acknowledgements
- Work primarily funded through ECMWF summer of weather code project // standard IPP approval
