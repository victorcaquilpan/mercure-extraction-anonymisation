"""
extraction-anomymisation.py script
"""

# Standard Python includes
import os   
import sys
import json
from pathlib import Path
import random
# Imports for loading DICOMs
import pydicom
from pydicom.uid import generate_uid
from dicomanonymizer import anonymize,keep,replace_UID 
import string
import copy

FOLDER_EXTRACTED_DATA = "extracted-data"
FOLDER_ANONYMISED_IMAGES = "anonymised-images"

def format_number(num):
    return str(num).zfill(5)

def generate_new_task_file(task,output_file_path):

    # Remove patient_name if it exists
    if "patient_name" in task.get("info", {}):
        del task["info"]["patient_name"]

    # Write back to the same file (overwrite)
    with open(output_file_path, "w") as json_file:
        json.dump(task, json_file, indent=4) 

    print("I can write the task json file")


def save_dicom_tags(dicom_file_path,output_file_path):
    """
    Reads DICOM tags from a file and saves them to a JSON file.
    
    Args:
        dicom_file_path: Path to the DICOM file
        output_file_path: Path where to save the tags JSON file
    """
    try:
        # Read the DICOM file
        # dcm_file_in = Path(in_folder) / dicom_file_path
        # ds = pydicom.dcmread(dcm_file_in)
        ds  = pydicom.dcmread(dicom_file_path)
        
        # Write tags to text file (excluding binary data and tag (6000,3000))
        with open(output_file_path, "w") as f:
            for elem in ds:
                # Skip binary data (VR types that contain binary data)
                if elem.VR in ['OB', 'OW', 'OF', 'OD', 'UN']:
                    f.write(f"{elem.tag} {elem.keyword}: [Binary data - {len(elem.value)} bytes]\n")
                else:
                    f.write(f"{elem.tag} {elem.keyword}: {elem.value}\n")
        
        print(f"DICOM tags saved to: {output_file_path}")
        
    except Exception as e:
        print(f"Error processing DICOM file: {e}")
        sys.exit(1)


def generate_random_string(length):
    """
    Generate a random string of given length containing only letters (A-Z, a-z).

    :param length: int, the desired length of the string
    :return: str, the generated random string
    """
    letters = string.ascii_letters  # 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(letters) for _ in range(length))

def anonymising(input_dicom_path,output_dicom_path,new_patient_name):
    
    extra_anonymization_rules = {}
    def set_date_to_year(dataset, tag):
        element = dataset.get(tag)
        if element is not None:
            element.value = f"{element.value[:4]}0101" # YYYYMMDD format

    def keep_and_clean_parameter(dataset, tag):
        element = dataset.get(tag)
        if element is not None:
            element.value = str(element.value.replace("/","-"))

    def create_patient_name(dataset, tag):
        element = dataset.get(tag)
        if element is not None:
            element.value = new_patient_name

    extra_anonymization_rules[(0x0010, 0x0030)] = set_date_to_year
    extra_anonymization_rules[(0x0008, 0x103e)] = keep_and_clean_parameter
    extra_anonymization_rules[(0x0010, 0x0010)] = create_patient_name
    extra_anonymization_rules[(0x0020, 0x0010)] = replace_UID

    # Launch the anonymization
    anonymize(
        input_dicom_path,
        output_dicom_path,
        extra_anonymization_rules,
        delete_private_tags=False)

def get_study_id(dcm_file_in):
    # Load the input slice
    ds = pydicom.dcmread(dcm_file_in)
    # Check if StudyID exists, otherwise fall back to StudyInstanceUID
    if 'StudyID' in ds:
        studyid = ds.StudyID
    else:
        studyid = "unnamed-study"  # or raise an exception if you prefer
    # If there is a backslash, change it by a dash
    studyid = studyid.replace("/","-")
    return studyid

def get_series_description(file,in_folder):
    dcm_file_in = Path(in_folder) / file
    # Load the input slice
    ds = pydicom.dcmread(dcm_file_in)
    series_description = ds.SeriesDescription
    # If there is a backslash, change it by a dash
    series_description = series_description.replace("/","-")
    return series_description

