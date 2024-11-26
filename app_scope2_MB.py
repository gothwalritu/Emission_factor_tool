# Import required libraries 
import pandas as pd
import streamlit as st

# File path
market_file_path = 'EEI_UtilityCO2EmissionsDatabase June 2023_copy.xlsx'

# Load the data
df_market = pd.read_excel(market_file_path, engine='openpyxl')

# Conversion factors
conversion_factors_1 = {
    "mtCO2e/kWh": 4.53592e-7,
    "mtCO2e/MWh": 4.53592e-4,
    "kgCO2e/kWh": 4.53592e-4,
    "kgCO2e/MWh": 0.453592
}

# Streamlit app
st.title("Emission Factor Tool")
st.title("**Scope 2, Market based**")

# User input: Select State
state_input = st.selectbox("Select a State", df_market['State'].unique())

# User input: Select Data Year
data_year_input = st.selectbox("Select a Data Year", df_market[df_market['State'] == state_input]['Data Year'].unique())

# Filter data based on State and Data Year
filtered_data = df_market[(df_market['State'] == state_input) & (df_market['Data Year'] == data_year_input)]

# User input: Select Company Name
company_name_input = st.selectbox("Select a Company Name", filtered_data['Company Name'].unique())

# Get Utility Average Emission Rate for the selected company
utility_avg_emission_rate = filtered_data[filtered_data['Company Name'] == company_name_input]['Utility Average Emissions Rate (lbs CO2/MWh)'].values[0]

# User input: Select output units (mtCO2e/kWh, kgCO2e/kWh, kgCO2e/MWh)
output_unit = st.selectbox("Select Output Unit", ["mtCO2e/kWh", "mtCO2e/MWh", "kgCO2e/kWh", "kgCO2e/MWh"])

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
        'Protocol': filtered_data[filtered_data['Company Name'] == company_name_input]['Protocol'].values
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
