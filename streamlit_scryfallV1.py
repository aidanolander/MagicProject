# Streamlit Scryfall App V1

import streamlit as st
import pandas as pd
from io import BytesIO
import requests
import time


st.title('Excel File Uploader with Multiple Sheets')

# Upload Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read Excel file
    sheet_name = st.selectbox("Select a sheet", pd.ExcelFile(uploaded_file).sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    df.columns = ['input_card_names']

    # Display the dataframe
    st.write(df)


def get_card_details(card_name):
    url = f"https://api.scryfall.com/cards/named"
    params = {'fuzzy': card_name}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        card_data = response.json()
        return card_data
    else:
        return f"An error occurred: {response.status_code}"

def get_multiple_cards(card_names):
    cards_details = []
    for card_name in card_names:
        card_details = get_card_details(card_name)
        if isinstance(card_details, dict):
            cards_details.append(card_details)
        time.sleep(0.1)  # Add delay to respect rate limits
    return cards_details

# Function to convert DataFrame to Excel and get the BytesIO object
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

try:

    card_names = list(df.input_card_names)
    cards_details = get_multiple_cards(card_names)
    card_df = pd.DataFrame(cards_details)
    card_df['usd_price'] = card_df['prices'].apply(lambda x: x.get('usd', 'N/A'))

    output_card_df = card_df[['name', 'type_line', 'mana_cost', 
                            'cmc', 'oracle_text', 'usd_price', 
                            'power', 'toughness','released_at']]
    output_card_df['cmc'] = output_card_df['cmc'].astype('int32')
    output_card_df['usd_price'] = output_card_df['usd_price'].astype('float64')
    output_card_df['released_at'] = pd.to_datetime(output_card_df['released_at'])

    # Button to download the Excel file
    if st.button('Download Excel'):
        excel_data = to_excel(output_card_df)
        st.download_button(
            label='Download Excel File',
            data=excel_data,
            file_name='data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )



    
except:
    pass



