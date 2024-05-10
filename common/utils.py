import streamlit as st
########################################################################################
###############################        PART 1           ################################
########################################################################################
def compute_interest(P, r):
    yearly_interest = (P * (r/100))
    monthly_interest = yearly_interest/12
    return monthly_interest


########################################################################################
###############################        PART 2           ################################
########################################################################################
# Function to calculate the monthly interest
def compute_monthly_interest(amount, rate):
    return amount * (rate / 100) / 12


########################################################################################
###############################        PART 3           ################################
########################################################################################
def calculate_interest_payment(amount, rate, months):
        """Calculate the interest payment over a given number of months."""
        return amount * (rate / 100) / 12 * months

def compute_final_rate(rate_type, initial_rate, is_discounted, duration, final_float_rate, monthly_dec, discount=0):
    """Adjust the rate for the duration considering decrements and discounts."""
    current_rate = initial_rate - (discount if is_discounted else 0)
    if rate_type.startswith("float"):
        for _ in range(0, duration, 3):
            # If discounted, allow current_rate to go below final_float_rate but not below 0
            if is_discounted:
                current_rate = max(0, current_rate - monthly_dec)  # Never allow negative rates
            else:
                # If not discounted, enforce the final_float_rate as the floor
                if current_rate > final_float_rate:
                    current_rate = max(final_float_rate, current_rate - monthly_dec)
                else:
                    # Ensure the rate does not fall below the final float rate if not discounted
                    current_rate = max(final_float_rate, current_rate)
    return current_rate
    
def compute_rates_over_time(rate_type, initial_rate, duration, final_float_rate, monthly_dec):
    """Generate a list of rates after each decrement for the duration."""
    rates_over_time = []
    #current_rate = initial_rate - (discount if is_discounted else 0)
    current_rate = initial_rate
    if rate_type.startswith("float"):
        for month in range(0, duration, 3):
            if current_rate > final_float_rate:
                current_rate = max(current_rate- monthly_dec, final_float_rate)
            rates_over_time.append(current_rate)
    else:
        # Fixed rate scenario: Apply the same rate for the duration
        rates_over_time = [current_rate] * (duration // 3)
    return rates_over_time



def compute_total_interest_and_final_rates(mortgage_parts, rates, discount_index, monthly_dec, final_float_rate, duration):
    total_interest = 0
    minimum_discounted_rate = 0.05
    final_rates = []
    detailed_interests = []
    discount = st.session_state['discount']

    for idx, (amount, (rate_type, rate, is_discounted)) in enumerate(zip(mortgage_parts, rates)):
        rates_over_time = compute_rates_over_time(rate_type, rate, duration, final_float_rate, monthly_dec)

        monthly_interests = []
        if rate_type.startswith("float"):
            for monthly_rate in rates_over_time:
                if is_discounted:
                    monthly_rate = monthly_rate - discount
                    monthly_rate = max(minimum_discounted_rate, monthly_rate)
                interest = calculate_interest_payment(amount, monthly_rate, 3)
                total_interest += interest
                monthly_interests.append((monthly_rate, interest))
            final_rates.append(f"{monthly_rate:.2f}%")  # Store the final rate after all decrements
        else:
            fixed_duration = int(rate_type.split('_')[1]) * 12
            if is_discounted:
                current_rate = rate - discount
                current_rate = max(minimum_discounted_rate, current_rate)
            else:
                current_rate = rate
            interest = calculate_interest_payment(amount, current_rate, fixed_duration)
            total_interest += interest
            monthly_interests.append((current_rate, interest))
            # Handle the float rate for the remainder if the fixed period ends before the total duration
            if duration > fixed_duration:  # Transition to float
                initial_float_rate = st.session_state['base_rates']['float']
                current_float_rate = compute_rates_over_time("float", initial_float_rate, fixed_duration, final_float_rate, monthly_dec)[-1]
                post_fixed_rates = compute_rates_over_time("float", current_float_rate, duration - fixed_duration, final_float_rate, monthly_dec)

                for monthly_rate in post_fixed_rates:
                    if is_discounted:
                        monthly_rate = monthly_rate - discount
                        monthly_rate = max(minimum_discounted_rate, monthly_rate)
                    interest = calculate_interest_payment(amount, monthly_rate, 3)
                    total_interest += interest
                    monthly_interests.append((monthly_rate, interest))
                final_rates.append(f"{monthly_rate:.2f}%")
            else:
                final_rates.append(f"{rate:.2f}%")

        detailed_interests.append(monthly_interests)

    scenario_description = ", ".join(f"Part {idx+1}: {name} @ {rate:.2f}%" for idx, (name, rate, _) in enumerate(rates))
    final_rates_description = ", ".join(final_rates)
    return total_interest, scenario_description, final_rates_description, detailed_interests