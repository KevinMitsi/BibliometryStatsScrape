import os
import json
import xml.etree.ElementTree as ET
import glob
import logging
import re # Import the regex module for splitting subjects
from datetime import datetime

# --- Helper Functions (kept outside the class for clarity, or could be static methods) ---
logger = logging.getLogger(__name__)

def _xml_element_to_dict(element):
    """
    Recursively converts an XML element and its children into an intermediate
    Python dictionary structure.
    Handles attributes (@attributes) and text content (#text).
    If multiple children have the same tag, they are put into a list.
    This structure will be cleaned up later.
    """
    d = {}
    # Handle attributes
    if element.attrib:
        d['@attributes'] = dict(element.attrib)

    # Handle children
    children = list(element)
    if children:
        for child in children:
            child_tag = child.tag
            # Recursive call using the helper
            child_data = _xml_element_to_dict(child)

            if child_tag in d:
                # If tag already exists, make it a list if not already
                if not isinstance(d[child_tag], list):
                    d[child_tag] = [d[child_tag]]
                d[child_tag].append(child_data)
            else:
                # First time seeing this tag
                d[child_tag] = child_data

    # Handle text content (if any, and not just whitespace)
    if element.text is not None and element.text.strip():
         d['#text'] = element.text.strip()

    # Return the constructed dictionary (even if empty or only #text/@attributes)
    return d

def _clean_data_structure(data):
    """
    Recursively cleans the intermediate dictionary structure:
    - Removes '@attributes' keys.
    - If a dictionary contains only '#text' (and optional '@attributes'),
      replaces the dictionary with the value of '#text'.
    - Removes '#text' if the dictionary contains other keys (assuming it was
      parent text before children, which is often less critical in data conversion).
    """
    if isinstance(data, dict):
        # Special case: If the dictionary is just {'#text': value} (and maybe @attributes)
        # Collapse it to just the value.
        if '#text' in data and len(data) <= 2 and all(k in ['#text', '@attributes'] for k in data.keys()):
             return data.get('#text', '') # Return the text value, discarding attributes here

        # General case: Process children and other keys
        new_dict = {}
        for key, value in data.items():
            # Skip attributes
            if key == '@attributes':
                continue
            # Skip #text as it's handled by the special case or discarded if children exist
            if key == '#text':
                 continue

            # Recursively clean the value
            cleaned_value = _clean_data_structure(value)

            # Add to the new dictionary
            new_dict[key] = cleaned_value

        return new_dict

    elif isinstance(data, list):
        # If it's a list, clean each item in the list
        return [_clean_data_structure(item) for item in data]

    else:
        # If it's a simple value (string, number, bool, None), return as is
        return data

def _format_subjects_string(subject_string):
    """
    Splits a string of subjects separated by ',' or ';' into a list of strings.
    Removes leading/trailing whitespace from each subject and filters out empty strings.
    """
    if not isinstance(subject_string, str):
        # If subjects wasn't a string after cleaning, return it as is (e.g., None or empty list)
        return subject_string

    # Split by comma or semicolon, handle multiple delimiters next to each other
    subjects_list = re.split(r'[;,]+', subject_string)

    # Strip whitespace from each subject and filter out any empty strings
    cleaned_subjects = [subject.strip() for subject in subjects_list if subject.strip()]

    return cleaned_subjects


