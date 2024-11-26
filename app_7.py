# Import required libraries
import pandas as pd
import streamlit as st

# File paths
file_path = 'Raw_eGRID_EF_1.xlsx'  # Update with the correct path if needed
gwp_file_path = 'GWP.xlsx'
scope_1_file_path = 'Scope_1_stationary_fuel.xlsx'

# Load the data
df = pd.read_excel(file_path, engine='openpyxl')
gwp_df = pd.read_excel(gwp_file_path)
scope_1_df = pd.read_excel(scope_1_file_path)

# Conversion factors
conversion_factors_1 = {
    "mtCO2e/kWh": 4.53592e-7,
    "mtCO2e/MWh": 4.53592e-4,
    "kgCO2e/kWh": 4.53592e-4,
    "kgCO2e/MWh": 0.453592
}

conversion_factors_2 = {
    "mtCO2e/therms": 1.0e-4,
    "mtCO2e/mmBTU": 1.0e-3,
    "kgCO2e/therms": 0.1,
    "kgCO2e/mmBTU": 1
}

# Streamlit app
st.title("Emission Factor Tool")
st.title("**Scope 2, Location based**")

# User input: Select eGRID region
acronym_input = st.selectbox("Select an eGRID Subregion Acronym", df['eGRID Subregion Acronym'].unique())

# User input: Select GWP column (SAR, AR5, AR6)
gwp_column = st.selectbox("Select GWP Column (AR5, AR4, SAR)", ['AR5', 'AR4',  'SAR'])

# User input: Select EF Category (Total Output Emission Factors or Non-Baseload Emission Factors)
ef_category = st.selectbox("Select EF Category", ["Total Output Emission Factors", "Non-Baseload Emission Factors"])

# User input: Select output units (mtCO2e/kWh, kgCO2e/kWh, kgCO2e/MWh)
output_unit = st.selectbox("Select Output Unit", ["mtCO2e/kWh", "mtCO2e/MWh", "kgCO2e/kWh", "kgCO2e/MWh"])

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
    conversion_factor = conversion_factors_1[unit]
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

# Scope 1 Section - Stationary Combustion
st.title("**Scope 1, Stationary Combustion**")

# User input: Select fuel type
fuel_type = st.selectbox("Select Fuel Type", scope_1_df['Unnamed: 1'][2:].unique())

# User input: Select output units (kgCO2, mtCO2)
scope_1_output_unit = st.selectbox("Select Output Unit", ["mtCO2e/therms", "mtCO2e/mmBTU","kgCO2e/therms","kgCO2e/mmBTU"])

# Function to get emission factors for selected fuel type
def get_scope_1_emission_factors(fuel):
    result = scope_1_df[scope_1_df['Unnamed: 1'] == fuel].iloc[0]
    co2_factor = float(result['Unnamed: 2'])  # CO2 Factor (kg/mmBtu)
    ch4_factor = float(result['Unnamed: 3'])  # CH4 Factor (kg/mmBtu)
    n2o_factor = float(result['Unnamed: 4'])  # N2O Factor (kg/mmBtu)
    ef_country = result['Unnamed: 5']  # EF Country
    ef_authority = result['Unnamed: 6']  # EF Authority
    ef_data_year = result['Unnamed: 7']  # EF Data Year
    ef_release_year = result['Unnamed: 8']  # EF Release Year
    return co2_factor, ch4_factor, n2o_factor, ef_country, ef_authority, ef_data_year, ef_release_year

# Function to convert raw factors to chosen unit
def convert_scope_1_units(co2, ch4, n2o, gwp_values, unit):
    conversion_factor = conversion_factors_2[unit]
    co2_converted = co2 * conversion_factor * gwp_values['CO2']
    ch4_converted = ch4 * conversion_factor * gwp_values['CH4']
    n2o_converted = n2o * conversion_factor * gwp_values['N2O']
    total_converted = co2_converted + ch4_converted + n2o_converted
    return co2_converted, ch4_converted, n2o_converted, total_converted

# When the user clicks the button, calculate Scope 1 emissions
if st.button("Calculate Scope 1 Emission Factors"):
    co2, ch4, n2o, ef_country, ef_authority, ef_data_year, ef_release_year = get_scope_1_emission_factors(fuel_type)
    gwp_values = get_gwp_values(gwp_column)
    co2_converted, ch4_converted, n2o_converted, total_converted = convert_scope_1_units(co2, ch4, n2o, gwp_values, scope_1_output_unit)
    
    # Display raw emission factors
    st.write("### Raw Emission Factors (kg/mmBtu):")
    
    raw_data_scope_1 = {
        'Fuel Type': [fuel_type],
        'Raw CO2 (kg/mmBtu)': [f"{co2:.4f}"],
        'Raw CH4 (kg/mmBtu)': [f"{ch4:.4f}"],
        'Raw N2O (kg/mmBtu)': [f"{n2o:.4f}"],
        'EF Country': [ef_country],
        'EF Authority': [ef_authority],
        'EF Data Year': [ef_data_year],
        'EF Release Year': [ef_release_year]
    }
    
    df_raw_scope_1 = pd.DataFrame(raw_data_scope_1)
    st.table(df_raw_scope_1)
    
    # Display converted emission factors
    st.write("### Converted Emission Factors ({})".format(scope_1_output_unit))
    
    scope_1_data = {
        'Fuel Type': [fuel_type],
        'CO2 ({})'.format(scope_1_output_unit): [f"{co2_converted:.4f}"],
        'CH4 ({})'.format(scope_1_output_unit): [f"{ch4_converted:.6f}"],
        'N2O ({})'.format(scope_1_output_unit): [f"{n2o_converted:.6f}"],
        'Total CO2e ({})'.format(scope_1_output_unit): [f"{total_converted:.6f}"]
    }
    
    df_scope_1 = pd.DataFrame(scope_1_data)
    st.table(df_scope_1)
