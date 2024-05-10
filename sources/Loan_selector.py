import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import itertools
import sys
sys.path.append('./')
from common import utils
from common.config import loan_params

st.title('Mortgage Re-Payments')
# Input sections for each part of the mortgage
rate_options = st.session_state['base_rates']
discount = st.session_state['discount']
mortgage_parts = [st.session_state['P1'], st.session_state['P2'], st.session_state['P3']]
with st.container():
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        st.subheader(":orange[Part 1]")
        rate_type_1 = st.selectbox("Select Rate Type", list(rate_options.keys()), key='part1_rate_type')
        r1 = rate_options[rate_type_1]
        st.write(f"Interest Rate (%): {r1:.2f}")  
    with col2:
        st.subheader(":orange[Part 2]")
        rate_type_2 = st.selectbox("Select Rate Type", list(rate_options.keys()), key='part2_rate_type')
        r2 = rate_options[rate_type_2]
        st.write(f"Interest Rate (%): {r2:.2f}")
    with col3:
        st.subheader(":orange[Part 3]")
        rate_type_3 = st.selectbox("Select Rate Type", list(rate_options.keys()), key='part3_rate_type')
        r3 = rate_options[rate_type_3]
        st.write(f"Interest Rate (%): {r3:.2f}")
    
    # Define which part gets the discount
    col1, col2 = st.columns(2, gap = 'large')
    with col1:
        discount_part = st.selectbox("Select Part to Apply Discount", ['None', 'Part 1', 'Part 2', 'Part 3'], index=0, key='discount_part')
    with col2:
        amort_rate = st.number_input(f"Amortization rate", value=2, key = 'A1')

    # Apply the discount to the selected part
    if discount_part == 'Part 1':
        r1 -= discount
    elif discount_part == 'Part 2':
        r2 -= discount
    elif discount_part == 'Part 3':
        r3 -= discount

    P1 = st.session_state['P1']
    P2 = st.session_state['P2']
    P3 = st.session_state['P3']

    # Prepare inputs
    inputs = [(P1, r1), (P2, r2), (P3, r3)]

with st.container():
    interests = [utils.compute_interest(P, r) for P, r in inputs]
    interest_monthly = sum([M for M in interests])
    tot_mortgage = P1 + P2 + P3
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
    index = ["interest Part 1", "interest Part 2", "interest Part 3", "Interest", "Amortized", "Total"]
    df = pd.DataFrame(data, index=index)

    df['Monthly'] = df['Monthly'].astype(int)
    df['Yearly'] = df['Yearly'].astype(int)
    #st.write(f"With an amortization of :red[{amort_rate}%]")
    st.dataframe(df.T, use_container_width=True)

#####################################################################################################################
####################################### ALL POSSIBLE COMBINATIONS ###################################################
#####################################################################################################################
st.header('Monthly Calculator - NO ADJUSTMENT CONSIDERED')
with st.expander("Dynamic Combinations"):
    # Define mortgage parts (assumed to be defined globally or fetched similarly)
    selected_rates = st.multiselect("Select which rates to include:", options=list(rate_options.keys()), default=list(rate_options.keys()))

    # Filter `base_rates` to only include the rates that have been selected
    selected_base_rates = {rate: rate_options[rate] for rate in selected_rates}

    # Generate all rate combinations for the selected mortgage parts
    rate_combinations = list(itertools.product(selected_base_rates.items(), repeat=len(mortgage_parts)))

    # Iterate through each combination and apply the discount to one part at a time
    results = []
    labels = []
    for rates in rate_combinations:
        for i in range(len(mortgage_parts)):
            # Apply discount to the ith part
            discounted_rates = [rate - discount if idx == i else rate for idx, (_, rate) in enumerate(rates)]
            scenario = ", ".join(f"Part {idx+1}: {name} @ {rate:.2f}%" for idx, ((name, _), rate) in enumerate(zip(rates, discounted_rates)))
            total_interest = sum(utils.compute_monthly_interest(mortgage, rate) for mortgage, rate in zip(mortgage_parts, discounted_rates))
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

    fig = px.bar(top_scenarios, x='Scenario', y='Monthly Interest (kr)',
                title="Top 10 Scenarios with Lowest Monthly Interest",
                labels={'Scenario': 'Rate Configuration', 'Monthly Interest (kr)': 'Monthly Interest (kr)'})
    st.plotly_chart(fig)

