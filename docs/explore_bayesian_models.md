----------------------------------------
Brady et al.
Q: whether climate indices can describe the observed variability in the frequency of flooding in river networks
Q: We investigate whether trends detected in peak river flows can be related to large-scale climate indices (which are proxies for climate variability)

- model that pools the information across stations, which may help to better detect signals that cannot be found using at-site analysis
- including a spatial random effect to account for this similarity between nearby stations in the multilevel models
- correlation-based approach, which can be used generally in any spatial setting, particularly for scenarios where measurement locations are fixed and the spatial domain is not continuous
(but my spatial domain IS continuous?)
- stationary correlation structure is that the correlation between sites i and j decreases as the distance between them increases.

Covariance matrix:
- This purely spatial correlation function depends on the locations through the Euclidean spatial distance dij only, so that for gauging stations i and j
$\Sigma { i j } = \eta ^ { 2 } \exp \left( \frac { - d { i j } } { \rho } \right)$
rho = range over which sites correlate
nu = marginal standard deviation controlling the magnitude of this range
Euclidean distance between the centroid

Ideas:
- Look at catchments / use the basin river data from Feyera to do the same study as theirs

----------------------------------------
Anderson & Ward: Black swans in space: modeling spatiotemporal processes with extremes

What q to answer:
- Bayesian predictive-process GLMM (generalized linear mixed-effects model) that uses a mul- tivariate-t distribution to describe spatial random effects

Squared exponential covariance function
- correlation between points i and j
- $H \left( \delta { i j } \right) = \exp \left( - \delta { i j } ^ { 2 } / 2 \theta _ { \mathrm { GP } } \right)$

- # building the covariance matrix:
- m knot locations = spatial variance parameter $sigma^2_{GP}$ scaling the amplitude
- \Sigma { i j } ^ { * } = \sigma { \mathrm { GP } } ^ { 2 } \exp \left( - \delta { i j } ^ { 2 } / 2 \theta { \mathrm { GP } } \right)


What they did:
- robust spatial predictive models using the MVT distribution
- estimate a spatial field as correlated random effects at a subset of locations or m “knots”

General:
- Spatial relation- ships can be included as predictors in models of the mean (e.g., a two-dimensional GAM) or can be included in models of the covariance (e.g., kriging)
----------------------------------------


----------------------------------------
