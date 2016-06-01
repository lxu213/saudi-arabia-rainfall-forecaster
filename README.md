# saudi-arabia-rainfall

Synthetic rainfall forecasting model for the Kingdom of Saudi Arabia

This project is a personal and independent effort to re-create and improve upon a proprietary Fortran model. The goal is to gain experience with Python programming and its associated data analysis libraries (numpy, pandas, scipy, matplotlib, etc). 

The synthetic rainfall forecaster uses 30-years of historical rainfall data to model significant characteristics:

1. Rainfall intensity: characterized by depth of individual storm events, sampled using a bootstrap method, drawback is that it fails to capture extreme events not existent in the historical data.

2. Seasonality: characterized by frequency of rain events per month, follows a poisson distribution.

3. Clustering of storm events: characterized by a series of conditional probabilities.
