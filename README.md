
# Yield Curve Analysis & Interest Rate Risk

## Overview

This project analyses euro area government yield curve data published by the European Central Bank (ECB). It explores changes in yields across maturities and examines how interest rate movements affect fixed-income bond prices.

The project combines market data analysis with basic fixed-income valuation and risk measurement using Python.

## Key Features

- **ECB Data Retrieval:** Downloads yield curve observations from the ECB Data Portal.
- **Yield Curve Analysis:** Compares yield curves across dates to identify changes in their shape.
- **Yield Changes:** Calculates yield movements across maturities in basis points.
- **2s10s Spread:** Tracks the difference between 10-year and 2-year yields as a measure of yield curve steepness.
- **Bond Valuation:** Prices a hypothetical fixed-rate bond using discounted cash flows.
- **Interest Rate Risk:** Estimates modified duration and analyses the impact of yield shocks.
- **Convexity:** Examines the limitations of duration-based price change estimates for larger yield movements.

## Data Source

European Central Bank (ECB) Data Portal.

The analysis uses euro area government bond yield curve observations for maturities of 1, 2, 5, 10, 20 and 30 years.

## Methodology

### Yield Curve Analysis

Yield changes are calculated in basis points:

Change in yield (bps) = (New yield − Old yield) × 100

The 2s10s spread is calculated as:

2s10s spread (bps) = (10-year yield − 2-year yield) × 100

### Bond Valuation

The project values a hypothetical five-year bond with a face value of 100 and an annual coupon rate of 3%.

Bond prices are calculated by discounting the annual coupon payments and the principal repayment at the selected market yield.

### Interest Rate Risk

Modified duration is estimated using the price change resulting from a small yield shock and compared with a direct duration calculation based on discounted cash flows.

Convexity is approximated using prices calculated at yields above and below the current market yield. This illustrates why duration alone becomes less accurate for larger yield movements.

## Tools

- Python
- pandas
- NumPy
- Matplotlib
- requests

## Disclaimer

This project is for educational purposes only. The bond valuation uses simplified assumptions, including annual coupon payments and a single market yield for discounting all cash flows. It is not intended as investment advice or as a complete representation of professional bond pricing.
