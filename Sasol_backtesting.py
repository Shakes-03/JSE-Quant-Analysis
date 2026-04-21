import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np

def get_quant_data(tickers, period="6mo"):
    """Downloads and cleans market data."""
    df = yf.download(tickers, period=period)['Close']
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def calculate_metrics(df):
    """Computes daily returns and volatility."""
    returns = df.pct_change().dropna()
    volatility = returns.std() * np.sqrt(252) # Annualized Vol
    return returns, volatility

# --- Execution ---
prices = get_quant_data(["SOL.JO", "BZ=F"])
rets, vol = calculate_metrics(prices)

print(f"Annualized Volatility:\n{vol}")

import numpy as np

def generate_signals(df, window=20):
    """
    Calculates the Z-Score of the spread between Sasol and Oil.
    Returns a DataFrame with signals: 1 (Buy), -1 (Sell), 0 (Hold).
    """
    # 1. Calculate the Spread (Normalized Sasol - Normalized Oil)
    # We use normalized prices so the units (ZAR vs $) don't clash
    norm_df = (df / df.iloc[0]) * 100
    spread = norm_df['SOL.JO'] - norm_df['BZ=F']
    
    # 2. Calculate Rolling Statistics
    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()
    
    # 3. Calculate Z-Score
    z_score = (spread - rolling_mean) / rolling_std
    
    # 4. Generate Trading Signals
    # Buy Sasol if it's 2 std devs BELOW oil (Z < -2)
    # Sell Sasol if it's 2 std devs ABOVE oil (Z > 2)
    signals = pd.Series(0, index=df.index)
    signals[z_score < -2] = 1   # Buy Signal
    signals[z_score > 2] = -1   # Sell Signal
    
    return z_score, signals

# --- Execution ---
z, trades = generate_signals(prices)

plt.figure(figsize=(10, 4))
plt.plot(z, label='Z-Score of Spread', color='purple')
plt.axhline(2, color='red', linestyle='--')   # Sell Threshold
plt.axhline(-2, color='green', linestyle='--') # Buy Threshold
plt.title("Mean Reversion Signal (Z-Score)")
plt.show()

def backtest_strategy(prices, signals):
    """
    Simulates trading Sasol based on the generated signals.
    """
    # 1. Calculate Daily Returns of Sasol
    sasol_returns = prices['SOL.JO'].pct_change()
    
    # 2. Shift signals by 1 day 
    # (Because if you get a signal today, you trade at tomorrow's open)
    positions = signals.shift(1).fillna(0)
    
    # 3. Calculate Strategy Returns
    strategy_returns = positions * sasol_returns
    
    # 4. Calculate Cumulative Performance
    cumulative_returns = (1 + strategy_returns).cumprod()
    
    return cumulative_returns

# --- Execution ---
performance = backtest_strategy(prices, trades)

plt.figure(figsize=(10, 5))
plt.plot(performance, label='Strategy Performance', color='blue', linewidth=2)
plt.axhline(1, color='black', linestyle=':') # Break-even line
plt.title("Backtest Result: Mean Reversion on Sasol")
plt.ylabel("Growth of R1")
plt.legend()
plt.show()

# Final Performance Metric
total_return = (performance.iloc[-1] - 1) * 100
print(f"Total Strategy Return: {total_return:.2f}%")

import numpy as np

def monte_carlo_simulation(start_price, days, mu, sigma, n_sims=1000):
    """
    Simulates n_sims future price paths using Geometric Brownian Motion.
    """
    # mu is mean daily return, sigma is daily volatility
    # Generate random daily returns using a normal distribution
    dt = 1 # 1 day
    stoch_vol = np.random.normal(0, 1, (days, n_sims))
    
    # GBM Formula: Price_t = Price_{t-1} * exp((mu - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z)
    drift = (mu - 0.5 * sigma**2) * dt
    returns = np.exp(drift + sigma * np.sqrt(dt) * stoch_vol)
    
    # Calculate price paths
    price_paths = np.zeros((days, n_sims))
    price_paths[0] = start_price
    for t in range(1, days):
        price_paths[t] = price_paths[t-1] * returns[t]
        
    return price_paths

# --- Execution ---
last_price = prices['SOL.JO'].iloc[-1]
# Use your earlier calculated mean and daily volatility
daily_mu = rets['SOL.JO'].mean()
daily_sigma = rets['SOL.JO'].std()

sims = monte_carlo_simulation(last_price, 30, daily_mu, daily_sigma)

# Visualization
plt.figure(figsize=(10, 6))
plt.plot(sims, color='grey', alpha=0.1) # The 'Spaghetti'
plt.plot(sims.mean(axis=1), color='red', linewidth=3, label='Mean Path')
plt.title(f"Sasol: 1,000 Simulated Futures (30 Days)")
plt.ylabel("Price (ZAR)")
plt.show()