#####################################################################################################################
################################################# Calculate scenarios including rate adjustments#####################
#####################################################################################################################
st.header('Loan Optimizaer - Adjustments Approximated')
with st.expander("Simulate Rate Adjustments - every 3 months"):
    # Define mortgage parts (assumed to be defined globally or fetched similarly)
    selected_rates_adj = st.multiselect("Select which rates to include:", options=list(rate_options.keys()), default=list(rate_options.keys()), key = 'adj')

    # Filter `base_rates` to only include the rates that have been selected
    selected_base_rates_adj = {rate: rate_options[rate] for rate in selected_rates_adj}

    col1, col2, col3= st.columns(3, gap='large')
    with col1:
        monthly_dec = st.number_input("Rate adjustments (every 3 months)", value=0.25)
    with col2:
        final_float_rate = st.number_input("Lowest float rate", value=3.0)
    with col3:
        duration = st.number_input("Simulation in months", value=24)


    # Generate all rate combinations for the selected mortgage parts
    rate_combinations_adj = list(itertools.product(selected_base_rates_adj.items(), repeat=len(mortgage_parts)))

    all_results_adj = []
    detailed_interests_all = []
    for rates in itertools.product(selected_base_rates_adj.items(), repeat=len(mortgage_parts)):
        for i in range(len(mortgage_parts)):
            # Apply discount to the ith part
            discounted_rates_adj = [(name, rate, 1 if idx == i else 0) for idx, (name, rate) in enumerate(rates)]
            #print(discounted_rates_adj)
            total_interest_adj, scenario_adj, final_rates_adj, detailed_interests = utils.compute_total_interest_and_final_rates(mortgage_parts, discounted_rates_adj, discount, monthly_dec, final_float_rate, duration)
            
             # Prepare detailed interests text or structured data
            detailed_interests_text = "; ".join([f"Part {idx+1}: " + ", ".join([f"Rate: {rate:.2f}%, Interest: {interest:.2f}" for rate, interest in part]) for idx, part in enumerate(detailed_interests)])

            detailed_dict = {}
            for idx, part in enumerate(detailed_interests):
                for rate, interest in part:
                    detailed_dict[f'Part {idx+1} Rate (%)'] = rate
                    detailed_dict[f'Part {idx+1} Interest (kr)'] = interest

            all_results_adj.append({
            'Scenario': scenario_adj,
            'Discount on': f"Part {i+1}",
            'Final Rates': final_rates_adj,
            'Total Interest Paid (kr)': total_interest_adj,
            'Detailed Interests': detailed_interests_text
            })

            detailed_interests_all.append({
            **detailed_dict  # Expand the detailed interests directly into the dictionary
        })

    df_details_adj = pd.DataFrame(all_results_adj)
    df_results_adj = df_details_adj.drop(['Detailed Interests'], axis =1)

    
    topN_adj = st.slider("Selct number of top scenarios",min_value = 1, max_value = 20, value=5, key='topN_adj')
    top_scenarios_adj = df_results_adj.sort_values(by='Total Interest Paid (kr)').head(topN_adj)  
    st.header(f"Top {topN_adj} Scenarios with Lowest Total Interest Paid Over {duration} Months")
    st.table(top_scenarios_adj)

    if 'show_df' not in st.session_state:
        st.session_state['show_df'] = False

    if st.button('See detailed adjusted monthly rates'):
        st.session_state['show_df'] = not st.session_state['show_df']

    df_details_interests = pd.DataFrame(detailed_interests_all)  # ensure it is being created correctly

    if st.session_state['show_df']:
        top_scenarios_details = df_details_adj.sort_values(by='Total Interest Paid (kr)').head(topN_adj)
        top_scenarios_details = top_scenarios_details.drop(['Final Rates', 'Total Interest Paid (kr)'], axis = 1)
        st.table(top_scenarios_details)
