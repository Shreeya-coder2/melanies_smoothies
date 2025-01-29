# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie
    """
)

name_on_order = st.text_input('Name on Smoothie: ')
st.write('The name on your smoothie will be ', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', pd_df['fruit_name'].tolist()
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Get the 'search_on' value for the chosen fruit
        search_on = pd_df.loc[pd_df['fruit_name'] == fruit_chosen, 'search_on'].iloc[0]

        if search_on:  # Check if search_on is not None or empty
            st.subheader(fruit_chosen + ' Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            
            if fruityvice_response.status_code == 200:
                fv_data = fruityvice_response.json()
                st.dataframe(data=fv_data, use_container_width=True)
            else:
                st.error(f"Failed to retrieve data for {fruit_chosen}")
        else:
            st.warning(f"No search value found for {fruit_chosen}")
   
    my_insert_stmt = """ 
    insert into smoothies.public.orders(ingredients)
    values ('""" + ingredients_string + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
