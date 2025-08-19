# Import python packages
import streamlit as st
import snowflake.snowpark.functions as F
import pandas as pd
import requests

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


# Load data from the 'fruit_options' table, including the new 'SEARCH_ON' column
my_dataframe = session.table("smoothies.public.fruit_options").select(F.col('FRUIT_NAME'), F.col('SEARCH_ON'))
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
    
    # New section to display smoothie root nutrition information for EACH chosen fruit
    st.subheader('Nutrition Information')
    
    # Loop through each chosen fruit
    for fruit_chosen in ingredients_list:
        # Get the search term from the Pandas DataFrame using the user's selected fruit name
        search_on = pd_dataframe.loc[pd_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f'{fruit_chosen} Nutrition Information')
        
        # Use the search_on term in the API call
       fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        
        # Check if the API request was successful before trying to display the data
        if smoothiefroot_response.status_code == 200:
            sf_df = pd.json_normalize(smoothiefroot_response.json())
            st.dataframe(data=sf_df, use_container_width=True)
        else:
            # Display a message if the fruit was not found
            st.write(f"Sorry, data for {fruit_chosen} was not found.")

    # Create a checkbox to mark the order as filled
    order_filled = st.checkbox('Mark as Filled')

    # Create the submit button
    time_to_insert = st.button('Submit Order')

    # Check if the button was clicked
    if time_to_insert:
        # Construct the INSERT statement as a string
        # Now we include the 'order_filled' column and its corresponding value
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}', {order_filled})
        """
        
        # Execute the SQL statement using the Snowpark session
        session.sql(my_insert_stmt).collect()
        
        # Show a success message with the user's name
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

