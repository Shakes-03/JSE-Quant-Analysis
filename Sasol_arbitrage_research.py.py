import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. Download Sasol data
# We'll get 2 years of daily data
sasol = yf.download("SOL.JO", start="2024-01-01")

# 2. Look at the "Raw" data (The first 5 days)
print("--- Sasol Price Data (First 5 Days) ---")
print(sasol.head())

# 3. Create a professional Chart
plt.figure(figsize=(12, 6))
plt.plot(sasol['Close'], label="SOL.JO Close Price", color='#1f77b4')

# Add the "Geopolitical Context" - Let's mark a point
plt.title("Sasol (SOL.JO) - 2-Year Historical Trend")
plt.xlabel("Date")
plt.ylabel("Price (ZAR)")
plt.grid(True, alpha=0.3)
plt.legend()
# Calculate a 50-day moving average
sasol['MA50'] = sasol['Close'].rolling(window=50).mean()

# Add it to the plot
plt.plot(sasol['MA50'], label="50-Day Trend (Smoothing)", color='orange', linestyle='--')
plt.legend() # Refresh the legend to show the new line
plt.show()

# 1. Zoom in on the most recent 60 days so it's not too crowded
recent_sasol = sasol.tail(60)

plt.figure(figsize=(12, 6))

# 2. Plot both Open and Close
plt.plot(recent_sasol.index, recent_sasol['Open'], label="Opening Price", color='gray', linestyle='--', alpha=0.6)
plt.plot(recent_sasol.index, recent_sasol['Close'], label="Closing Price", color='#1f77b4', linewidth=2)

# 3. Highlight the "Gaps"
plt.title("Sasol (SOL.JO): Opening vs. Closing (Last 60 Days)")
plt.ylabel("Price (ZAR)")
plt.legend()
plt.grid(True, alpha=0.2)
plt.show()

import yfinance as yf
import mplfinance as mpf

# 1. Download the data
sasol = yf.download("SOL.JO", period="1y")

# 2. THE FIX: Flatten the MultiIndex columns
# This collapses 'Price' and 'Open' into just 'Open'
sasol.columns = sasol.columns.get_level_values(0)

# 3. Double-check for missing values (NaNs) and drop them
sasol = sasol.dropna()

# 4. Now run the plot
if not sasol.empty:
    print("✅ Data flattened and ready.")
    mpf.plot(sasol.tail(50), 
             type='candle', 
             style='charles', 
             title="Sasol (SOL.JO) - Flattened Analysis",
             ylabel="Price (ZAR)",
             volume=True, 
             mav=(10, 20))
else:
    print("❌ No data found. Check the ticker or connection.")


    # 1. Calculate the percentage change from day to day
sasol['Daily_Return'] = sasol['Close'].pct_change() * 100

# 2. Plot a Histogram of these returns
plt.figure(figsize=(10, 5))
sasol['Daily_Return'].hist(bins=50, color='seagreen', edgecolor='black')
plt.title("Sasol Daily Returns Distribution (%)")
plt.xlabel("Return %")
plt.ylabel("Frequency")
plt.show()

# 3. Print the 'Risk' stats
print(f"Sasol Average Daily Move: {sasol['Daily_Return'].mean():.2f}%")
print(f"Sasol Volatility (Std Dev): {sasol['Daily_Return'].std():.2f}%")

sasol['Daily_Return'].kurt()

import yfinance as yf
import matplotlib.pyplot as plt

# 1. Download both together
# BZ=F is Brent Crude Oil
tickers = ["SOL.JO", "BZ=F"]
data = yf.download(tickers, period="6mo")

# 2. Select only the 'Close' prices
# In Python 3.14/Pandas 3.x, we specify the 'Price' level
close_prices = data['Close']

# 3. Handle the flattening for the new yfinance format
if isinstance(close_prices.columns, pd.MultiIndex):
    close_prices.columns = close_prices.columns.get_level_values(0)

# 4. Drop any rows where data is missing (NaN)
close_prices = close_prices.dropna()

# 5. NORMALIZE: (Price / Start Price) * 100
# This makes both start at 100 so we can see the % change comparison
normalized = (close_prices / close_prices.iloc[0]) * 100

# 6. Plot the comparison
normalized.plot(figsize=(12, 6))
plt.title("Correlation: Sasol vs. Brent Crude Oil (Normalized)")
plt.ylabel("Price Index (Starts at 100)")
plt.grid(True, alpha=0.3)
plt.show()

# 7. The Mathematical Proof
correlation = close_prices['SOL.JO'].corr(close_prices['BZ=F'])
print(f"--- Quant Result ---")
print(f"Correlation: {correlation:.2f}")

# 1. Calculate the correlation (The 'Math' part)
correlation = close_prices['SOL.JO'].corr(close_prices['BZ=F'])

# 2. Print it to your Terminal
print("\n" + "="*30)
print(f"QUANT RESULT: Correlation is {correlation:.4f}")
print("="*30)

# 3. Add a visual guide (Optional but helpful)
if correlation > 0.75:
    print("ANALYSIS: High Correlation. Geopolitics & Oil are the primary drivers.")
elif correlation > 0.40:
    print("ANALYSIS: Moderate Correlation. Check the Rand (ZAR) or Debt levels.")
else:
    print("ANALYSIS: Low Correlation. Internal Sasol factors (Debt/Management) dominate.")
# Shift Sasol's data by 1 day to see if it correlates BETTER with YESTERDAY'S oil
lagged_correlation = close_prices['SOL.JO'].shift(-1).corr(close_prices['BZ=F'])

print(f"Current Correlation: {correlation:.4f}")
print(f"Lagged Correlation (Oil leading Sasol): {lagged_correlation:.4f}")

import seaborn as sns

plt.figure(figsize=(8, 8))
sns.regplot(x=close_prices['BZ=F'], y=close_prices['SOL.JO'], 
            scatter_kws={'alpha':0.5}, line_kws={'color':'red'})

plt.title(f"Quant Analysis: Sasol vs Oil (Corr: {correlation:.4f})")
plt.xlabel("Brent Crude Price ($)")
plt.ylabel("Sasol Price (ZAR)")
plt.grid(True)
plt.show()

# --- 1. DATA EXTRACTION ---
# Tickers: Sasol (JSE), Brent Crude (Oil), and USD/ZAR (The Rand)
tickers = ["SOL.JO", "BZ=F", "USDZAR=X"]
print("Downloading market data...")
data = yf.download(tickers, period="6mo")['Close']

# --- 2. DATA CLEANING ---
# Flatten headers if yfinance returns them in multiple rows
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# Drop any days where markets were closed (NaN values)
data = data.dropna()

# --- 3. THE MULTI-FACTOR VISUAL ---
# Normalize to 100 so they all start at the same point on the graph
normalized = (data / data.iloc[0]) * 100

plt.figure(figsize=(12, 6))
plt.plot(normalized['SOL.JO'], label="Sasol (SOL.JO)", linewidth=2, color='orange')
plt.plot(normalized['BZ=F'], label="Brent Crude Oil", linestyle='--', alpha=0.8)
plt.plot(normalized['USDZAR=X'], label="USD/ZAR (The Rand)", linestyle=':', alpha=0.8)

plt.title("The Triple Threat: Sasol vs. Oil vs. The Rand (Last 6 Months)")
plt.ylabel("Normalized Growth (Start = 100)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# --- 4. THE QUANT GRADUATION MATH ---
matrix = data.corr()
print("\n" + "="*40)
print("--- THE MULTI-FACTOR CORRELATION MATRIX ---")
print(matrix['SOL.JO'].sort_values(ascending=False))
print("="*40)