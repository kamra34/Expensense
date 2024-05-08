import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import itertools

def calculate_mortgage(P, r, n):
    #n = 50
    r = r / 12 / 100  # Convert APR to a monthly decimal rate
    n = n * 12  # Convert loan term in years to number of monthly payments
    M = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    total_interest = M * n - P
    return M, total_interest

def compute_interest(P, r, n):
    yearly_interest = (P * ((r - n)/100))
    monthly_interest = yearly_interest/12
    return monthly_interest

st.title('Mortgage Calculator')

# Input sections for each part of the mortgage
inputs = []
with st.container():
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        st.header("Part 1")
        P1 = st.number_input(f"Principal", value=3000000, key = 'P1')
        r1 = st.number_input(f"Interest Rate(%)", value=2.49, key = 'r1')
        n1 = st.number_input(f"Discount(%)", value=0.0, key = 'n1')
    with col2:
        st.header("Part 2")
        P2 = st.number_input(f"Principal", value=2692309, key = 'P2')
        r2 = st.number_input(f"Interest Rate(%)", value=4.19, key = 'r2')
        n2 = st.number_input(f"Discount(%)", value=0.0, key = 'n2')
    with col3:
        st.header("Part 3")
        P3 = st.number_input(f"Principal", value=2692309, key = 'P3')
        r3 = st.number_input(f"Interest Rate(%)", value=4.54, key = 'r3')
        n3 = st.number_input(f"Discount(%)", value=0.0, key = 'n3')

    inputs.append((P1, r1, n1))
    inputs.append((P2, r2, n2))
    inputs.append((P3, r3, n3))

with st.container():
    st.header("Mortgage Re-Payments")
    interests = [compute_interest(P, r, n) for P, r, n in inputs]
    interest_monthly = sum([M for M in interests])
    tot_mortgage = P1 + P2 + P3
    amort_rate = st.number_input(f"Amortization rate", value=2, key = 'A1')
    amort_percentage = amort_rate / 100
    amortized_monthly = (tot_mortgage*amort_percentage)/12
    total_monthly = amortized_monthly + interest_monthly
    # Creating the DataFrame
    data = {    
        'Monthly': [
            interests[0],
            interests[1],
            interests[2],
            interest_monthly,
            amortized_monthly,
            total_monthly
        ],
        'Yearly': [
            interests[0]*12,
            interests[1]*12,
            interests[2]*12,
            interest_monthly*12,
            amortized_monthly*12,
            total_monthly*12
        ]
    }
    index = ["interest Part 1", "interest Part 2", "interest Part 3", "Interest", "Amortized", "Total Monthly"]
    df = pd.DataFrame(data, index=index)
    # After creating DataFrame, convert 'amount' column to integers
    df['Monthly'] = df['Monthly'].astype(int)
    df['Yearly'] = df['Yearly'].astype(int)
    #st.write(f"With an amortization of :red[{amort_rate}%]")
    st.dataframe(df.T)

#####################################################################################################################
####################################### ALL POSSIBLE COMBINATIONS ###################################################
#####################################################################################################################
with st.expander("All possible combinations:"):
    st.header("All possible combinations:")
    # Define base rates and mortgage parts
    mortgage_parts = [P1, P2, P3]

    # User inputs for interest rates
    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col1:
        include_float = st.checkbox("Include Float Rate", True)
        float_ir = st.number_input("Float rate (%)", value=4.65, key='fir1')
    with col2:
        include_fixed_1 = st.checkbox("Include Fixed 1 Year", True)
        fixed_1_ir = st.number_input("Fixed 1 year (%)", value=4.54, key='f1y1')
    with col3:
        include_fixed_2 = st.checkbox("Include Fixed 2 Year", True)
        fixed_2_ir = st.number_input("Fixed 2 year (%)", value=4.19, key='f2y1')
    with col4:
        include_fixed_3 = st.checkbox("Include Fixed 3 Year", True)
        fixed_3_ir = st.number_input("Fixed 3 year (%)", value=4.00, key='f3y1')

    discount = st.number_input("Discount (%)", value=2.19, key='D11')

    # Filter selected rate types based on user input
    base_rates = {}
    if include_float:
        base_rates['float'] = float_ir
    if include_fixed_1:
        base_rates['fixed_1_year'] = fixed_1_ir
    if include_fixed_2:
        base_rates['fixed_2_year'] = fixed_2_ir
    if include_fixed_3:
        base_rates['fixed_3_year'] = fixed_3_ir

    # Generate all rate combinations for the selected mortgage parts
    rate_combinations = list(itertools.product(base_rates.items(), repeat=len(mortgage_parts)))

    # Function to calculate the monthly interest
    def compute_monthly_interest(amount, rate):
        return amount * (rate / 100) / 12

    # Iterate through each combination and apply the discount to one part at a time
    results = []
    labels = []
    for rates in rate_combinations:
        for i in range(len(mortgage_parts)):
            # Apply discount to the ith part
            discounted_rates = [rate - discount if idx == i else rate for idx, (_, rate) in enumerate(rates)]
            scenario = ", ".join(f"Part {idx+1}: {name} @ {rate:.2f}%" for idx, ((name, _), rate) in enumerate(zip(rates, discounted_rates)))
            total_interest = sum(compute_monthly_interest(mortgage, rate) for mortgage, rate in zip(mortgage_parts, discounted_rates))
            labels.append(scenario)
            results.append(total_interest)

    # Create a DataFrame for results
    df_results = pd.DataFrame({
        'Scenario Index': list(range(len(results))),
        'Monthly Interest (kr)': results,
        'Scenario': labels
    })

    df_results['Monthly Interest (kr)'] = df_results['Monthly Interest (kr)'].astype(int)

    # Plotting using Plotly
    fig = px.scatter(df_results, x='Scenario Index', y='Monthly Interest (kr)',
                    hover_data=['Scenario'], labels={'Scenario Index': 'Combination Index'})
    fig.update_traces(mode='markers+lines', textposition='top center')
    fig.update_layout(
        title='Total Monthly Interest for Each Configuration',
        xaxis_title='Combination Index',
        yaxis_title='Total Monthly Interest (kr)',
        hovermode='closest'
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Sort by monthly interest and take the top N
    st.header("Top Scenarios with Lowest Monthly Interest")
    topN = st.slider("Selct number of top scenarios",min_value = 1, max_value = 40, value=10, key='topN')
    top_scenarios = df_results.sort_values(by='Monthly Interest (kr)').head(topN)

    # Display the top 10 scenarios
    st.table(top_scenarios)

    # Optional: You can also visualize the top scenarios if desired
    fig = px.bar(top_scenarios, x='Scenario', y='Monthly Interest (kr)',
                title="Top 10 Scenarios with Lowest Monthly Interest",
                labels={'Scenario': 'Rate Configuration', 'Monthly Interest (kr)': 'Monthly Interest (kr)'})
    st.plotly_chart(fig)