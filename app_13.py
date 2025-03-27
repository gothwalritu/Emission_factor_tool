
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
    "mtCO2e/kWh": 4.5359237e-7,
    "mtCO2e/MWh": 4.5359237e-4,
    "kgCO2e/kWh": 4.5359237e-4,
    "kgCO2e/MWh": 0.45359237
}

conversion_factors_2 = {
    "mtCO2e/therms": 1.0e-4,
    "mtCO2e/mmBTU": 1.0e-3,
    "kgCO2e/therms": 0.1,
    "kgCO2e/mmBTU": 1
}

# Streamlit app
st.title("Emission Factor Tool")



# User input: Select GWP column (SAR, AR5, AR6)
st.markdown(
    'Select GWP Column (AR6, AR5, AR4, SAR) <span title="Global Warming Potential (GWP) measures the relative impact of greenhouse gases compared to CO2.">ℹ️</span>',
    unsafe_allow_html=True
)
gwp_column = st.selectbox("", ['AR6','AR5', 'AR4', 'SAR'])



# Scope 1 Section - Stationary Combustion
st.title("**Scope 1, Stationary Combustion**")

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

# User input: Select fuel type
fuel_type = st.selectbox("Select Fuel Type", scope_1_df['Unnamed: 1'][2:].unique())

# User input: Select output units (kgCO2, mtCO2)
scope_1_output_unit = st.selectbox("Select Output Unit for scope 1", ["mtCO2e/therms", "mtCO2e/mmBTU","kgCO2e/therms","kgCO2e/mmBTU"])

# Function to get emission factors for selected fuel type
def get_scope_1_emission_factors(fuel):
    result = scope_1_df[scope_1_df['Unnamed: 1'] == fuel].iloc[0]
    co2_factor = float(result['Unnamed: 2'])  # CO2 Factor (kg/mmBtu)
    ch4_factor = float(result['Unnamed: 3'])  # CH4 Factor (g/mmBtu)
    n2o_factor = float(result['Unnamed: 4'])  # N2O Factor (g/mmBtu)
    ef_country = result['Unnamed: 5']  # EF Country
    ef_authority = result['Unnamed: 6']  # EF Authority
    ef_data_year = result['Unnamed: 7']  # EF Data Year
    ef_release_year = result['Unnamed: 8']  # EF Release Year
    ef_combustion_type = result['Unnamed: 9'] # EF Combustion type
    return co2_factor, ch4_factor, n2o_factor, ef_country, ef_authority, ef_data_year, ef_release_year, ef_combustion_type

# Function to convert raw factors to chosen unit
def convert_scope_1_units(co2, ch4, n2o, gwp_values, unit):
    conversion_factor = conversion_factors_2[unit]
    co2_converted = co2 * conversion_factor * gwp_values['CO2']
    ch4_converted = ch4 * conversion_factor * gwp_values['CH4']*0.001
    n2o_converted = n2o * conversion_factor * gwp_values['N2O']*0.001
    total_converted = co2_converted + ch4_converted + n2o_converted
    return co2_converted, ch4_converted, n2o_converted, total_converted

# When the user clicks the button, calculate Scope 1 emissions
if st.button("Calculate Scope 1 Emission Factors"):
    co2, ch4, n2o, ef_country, ef_authority, ef_data_year, ef_release_year, ef_combustion_type = get_scope_1_emission_factors(fuel_type)
    gwp_values = get_gwp_values(gwp_column)
    co2_converted, ch4_converted, n2o_converted, total_converted = convert_scope_1_units(co2, ch4, n2o, gwp_values, scope_1_output_unit)
    
    # Display raw emission factors
    st.write("### Raw Emission Factors (kg/mmBtu):")
    
    raw_data_scope_1 = {
        'Fuel Type': [fuel_type],
        'Raw CO2 (kg/mmBtu)': [f"{co2:.2f}"],
        'Raw CH4 (g/mmBtu)': [f"{ch4:.2f}"],
        'Raw N2O (g/mmBtu)': [f"{n2o:.2f}"],
        'EF Country': [ef_country],
        'EF Authority': [ef_authority],
        'EF Data Year': [ef_data_year],
        'EF Release Year': [ef_release_year],
        'Combustion Type': [ef_combustion_type]
    }
    
    df_raw_scope_1 = pd.DataFrame(raw_data_scope_1)
    st.table(df_raw_scope_1)
    
    # Display converted emission factors
    st.write("### Converted Emission Factors ({})".format(scope_1_output_unit))
    
    scope_1_data = {
        'Fuel Type': [fuel_type],
        'CO2 ({})'.format(scope_1_output_unit): [f"{co2_converted:.7f}"],
        'CH4 ({})'.format(scope_1_output_unit): [f"{ch4_converted:.7f}"],
        'N2O ({})'.format(scope_1_output_unit): [f"{n2o_converted:.7f}"],
        'Total CO2e ({})'.format(scope_1_output_unit): [f"{total_converted:.7f}"]
    }
    
    df_scope_1 = pd.DataFrame(scope_1_data)
    st.table(df_scope_1)



