# Import required libraries 
import pandas as pd
import streamlit as st

# File path
market_file_path = 'EEI_clean.csv'

# Load the data
df_market = pd.read_csv(market_file_path)

# Clean the column names to avoid issues
df_market.columns = df_market.columns.str.strip().str.lower()

# Rename columns to more usable names
df_market.columns = [
    'company_name', 'state', 'data_year', 'utility_specific_residual_mix_emission_rate',
    'utility_avg_emission_rate', 'protocol', 'emissions_certified', 'emission_totals_intensity'
]

# Streamlit app
st.title("Emission Factor Tool")
st.title("**Scope 2, Market based**")

# User input: Select State
state_input = st.selectbox("Select a State", df_market['state'].unique())

# Filter data based on State to show all utility providers in that state
filtered_state_data = df_market[df_market['state'] == state_input]

# User input: Select Company Name
company_name_input = st.selectbox("Select a Company Name", filtered_state_data['company_name'].unique())

# Filter data based on selected company
filtered_company_data = filtered_state_data[filtered_state_data['company_name'] == company_name_input]

# User input: Select Data Year
data_year_input = st.selectbox("Select a Data Year", filtered_company_data['data_year'].unique())

# Filter data based on selected Data Year
final_filtered_data = filtered_company_data[filtered_company_data['data_year'] == data_year_input]

# Extract Utility Average Emission Rate and other relevant information
if not final_filtered_data.empty:
    utility_avg_emission_rate = final_filtered_data['utility_avg_emission_rate'].values[0]
    protocol = final_filtered_data['protocol'].values[0]
    emissions_certified = final_filtered_data['emissions_certified'].values[0]
else:
    st.error("No data available for the selected criteria.")

# User input: Select output units (mtCO2e/kWh, kgCO2e/kWh, kgCO2e/MWh)
output_unit = st.selectbox("Select Output Unit", ["mtCO2e/kWh", "mtCO2e/MWh", "kgCO2e/kWh", "kgCO2e/MWh"])

# Conversion factors
conversion_factors_1 = {
    "mtCO2e/kWh": 4.53592e-7,
    "mtCO2e/MWh": 4.53592e-4,
    "kgCO2e/kWh": 4.53592e-4,
    "kgCO2e/MWh": 0.453592
}

# Function to convert emission rate to chosen unit
def convert_emission_rate(emission_rate, unit):
    conversion_factor = conversion_factors_1[unit]
    converted_emission_rate = emission_rate * conversion_factor
    return converted_emission_rate

# When the user clicks the button, run the calculation and display results
if st.button("Calculate Emission Factors"):
    converted_emission_rate = convert_emission_rate(utility_avg_emission_rate, output_unit)
    
    # Display input data
    st.write("### Input Data:")
    input_data = {
        'Company Name': [company_name_input],
        'State': [state_input],
        'Data Year': [data_year_input],
        'Utility Average Emission Rate (lbs CO2/MWh)': [utility_avg_emission_rate],
        'Protocol': [protocol],
        'Emissions Certified': [emissions_certified]
    }
    df_input = pd.DataFrame(input_data)
    st.table(df_input)
    
    # Display converted emission factors
    st.write("### Converted Emission Factors ({})".format(output_unit))
    converted_data = {
        'Emission Source': ['Electricity'],
        'eGRID': [company_name_input],
        'CO2 ({})'.format(output_unit): [f"{converted_emission_rate:.10f}"],
        'CH4 ({})'.format(output_unit): ["0.0000000000"],  # Placeholder values as no CH4 data provided
        'N2O ({})'.format(output_unit): ["0.0000000000"],  # Placeholder values as no N2O data provided
        'Total CO2e ({})'.format(output_unit): [f"{converted_emission_rate:.10f}"]
    }
    df_converted = pd.DataFrame(converted_data)
    st.table(df_converted)