def process_image(file, in_folder, out_folder, series_uid,synthetic_patient_name,slice_number,series_desc,task = None):

    dcm_file_in = Path(in_folder) / file
    # Compose the filename of the modified DICOM using the new series UID
    #out_filename = file.split("#", 1)[1]
    ds = pydicom.dcmread(dcm_file_in)
    out_filename = format_number(int(ds.InstanceNumber)) + ".dcm"
    # We  have the out_folder 
    dcm_file_out = Path(out_folder) / series_uid/out_filename
    anonymising(dcm_file_in,dcm_file_out,synthetic_patient_name)
    if slice_number == 0:
        # Save tags to text file
        output_file = os.path.join(out_folder,f"{FOLDER_EXTRACTED_DATA}/{series_desc}.json")
        save_dicom_tags(dcm_file_out,output_file)
        if task is not None:
            # Save the new_task_file
            new_study_id = get_study_id(dcm_file_out)
            generate_new_task_file(task,f"{out_folder}/{new_study_id}.json")

def main(args=sys.argv[1:]):
    """
    Main entry function of the test module. 
    The module is called with two arguments from the function docker-entrypoint.sh:
    'testmodule [input-folder] [output-folder]'. The exact paths of the input-folder 
    and output-folder are provided by mercure via environment variables
    """
    # Print some output, so that it can be seen in the logfile that the module was executed
    print(f"Hello, I am the extraction-anonymisation module")

    # Check if the input and output folders are provided as arguments
    if len(sys.argv) < 3:
        print("Error: Missing arguments!")
        print("Usage: anonymisation module [input-folder] [output-folder]")
        sys.exit(1)

    # Check if the input and output folders actually exist
    in_folder = sys.argv[1]
    out_folder = sys.argv[2]
    if not Path(in_folder).exists() or not Path(out_folder).exists():
        print("IN/OUT paths do not exist")
        sys.exit(1)

    # Load the task.json file, which contains the settings for the processing module
    try:
        with open(Path(in_folder) / "task.json", "r") as json_file:
            task = json.load(json_file)

    except Exception:
        print("Error: Task file task.json not found")
        sys.exit(1)

    # Get a new name for the patient
    synthetic_patient_name = generate_random_string(8)

    # Create a folder to store the json files with the extracted data
    if not os.path.exists(os.path.join(out_folder,FOLDER_EXTRACTED_DATA)):
        os.makedirs(os.path.join(out_folder,FOLDER_EXTRACTED_DATA))

    series = {}
    for entry in os.scandir(in_folder):
        if entry.name.endswith(".dcm") and not entry.is_dir():
            # Get the Series UID from the file name
            seriesString = entry.name.split("#", 1)[0]
            # If this is the first image of the series, create new file list for the series
            if not seriesString in series.keys():
                series[seriesString] = []
            # Add the current file to the file list
            series[seriesString].append(entry.name)

    # Now loop over all series found
    for series_number, item in enumerate(series):
        # # Get the series desciption from the first instance
        for image_filename in series[item]:
            series_desc = get_series_description(image_filename,in_folder)
            break
        #     # Save tags to text file
        #     output_file = os.path.join(out_folder,f"{FOLDER_EXTRACTED_DATA}/{series_desc}.json")
        #     save_dicom_tags(image_filename, in_folder,output_file)
        output_series = os.path.join(FOLDER_ANONYMISED_IMAGES,series_desc)
        # Create the output folders for the series
        if not os.path.exists(os.path.join(out_folder,output_series)):
            os.makedirs(os.path.join(out_folder,output_series))

        # Loop over all the slices
        for slice_number,image_filename in enumerate(series[item]):
            series_desc = get_series_description(image_filename,in_folder)
            # We are storing the task.json file just once at the first series
            if series_number == 0:
                process_image(image_filename, in_folder, out_folder, output_series,synthetic_patient_name,slice_number,series_desc,task)
            # After, we are storing the series normally
            else:
                process_image(image_filename, in_folder, out_folder, output_series,synthetic_patient_name,slice_number,series_desc)

if __name__ == "__main__":
    main()
