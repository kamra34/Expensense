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

def compute_final_rate(rate_type, initial_rate, duration, final_float_rate, monthly_dec):
    """Determine the final rate after the duration, accounting for decrements."""
    if rate_type.startswith("fixed"):
        # Calculate when the fixed rate term ends and floating kicks in
        months_remaining = max(0, duration - (int(rate_type.split('_')[1]) * 12))
    else:
        months_remaining = duration

    current_rate = initial_rate
    for _ in range(0, months_remaining, 3):
        if current_rate > final_float_rate:
            current_rate = max(final_float_rate, current_rate - monthly_dec)
    return current_rate

def compute_total_interest_and_final_rates(mortgage_parts, rates, discount, monthly_dec, final_float_rate, duration):
    total_interest = 0
    final_rates = []

    for amount, (rate_type, rate) in zip(mortgage_parts, rates):
        if rate_type.startswith("float"):
            final_rate = compute_final_rate(rate_type, rate, duration, final_float_rate, monthly_dec)
            total_interest += calculate_interest_payment(amount, final_rate, duration)
        else:
            fixed_duration = int(rate_type.split('_')[1]) * 12
            total_interest += calculate_interest_payment(amount, rate, fixed_duration)
            final_rate = compute_final_rate("float", rate, duration, final_float_rate, monthly_dec)
            total_interest += calculate_interest_payment(amount, final_rate, duration - fixed_duration)
        
        final_rates.append(f"{final_rate:.2f}%")

    scenario_description = ", ".join(f"Part {idx+1}: {name} @ {rate:.2f}%" for idx, (name, rate) in enumerate(rates))
    final_rates_description = ", ".join(final_rates)
    return total_interest, scenario_description, final_rates_description