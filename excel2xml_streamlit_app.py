import streamlit as st
import pandas as pd
from lxml import etree as et
from zipfile import ZipFile
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
        st.download_button(label='Download Excel Template', data=my_file, file_name='XXXXX_SX_Metadata_XX_iTunes_TV.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

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
            option += "_ASSET_SHARE"

        # Path to the templates
        xml_template_path = os.path.join(os.path.dirname(__file__), 'TEMPLATES', f'iTunes_TV_EPISODE_TEMPLATE_v5-3_{option}.xml')
        default_template_path = os.path.join(os.path.dirname(__file__), 'TEMPLATES', 'iTunes_TV_EPISODE_TEMPLATE_v5-3_us-US.xml')

        # Check if template exists, else use default template
        if not os.path.exists(xml_template_path):
            st.error(f"Template XML file not found: {xml_template_path}")
            st.error(f"Falling back to default template: {default_template_path}")
            xml_template_path = default_template_path  # Use default template if locale-specific template not found

        tree = et.parse(xml_template_path)
        template_root = tree.getroot()
        package_folder = "iTunes Package with XML"
        xml_folder = "XML"
        os.makedirs(package_folder, exist_ok=True)
        os.makedirs(xml_folder, exist_ok=True)

        for index, row in dataframe.iterrows():
            if index > 2:
                package_name = str(row['Unnamed: 23']).strip()

                if not package_name or package_name.lower() == 'nan':
                    st.warning(f"Skipping row {index+1}: Invalid package name.")
                    continue

                template_root[2][14][0].attrib['code'] = str(row['Unnamed: 7'])  # rating code

                if bundle:
                    for bundle_only in template_root[2].iter('{http://apple.com/itunes/importer}products'):
                        bundle_only[0][3].text = 'true'

                if share:
                    for shared_asset_id in template_root[2].iter('{http://apple.com/itunes/importer}share_assets'):
                        shared_asset_id.attrib['vendor_id'] = str(row['Unnamed: 27'])

                if "en" in option and "_ASSET_SHARE" not in option:
                    template_root[2][16][0][0][1].text = package_name + '.mov'  # mov file name
                    template_root[2][16][0][1][1].text = package_name + '.scc'  # scc file name

                if "en" not in option and "_ASSET_SHARE" not in option:
                    template_root[2][15][0][0][1].text = package_name + ".mov"  # mov file name

                for container_id in template_root[2].iter('{http://apple.com/itunes/importer}