##---------------------------------------------------------------------------------------------------------------------

st.title("**Scope 2, Location based**")

#st.markdown(
    #'## Scope 2, Location based <span title="It represents the average greenhouse gas (GHG) emissions intensity from the consumption of purchased electricity, steam, heating, and cooling.">ℹ️</span>',
    #unsafe_allow_html=True
#)


# User input: Select eGRID region
st.markdown(
    'Select an eGRID Subregion Acronym '
    '<a href="https://www.epa.gov/egrid/power-profiler#/" target="_blank" title="Learn more about eGRID Subregions on EPA\'s Power Profiler website.">ℹ️</a>',
    unsafe_allow_html=True
)
acronym_input = st.selectbox("", df['eGRID Subregion Acronym'].unique())




# User input: Select EF Category (Total Output Emission Factors or Non-Baseload Emission Factors)
ef_category = st.selectbox("Select EF Category", ["Total Output Emission Factors", "Non-Baseload Emission Factors"])

# User input: Select output units (mtCO2e/kWh, kgCO2e/kWh, kgCO2e/MWh)
output_unit = st.selectbox("Select Output Unit for LB Scope 2", ["mtCO2e/kWh", "mtCO2e/MWh", "kgCO2e/kWh", "kgCO2e/MWh"])



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
            'CO2 ({})'.format(output_unit): [f"{factors_converted['CO2 ({})'.format(output_unit)]:.9f}"],
            'CH4 ({})'.format(output_unit): [f"{factors_converted['CH4 ({})'.format(output_unit)]:.9f}"],
            'N2O ({})'.format(output_unit): [f"{factors_converted['N2O ({})'.format(output_unit)]:.9f}"],
            'Total CO2e ({})'.format(output_unit): [f"{factors_converted['Total CO2e ({})'.format(output_unit)]:.9f}"]
        }
        
        df_converted = pd.DataFrame(converted_data)
        
        # Display the converted factors table using st.table
        st.table(df_converted)
        
    else:
        st.write(factors_converted)

#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Scope-2 Market Based

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

# Convert 'data_year' column to integer format (remove decimals)
df_market['data_year'] = pd.to_numeric(df_market['data_year'], errors='coerce').fillna(0).astype(int)

# Convert 'state' column to string and sort alphabetically, removing "nan"
df_market['state'] = df_market['state'].astype(str)
sorted_states = sorted(df_market['state'].dropna().unique())
sorted_states = [state for state in sorted_states if state.lower() != 'nan']

# Streamlit app title with smaller ℹ️ info icon
st.markdown("""
    <h1>Scope 2, Market Based 
        <span title="1. Utility Average Emissions Rate is defined as the average amount of carbon dioxide (CO₂) emissions associated with the electricity delivered to customers.<br>2. EEI Utility Emission Factors (EFs) are provided for CO2 only; use LB CH4 and N2O factors to calculate CO2e for their emissions calculations." style="font-size: 0.4em;">ℹ️</span>
    </h1>
""", unsafe_allow_html=True)


# User input: Select State (sorted alphabetically)
state_input = st.selectbox("Select a State", sorted_states)

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

    # Handle null or blank values
    if pd.isna(utility_avg_emission_rate) or utility_avg_emission_rate == "":
        utility_avg_emission_rate = "no value"
else:
    st.error("No data available for the selected criteria.")

# User input: Select output units (mtCO2e/kWh, kgCO2e/kWh, kgCO2e/MWh)
output_unit = st.selectbox("Select Output Unit for MB Scope 2", ["mtCO2e/kWh", "mtCO2e/MWh", "kgCO2e/kWh", "kgCO2e/MWh"])

# Conversion factors
conversion_factors_1 = {
    "mtCO2e/kWh": 4.53592e-7,
    "mtCO2e/MWh": 4.53592e-4,
    "kgCO2e/kWh": 4.53592e-4,
    "kgCO2e/MWh": 0.453592
}

# Function to convert emission rate to chosen unit
def convert_emission_rate(emission_rate, unit):
    if emission_rate == "no value":
        return "no value"
    conversion_factor = conversion_factors_1[unit]
    converted_emission_rate = float(emission_rate) * conversion_factor
    return f"{converted_emission_rate:.10f}"

# When the user clicks the button, run the calculation and display results
if st.button("Calculate Emission Factors Scope 2"):
    converted_emission_rate = convert_emission_rate(utility_avg_emission_rate, output_unit)
    
    # Display input data with formatted Data Year
    st.write("### Input Data:")
    input_data = {
        'Company Name': [company_name_input],
        'State': [state_input],
        'Data Year': [str(data_year_input)],  # Convert year to string for proper formatting 
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
        'CO2 ({})'.format(output_unit): [converted_emission_rate],
        'CH4 ({})'.format(output_unit): ["0.0000000000"],  # Placeholder values as no CH4 data provided
        'N2O ({})'.format(output_unit): ["0.0000000000"],  # Placeholder values as no N2O data provided
        'Total CO2e ({})'.format(output_unit): [converted_emission_rate]
    }
    df_converted = pd.DataFrame(converted_data)
    st.table(df_converted)