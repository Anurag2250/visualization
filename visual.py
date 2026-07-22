import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('worldometer_data.csv')

# Standardize column names
df.columns = df.columns.str.lower().str.replace(' ', '_')

# Fill missing values
df['who_region'] = df['who_region'].fillna('Unknown')
df['tests/1m_pop'] = df['tests/1m_pop'].fillna(df['tests/1m_pop'].mean())

# Drop unnecessary columns
df = df.drop(columns=['newcases', 'newrecovered', 'newdeaths', 'activecases'])

# Fill categorical + numerical missing values
df['continent'] = df['continent'].fillna(df['continent'].mode()[0])
df['population'] = df['population'].fillna(df['population'].median())
df['totaldeaths'] = df['totaldeaths'].fillna(df['totaldeaths'].median())
df['totalrecovered'] = df['totalrecovered'].fillna(df['totalrecovered'].median())
df['serious,critical'] = df['serious,critical'].fillna(df['serious,critical'].median())
df['tot_cases/1m_pop'] = df['tot_cases/1m_pop'].fillna(df['tot_cases/1m_pop'].median())
df['deaths/1m_pop'] = df['deaths/1m_pop'].fillna(df['deaths/1m_pop'].median())
df['totaltests'] = df['totaltests'].fillna(df['totaltests'].median())

# Outlier detection
col = ['totalcases', 'totaldeaths', 'totalrecovered',
       'tot_cases/1m_pop', 'deaths/1m_pop']

for i in col:
    q1 = df[i].quantile(0.25)
    q3 = df[i].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[(df[i] < lower) | (df[i] > upper)]
    print(f"{i}: {len(outliers)} outliers")

# Log transformation
skewed_cols = ['totalcases', 'totaldeaths', 'totalrecovered', 'totaltests']

for col in skewed_cols:
    df[f'log_{col}'] = np.log1p(df[col])

# ----------------- VISUALIZATION (DASHBOARD STYLE) -----------------

fig, axes = plt.subplots(3, 2, figsize=(16, 18))
fig.suptitle('COVID-19 World Analysis Dashboard', fontsize=18)

# 1. Distribution
sns.histplot(df['log_totalcases'], bins=30, kde=True, ax=axes[0, 0])
axes[0, 0].set_title('Distribution of Total Cases (Log)')

# 2. Continent
sns.countplot(data=df, y='continent',
              order=df['continent'].value_counts().index,
              ax=axes[0, 1])
axes[0, 1].set_title('Countries by Continent')

# 3. Top 10 countries
top10 = df.nlargest(10, 'totalcases')
sns.barplot(data=top10, y='country/region', x='totalcases', ax=axes[1, 0])
axes[1, 0].set_title('Top 10 Countries by Cases')

# 4. Correlation heatmap
corr_cols = ['totalcases', 'totaldeaths', 'totalrecovered',
             'tot_cases/1m_pop', 'deaths/1m_pop', 'tests/1m_pop']

sns.heatmap(df[corr_cols].corr(),
            annot=True, cmap='coolwarm', fmt='.2f',
            ax=axes[1, 1])
axes[1, 1].set_title('Correlation Matrix')

# 5. Per capita
per_capita = df.nlargest(15, 'tot_cases/1m_pop')
sns.barplot(data=per_capita,
            y='country/region',
            x='tot_cases/1m_pop',
            ax=axes[2, 0])
axes[2, 0].set_title('Cases per 1M Population')

# 6. South Asia
south_asia = ['Nepal', 'India', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Afghanistan']
sa_df = df[df['country/region'].isin(south_asia)]

sns.barplot(data=sa_df,
            x='country/region',
            y='tot_cases/1m_pop',
            ax=axes[2, 1])
axes[2, 1].set_title('South Asia Comparison')
axes[2, 1].tick_params(axis='x', rotation=45)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()