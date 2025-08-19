# Import python packages
import streamlit as st
import snowflake.snowpark.functions as F
import pandas as pd
import requests # This line is critical for the requests.get() call to work

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw: ")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Get the current active Snowpark session using st.connection
# This will now look for credentials in .streamlit/secrets.toml
cnx = st.connection("snowflake")
session = cnx.session()


# Add a text input for the smoothie's name
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your Smoothie will be:', name_on_order)


# Load data from the 'fruit_options' table
my_dataframe = session.table("smoothies.public.fruit_options").select(F.col('FRUIT_NAME'))
pd_dataframe = my_dataframe.to_pandas()
fruit_names = pd_dataframe['FRUIT_NAME'].tolist()

# Create a multiselect widget
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# Only proceed if the user has selected ingredients
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    st.write('### Your Smoothie Order:')
    st.write(ingredients_string)

    # Construct the INSERT statement as a string
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    
    # Create the submit button
    time_to_insert = st.button('Submit Order')

    # Check if the button was clicked
    if time_to_insert:
        # Execute the SQL statement using the Snowpark session
        # .collect() will run the query and return the results
        session.sql(my_insert_stmt).collect()
        
        # Show a success message with the user's name
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# New section to display smoothie root nutrition information
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Expose the JSON data from the API response
sf_df = pd.json_normalize(smoothiefroot_response.json())

# Put the JSON data into a dataframe and display it
st.dataframe(data=sf_df, use_container_width=True)
