# Import required libraries
import pandas as pd
import streamlit as st

# File paths
file_path = 'Raw_eGRID_EF_1.xlsx'  # Update with the correct path if needed
gwp_file_path = 'GWP.xlsx'

# Load the data
df = pd.read_excel(file_path, engine='openpyxl')
gwp_df = pd.read_excel(gwp_file_path)

# Conversion factors
conversion_factors = {
    "mtCO2e/kWh": 4.53592e-7,
    "mtCO2e/MWh": 4.53592e-4,
    #"mtCO2e/lbs":,
    "kgCO2e/kWh": 4.53592e-4,
    "kgCO2e/MWh": 0.453592
    #"kgCO2e/lbs": 
}

# Streamlit app
st.title("Emission Factor Tool")
st.title("**Location based**")

# User input: Select eGRID region
acronym_input = st.selectbox("Select an eGRID Subregion Acronym", df['eGRID Subregion Acronym'].unique())

# User input: Select GWP column (SAR, AR5, AR6)
gwp_column = st.selectbox("Select GWP Column (SAR, AR5, AR6)", ['SAR', 'AR4', 'AR5'])

# User input: Select EF Category (Total Output Emission Factors or Non-Baseload Emission Factors)
ef_category = st.selectbox("Select EF Category", ["Total Output Emission Factors", "Non-Baseload Emission Factors"])

# User input: Select output units (mtCO2e/kWh, kgCO2e/kWh, kgCO2e/MWh)
output_unit = st.selectbox("Select Output Unit", ["mtCO2e/kWh","mtCO2e/MWh","mtCO2e/lbs","kgCO2e/kWh","kgCO2e/MWh","kgCO2e/lbs"])

# Function to get emission factors based on eGRID Acronym input and EF Category
def get_emission_factors(acronym, category):
    result = df[(df['eGRID Subregion Acronym'].str.upper() == acronym.upper()) & 
                (df['EF Category'] == category)]
    if not result.empty:
        return result[['CO2 Factor (lb / MWh)', 'CH4 Factor (lb / MWh)', 'N2O Factor (lb / MWh)', 
                       'EF Country', 'EF Authority', 'EF Data Year', 'EF Release Year']]
    else:
        return None

# Function to extract relevant GWP values based on the selected column
def get_gwp_values(column):
    gwp_values = {
        'CO2': gwp_df[gwp_df['Global Warming Potential'] == 'CO2'][column].values[0],
        'CH4': gwp_df[gwp_df['Global Warming Potential'] == 'CH4'][column].values[0],
        'N2O': gwp_df[gwp_df['Global Warming Potential'] == 'N2O'][column].values[0]
    }
    return gwp_values

# Function to convert raw factors to chosen unit
def convert_to_unit(co2, ch4, n2o, gwp_values, unit):
    conversion_factor = conversion_factors[unit]
    co2_converted = co2 * conversion_factor * gwp_values['CO2']
    ch4_converted = ch4 * conversion_factor * gwp_values['CH4']
    n2o_converted = n2o * conversion_factor * gwp_values['N2O']
    total_converted = co2_converted + ch4_converted + n2o_converted
    return co2_converted, ch4_converted, n2o_converted, total_converted

# Function to get emission factors, convert them, and display GWP values
def get_emission_factors_and_convert(acronym, gwp_column, category, unit):
    result = get_emission_factors(acronym, category)
    if result is not None:
        co2 = result['CO2 Factor (lb / MWh)'].values[0]
        ch4 = result['CH4 Factor (lb / MWh)'].values[0]
        n2o = result['N2O Factor (lb / MWh)'].values[0]
        
        # Get GWP values for the selected column
        gwp_values = get_gwp_values(gwp_column)
        
        # Convert the emission factors to the selected unit
        co2_converted, ch4_converted, n2o_converted, total_converted = convert_to_unit(co2, ch4, n2o, gwp_values, unit)
        
        return {
            'Raw CO2 (lb/MWh)': co2,
            'Raw CH4 (lb/MWh)': ch4,
            'Raw N2O (lb/MWh)': n2o,
            'EF Country': result['EF Country'].values[0],
            'EF Authority': result['EF Authority'].values[0],
            'EF Data Year': result['EF Data Year'].values[0],
            'EF Release Year': result['EF Release Year'],
            'CO2 ({})'.format(unit): co2_converted,
            'CH4 ({})'.format(unit): ch4_converted,
            'N2O ({})'.format(unit): n2o_converted,
            'Total CO2e ({})'.format(unit): total_converted
        }
    else:
        return "Acronym not found!"

# When the user clicks the button, run the calculation and display results
if st.button("Calculate Emission Factors"):
    factors_converted = get_emission_factors_and_convert(acronym_input, gwp_column, ef_category, output_unit)
    
    if isinstance(factors_converted, dict):
        st.write("### Raw Emission Factors (lb/MWh):")
        
        # Create a DataFrame to display raw factors and additional information
        raw_data = {
            'Emission Source': ['Electricity'],
            'eGRID': [acronym_input],
            'Raw CO2 (lb/MWh)': [f"{factors_converted['Raw CO2 (lb/MWh)']:.4f}"],
            'Raw CH4 (lb/MWh)': [f"{factors_converted['Raw CH4 (lb/MWh)']:.4f}"],
            'Raw N2O (lb/MWh)': [f"{factors_converted['Raw N2O (lb/MWh)']:.4f}"],
            'EF Country': [factors_converted['EF Country']],
            'EF Authority': [factors_converted['EF Authority']],
            'EF Data Year': [factors_converted['EF Data Year']],
            'EF Release Year': [factors_converted['EF Release Year']]
        }
        
        df_raw = pd.DataFrame(raw_data)
        
        # Display the raw factors table using st.table
        st.table(df_raw)
        
        st.write("### Converted Emission Factors ({})".format(output_unit))
        
        # Create a DataFrame to display the converted factors
        converted_data = {
            'Emission Source': ['Electricity'],
            'eGRID': [acronym_input],
            'CO2 ({})'.format(output_unit): [f"{factors_converted['CO2 ({})'.format(output_unit)]:.10f}"],
            'CH4 ({})'.format(output_unit): [f"{factors_converted['CH4 ({})'.format(output_unit)]:.10f}"],
            'N2O ({})'.format(output_unit): [f"{factors_converted['N2O ({})'.format(output_unit)]:.10f}"],
            'Total CO2e ({})'.format(output_unit): [f"{factors_converted['Total CO2e ({})'.format(output_unit)]:.10f}"]
        }
        
        df_converted = pd.DataFrame(converted_data)
        
        # Display the converted factors table using st.table
        st.table(df_converted)
        
    else:
        st.write(factors_converted)