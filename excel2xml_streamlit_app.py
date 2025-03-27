import streamlit as st
import pandas as pd
from lxml import etree as et
import shutil
import os

st.title("iTunes XML Generator 🍏")
st.markdown("Create iTunes Episodic XML's by uploading an excel metadata spreadsheet")
st.markdown("More Details about iTunes Package TV Specification 5.3.6  >>> [Click Here](https://help.apple.com/itc/tvspec/#/apdATD1E170-D1E1A1303-D1E170A1126)")

col1, col2 = st.columns(2)
with col1:
    share = st.checkbox("Asset Share (optional)")
    bundle = st.checkbox("Bundle Only (optional)")
    with open('TEMPLATES/XXXXX_SX_Metadata_XX_iTunes_TV.xlsx', 'rb') as my_file:
        st.download_button(label = 'Download Excel Template', data = my_file, file_name = 'XXXXX_SX_Metadata_XX_iTunes_TV.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

with col2:
    option = st.radio(
        "Select a Locale Name",
        ("en-CA", "en-AU", "en-GB", "de-DE", "fr-FR", "us-US")  # Added "us-US"
    )

uploaded_file = st.file_uploader("Create XML")
try:
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file)

        if share:
            option = option + "_ASSET_SHARE"  # Add ASSET_SHARE if checkbox is checked

        # Try loading the template with the ASSET_SHARE version
        xml_template_path = f'TEMPLATES/iTunes_TV_EPISODE_TEMPLATE_v5-3_{option}.xml'

        if not os.path.exists(xml_template_path):
            # Fall back to default template if ASSET_SHARE template is not found
            st.warning(f"Template {xml_template_path} not found. Falling back to default template.")
            xml_template_path = f'TEMPLATES/iTunes_TV_EPISODE_TEMPLATE_v5-3_{option.replace("_ASSET_SHARE", "")}.xml'

        # Check if the default template exists
        if not os.path.exists(xml_template_path):
            st.error(f"Template file not found: {xml_template_path}")
            st.stop()

        # Load the template
        tree = et.parse(xml_template_path)
        template_root = tree.getroot()

        # Create folders
