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

        # Add "_ASSET_SHARE" if the checkbox is selected
        if share:
            option = option + "_ASSET_SHARE"

        # Force template to use us-US for button press
        if "us-US" in option:
            xml_template_path = "TEMPLATES/iTunes_TV_EPISODE_TEMPLATE_v5-3_us-US.xml"
        else:
            xml_template_path = f'TEMPLATES/iTunes_TV_EPISODE_TEMPLATE_v5-3_{option}.xml'

        # Check if the correct template exists for the selected option
        if not os.path.exists(xml_template_path):
            st.error(f"Template file not found: {xml_template_path}")
            st.stop()

        # Load the template XML
        tree = et.parse(xml_template_path)
        template_root = tree.getroot()

        # Create folders for the output XML files and iTunes package
        package_folder = "iTunes Package with XML"
        os.makedirs(package_folder, exist_ok=True)
        xml_folder = "XML"
        os.makedirs(xml_folder, exist_ok=True)

        # Iterate over the rows of the dataframe and populate the template with values
        for index, row in dataframe.iterrows():
            if index > 2:
                package_name = str(row['Unnamed: 23']).strip()

                if not package_name or package_name.lower() == 'nan':
                    st.warning(f"Skipping row {index + 1}: Invalid package name.")
                    continue

                # Apply values from the Excel file to the XML template
                template_root[2][14][0].attrib['code'] = str(row['Unnamed: 7'])  # Rating code

                if bundle:
                    for bundle_only in template_root[2].iter('{http://apple.com/itunes/importer}products'):
                        bundle_only[0][3].text = 'true'

                if share:
                    for shared_asset_id in template_root[2].iter('{http://apple.com/itunes/importer}share_assets'):
                        shared_asset_id.attrib['vendor_id'] = str(row['Unnamed: 27'])

                # Handle "mov" and "scc" file names for English locales
                if "en" in option and not "_ASSET_SHARE" in option:
                    template_root[2][16][0][0][1].text = package_name + '.mov'  # mov file name
                    template_root[2][16][0][1][1].text = package_name + '.scc'  # scc file name

                if not "en" in option and not "_ASSET_SHARE" in option:
                    template_root[2][15][0][0][1].text = package_name + ".mov"  # mov file name

                # Update other metadata fields in the XML template
                for container_id in template_root[2].iter('{http://apple.com/itunes/importer}container_id'):
                    container_id.text = str(row['ITUNES'])

                for container_position in template_root[2].iter('{http://apple.com/itunes/importer}container_position'):
                    container_position.text = str(row['Unnamed: 24'])

                for vendor_id in template_root[2].iter('{http://apple.com/itunes/importer}vendor_id'):
                    vendor_id.text = str(row['Unnamed: 23'])

                for episode_production_number in template_root[2].iter('{http://apple.com/itunes/importer}episode_production_number'):
                    episode_production_number.text = str(row['TITLE'])

                for title in template_root[2].iter('{http://apple.com/itunes/importer}title'):
                    title.text = str(row['Unnamed: 3'])

                for studio_release_title in template_root[2].iter('{http://apple.com/itunes/importer}studio_release_title'):
                    studio_release_title.text = str(row['Unnamed: 4'])

                for description in template_root[2].iter('{http://apple.com/itunes/importer}description'):
                    description.text = str(row['Unnamed: 5'])

                for release_date in template_root[2].iter('{http://apple.com/itunes/importer}release_date'):
                    full_date = str(row['Unnamed: 14'])
                    release_date.text = full_date[0:10]

                for copyright in template_root[2].iter('{http://apple.com/itunes/importer}copyright_cline'):
                    copyright.text = str(row['Unnamed: 15'])

                for sales_start_date in template_root[2].iter('{http://apple.com/itunes/importer}products'):
                    full_sale_date = str(row['Unnamed: 34'])
                    sales_start_date[0][1].text = full_sale_date[0:10]

                # Create package folders
                package = f'{package_name}.itmsp'
                xml = "metadata.xml"
                os.makedirs(package, exist_ok=True)
                package_path = os.path.abspath(package)

                # Save XML files to disk
                tree.write(f'{package_name}.xml', encoding="utf-8", xml_declaration=True)
                tree.write(xml, encoding="utf-8", xml_declaration=True)

                xml_path = os.path.abspath(xml)
                shutil.move(xml_path, package_path)
                shutil.move(os.path.abspath(package_path), os.path.abspath(package_folder))
                shutil.move(os.path.abspath(f'{package_name}.xml'), os.path.abspath(xml_folder))

        # Create ZIP file containing the generated files
        zip_name = container_id.text if container_id.text else "default_zip"
        os.mkdir(zip_name)
        shutil.move(os.path.abspath(package_folder), os.path.abspath(zip_name))
        shutil.move(os.path.abspath(xml_folder), os.path.abspath(zip_name))
        shutil.make_archive(zip_name, 'zip', os.path.abspath(zip_name))
        shutil.rmtree(zip_name)

        # Provide download button for the ZIP file
        with open(zip_name + '.zip', 'rb') as f:
            st.download_button('Download Zip', f, file_name=zip_name + '.zip')

except Exception as e:
    st.error(f"An error occurred: {e}")