# --- Converter Class ---
class XmlToJsonConverter:
    """
    A class to convert XML files from a specified directory into a single
    cleaned and formatted JSON structure and save it to a file.
    """
    # Set the default directory where XML files are expected
    DEFAULT_XML_DIRECTORY = "../refs"

    def __init__(self, xml_dir=None, output_dir=None):
        """
        Initializes the converter.

        Args:
            xml_dir (str, optional): The path to the directory containing XML files.
                                     Defaults to XmlToJsonConverter.DEFAULT_XML_DIRECTORY.
            output_dir (str, optional): The directory where the output JSON file will be saved.
                                      Defaults to the current working directory ('.').
        """
        self.xml_directory = xml_dir if xml_dir is not None else self.DEFAULT_XML_DIRECTORY
        self.output_directory = output_dir if output_dir is not None else "."

        # Ensure the output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        print(f"Converter initialized. Looking for XMLs in: {self.xml_directory}")
        print(f"Output JSON will be saved in: {self.output_directory}")

    def _convert_all_xmls(self):
        """
        Internal method to find, parse, and convert all XML files in the
        configured directory into the raw intermediate dictionary format.
        Returns a list of these dictionaries or None on failure/no files.
        """
        if not os.path.isdir(self.xml_directory):
            print(f"Error: XML directory not found: {self.xml_directory}")
            return None

        # Find all XML files
        xml_pattern = os.path.join(self.xml_directory, "*.xml")
        xml_files = glob.glob(xml_pattern)

        if not xml_files:
            print(f"No XML files found matching pattern: {xml_pattern}")
            return [] # Return empty list if no files, not None

        all_raw_data = []
        print(f"Found {len(xml_files)} XML files. Starting raw conversion...")

        # Process each XML file
        for i, xml_file in enumerate(xml_files):
            # print(f"Processing file {i+1}/{len(xml_files)}: {os.path.basename(xml_file)}...")
            try:
                # Parse the XML file
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Convert the root element to the raw dictionary format
                xml_dict = _xml_element_to_dict(root)
                all_raw_data.append(xml_dict)
                # print("  Raw conversion successful.")
            except ET.ParseError as e:
                print(f"  Error parsing XML file {xml_file}: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred while processing {xml_file}: {e}")

        return all_raw_data

    def convert_xmls_to_list(self):
        """
        Converts XML files from the configured directory into a list of cleaned
        and formatted Python dictionaries WITHOUT saving to a file.
        This is suitable for returning directly in an API response.

        Returns:
            list: A list of cleaned dictionaries. Returns an empty list on failure
                  or if no data was processed/cleaned.
        """
        logger.info("Starting XML to list conversion (in-memory)...")

        # 1. Convert XMLs to raw intermediate dictionaries
        raw_data_list = self._convert_all_xmls()

        if raw_data_list is None:  # Directory error from _convert_all_xmls
            return []  # Return empty list
        # _convert_all_xmls already returns [] if no files found

        logger.info(f"Starting data cleaning and formatting for {len(raw_data_list)} records (in-memory)...")
        cleaned_data_list = []

        # 2. Clean and format each record
        for raw_record in raw_data_list:
            cleaned_record = _clean_data_structure(raw_record)

            # Apply specific formatting for 'subjects'
            if isinstance(cleaned_record, dict) and 'subjects' in cleaned_record:
                cleaned_record['subjects'] = _format_subjects_string(cleaned_record.get('subjects'))

            # Only append if the cleaned record is not None or empty after cleaning
            # The cleaning function might return None or empty dict/list depending on input
            # Let's assume _clean_data_structure returns a dict or list, or a simple value.
            # If it's a meaningful dict/value, add it.
            if cleaned_record is not None and cleaned_record != {}:
                cleaned_data_list.append(cleaned_record)

        if not cleaned_data_list:
            logger.warning("No data remained after cleaning.")
            return []  # Return empty list

        logger.info(f"Successfully processed {len(cleaned_data_list)} records into a list.")
        return cleaned_data_list  # Return the list

    def convert_clean_and_save(self, output_filename=None):
        """
        Orchestrates the process: converts XMLs, cleans the structure,
        formats specific fields (like subjects), and saves the final
        result as a single JSON file.

        Args:
            output_filename (str, optional): The desired name for the output JSON file.
                                             If None, defaults to 'cleaned_converted_data_<timestamp>.json'.
                                             Saved in self.output_directory.

        Returns:
            str or None: The full path to the saved JSON file if successful, None otherwise.
        """
        # 1. Convert XMLs to raw intermediate dictionaries
        raw_data_list = self._convert_all_xmls()

        if raw_data_list is None: # Directory error
            return None
        if not raw_data_list: # No files found or converted
            print("No data generated from XML files to clean and save.")
            return None

        print(f"Starting data cleaning and formatting for {len(raw_data_list)} records...")
        cleaned_data_list = []

        # 2. Clean and format each record
        for i, raw_record in enumerate(raw_data_list):
            # print(f"Cleaning record {i+1}/{len(raw_data_list)}...")
            # Apply general cleaning (_remove #text, @attributes, collapse simple text nodes)
            cleaned_record = _clean_data_structure(raw_record)

            # Apply specific formatting for 'subjects'
            if isinstance(cleaned_record, dict) and 'subjects' in cleaned_record:
                # After general cleaning, subjects might be a string or already a list/dict depending on XML
                # We expect it to be a string like "subj1, subj2; subj3"
                cleaned_record['subjects'] = _format_subjects_string(cleaned_record.get('subjects'))

            cleaned_data_list.append(cleaned_record)
            # print("  Record cleaned and formatted.")


        if not cleaned_data_list:
            print("No data remained after cleaning.")
            return None

        # 3. Determine the output file path
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"libs_{timestamp}.json"

        full_output_path = os.path.join(self.output_directory, output_filename)

        # 4. Save the cleaned and formatted data as JSON
        try:
            with open(full_output_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data_list, f, ensure_ascii=False, indent=4)
            print(f"\nSuccessfully processed and saved {len(cleaned_data_list)} records.")
            print(f"Cleaned JSON data saved to: {full_output_path}")
            return full_output_path # Return the path on success
        except IOError as e:
            print(f"Error saving JSON file {full_output_path}: {e}")
            return None


# --- Example Usage (for testing/demonstration when run directly) ---
if __name__ == "__main__":
    print("Running conversor.py directly for demonstration.")
    print(f"Attempting to convert and clean XMLs from the default directory: {XmlToJsonConverter.DEFAULT_XML_DIRECTORY}")

    # Create an instance of the converter using the default XML directory '../refs'
    # The output will be saved in the current directory by default.
    converter = XmlToJsonConverter()

    # Or, explicitly specify input/output directories if needed for testing
    # converter = XmlToJsonConverter(xml_dir="./test_xmls", output_dir="./output_json")

    # Ensure the default XML directory exists for the demonstration run
    os.makedirs(XmlToJsonConverter.DEFAULT_XML_DIRECTORY, exist_ok=True)
    # You would need to place some sample .xml files in ../refs for this demonstration to work.

    # Run the full conversion, cleaning, and saving process
    saved_file = converter.convert_clean_and_save("libs.json")

    if saved_file:
        print(f"\nDemonstration complete. Check the file: {saved_file}")
    else:
        print("\nDemonstration failed.")