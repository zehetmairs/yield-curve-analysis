
# ============================================================
# 1. Imports and ECB data download
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO


url = (
    "https://data-api.ecb.europa.eu/service/data/YC/"
    "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y+SR_2Y+SR_5Y+SR_10Y+SR_20Y+SR_30Y"
    "?format=csvdata&lastNObservations=5"
)


try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = pd.read_csv(StringIO(response.text))

    if data.empty:
        raise ValueError("The ECB API returned no data.")

    print("ECB data downloaded successfully.")

except (requests.RequestException, ValueError) as error:
    print(f"Error downloading or reading ECB data: {error}")
    raise



# ============================================================
# 2. Data preparation
# ============================================================

data = data[["TIME_PERIOD", "KEY", "OBS_VALUE"]]

data = data.rename(columns={
    "TIME_PERIOD": "Date",
    "KEY": "Yield_Type",
    "OBS_VALUE": "Yield"
})

data["Maturity"] = (
    data["Yield_Type"].str.extract(r"SR_(\d+)Y").astype(int)
)

data = data.sort_values(["Date", "Maturity"])

print("\nECB Yield Data")
print(data[["Date", "Maturity", "Yield"]])


# ============================================================
# 3. Yield curve comparison
# ============================================================

old_date = "2026-10-23"
new_date = "2026-10-27"

comparison_dates = [old_date, new_date]

plt.figure(figsize=(9, 5))

for date in comparison_dates:
    curve = data[data["Date"] == date].sort_values("Maturity")

    plt.plot(
        curve["Maturity"],
        curve["Yield"],
        marker="o",
        label=date
    )

plt.title("Euro Area Yield Curve: 23 Oct vs 27 Oct 2026")
plt.xlabel("Maturity (Years)")
plt.ylabel("Yield (% per annum)")
plt.xticks(sorted(data["Maturity"].unique()))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 4. Yield changes between the two dates
# ============================================================

old_curve = data[data["Date"] == old_date][["Maturity", "Yield"]]
new_curve = data[data["Date"] == new_date][["Maturity", "Yield"]]

comparison = old_curve.merge(
    new_curve,
    on="Maturity",
    suffixes=("_Old", "_New")
)

comparison["Change_bps"] = (
    comparison["Yield_New"] - comparison["Yield_Old"]
) * 100

print("\nYield Changes")
print(comparison[
    ["Maturity", "Yield_Old", "Yield_New", "Change_bps"]
].round(2))


plt.figure(figsize=(9, 5))

plt.bar(
    comparison["Maturity"].astype(str) + "Y",
    comparison["Change_bps"]
)

plt.axhline(y=0, color="black", linewidth=0.8)
plt.title("Yield Changes: 23 Oct to 27 Oct 2026")
plt.xlabel("Maturity")
plt.ylabel("Change (basis points)")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 5. 2s10s spread analysis
# ============================================================

spread_data = data[data["Maturity"].isin([2, 10])].pivot(
    index="Date",
    columns="Maturity",
    values="Yield"
)

spread_data["2s10s_Spread"] = (
    spread_data[10] - spread_data[2]
) * 100

spread_old = spread_data.loc[old_date, "2s10s_Spread"]
spread_new = spread_data.loc[new_date, "2s10s_Spread"]

print("\n2s10s Spread")
print(f"{old_date}: {spread_old:.2f} bps")
print(f"{new_date}: {spread_new:.2f} bps")
print(f"Change: {spread_new - spread_old:.2f} bps")

print("\n2s10s Spread over Time")
print(spread_data[["2s10s_Spread"]].round(2))


plt.figure(figsize=(9, 5))

plt.plot(
    spread_data.index,
    spread_data["2s10s_Spread"],
    marker="o"
)

plt.title("Euro Area 2s10s Yield Spread")
plt.xlabel("Date")
plt.ylabel("Spread (basis points)")
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 6. Bond valuation
# ============================================================

def bond_price(face_value, coupon_rate, yield_to_maturity, years):
    annual_coupon = face_value * coupon_rate
    price = 0

    for year in range(1, years + 1):
        price += annual_coupon / (1 + yield_to_maturity) ** year

    price += face_value / (1 + yield_to_maturity) ** years

    return price


latest_date = data["Date"].max()

market_yield = data.loc[
    (data["Date"] == latest_date) &
    (data["Maturity"] == 5),
    "Yield"
].iloc[0] / 100

face_value = 100
coupon_rate = 0.03
years = 5

price = bond_price(
    face_value,
    coupon_rate,
    market_yield,
    years
)

print("\nBond Valuation")
print(f"Date: {latest_date}")
print(f"Market yield: {market_yield * 100:.3f}%")
print(f"Bond price: {price:.4f}")


# ============================================================
# 7. Interest rate risk and modified duration
# ============================================================

yield_change = 0.0001  # 1 basis point

price_after_shock = bond_price(
    face_value,
    coupon_rate,
    market_yield + yield_change,
    years
)

price_change = price_after_shock - price
price_change_bps = price_change / price * 10000

modified_duration_estimate = -(
    price_change / price
) / yield_change

print("\nInterest Rate Risk")
print(f"Original price: {price:.4f}")
print(f"Price after +1 bp yield move: {price_after_shock:.4f}")
print(f"Price change: {price_change:.6f}")
print(f"Relative price change: {price_change_bps:.4f} bps")

print("\nModified Duration Estimate")
print(f"Estimated modified duration: {modified_duration_estimate:.4f} years")


# ============================================================
# 8. Direct duration calculation from cash flows
# ============================================================

cash_flows = []

for year in range(1, years + 1):
    cash_flow = face_value * coupon_rate

    if year == years:
        cash_flow += face_value

    cash_flows.append(cash_flow)


present_values = []

for year, cash_flow in enumerate(cash_flows, start=1):
    present_value = cash_flow / (1 + market_yield) ** year
    present_values.append(present_value)


macaulay_duration = sum(
    year * present_value
    for year, present_value in enumerate(present_values, start=1)
) / sum(present_values)

modified_duration_direct = macaulay_duration / (1 + market_yield)

print("\nDuration Comparison")
print(f"Macaulay duration: {macaulay_duration:.4f} years")
print(f"Modified duration (direct): {modified_duration_direct:.4f} years")
print(f"Modified duration (1 bp estimate): {modified_duration_estimate:.4f} years")


# ============================================================
# 9. Bond convexity
# ============================================================

yield_shift = 0.01  # 100 basis points

price_up = bond_price(
    face_value, coupon_rate, market_yield + yield_shift, years
)

price_down = bond_price(
    face_value, coupon_rate, market_yield - yield_shift, years
)

convexity = (
    price_down + price_up - 2 * price
) / (price * yield_shift ** 2)

actual_change_up = (price_up - price) / price
actual_change_down = (price_down - price) / price

duration_change_up = -modified_duration_direct * yield_shift
duration_change_down = modified_duration_direct * yield_shift

print("\nBond Convexity")
print(f"Convexity: {convexity:.4f}")
print(f"Price change for +100 bp: {actual_change_up * 100:.2f}%")
print(f"Duration estimate for +100 bp: {duration_change_up * 100:.2f}%")
print(f"Price change for -100 bp: {actual_change_down * 100:.2f}%")
print(f"Duration estimate for -100 bp: {duration_change_down * 100:.2f}%")
