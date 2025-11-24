import os
import pandas as pd
import json

def create_lookup(input_csv, output_mercure, output_csv):
    """
    Creates a lookup CSV file mapping ACCESSION-NUMBERs to filenames in the output mercure directory.
    input_csv: Path to the input CSV file containing ACCESSION-NUMBERs.
    output_mercure: Path to the output mercure directory containing processed files.
    output_csv: Path to the output CSV file to write the lookup mapping.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Ensure the column name is correct
    if 'ACCESSION-NUMBER' not in df.columns:
        raise ValueError("Input CSV must contain 'ACCESSION-NUMBER' column")

    # Create a new column in the DataFrame for filenames, initialized to None
    df['MERCURE-OUTPUT'] = None

    # Read the output mercure directory to get the list of files
    outputs = set(os.listdir(output_mercure))
    
    # For each folder in the output mercure directory, get the accession number and map it to the filename
    mapping = {}
    for subfolder in outputs:
        files = os.listdir(os.path.join(output_mercure, subfolder))
        task_file = [f for f in files if f.endswith('.json')]
        if task_file:
            # Read the JSON file to get the accession number
            task_path = os.path.join(output_mercure, subfolder, task_file[0])
            with open(task_path, 'r') as f:
                task_data = f.read()
                # Parse the JSON content
                parsed_data = json.loads(task_data)
            # Extract accession number from the JSON content
            accession_number = parsed_data["info"]["acc"]
            mapping[accession_number] = subfolder
    print("Mapping:", mapping)
    # Update the DataFrame with the corresponding filenames
    for index, row in df.iterrows():
        accession_number = row['ACCESSION-NUMBER']
        if accession_number in mapping:
            df.at[index, 'MERCURE-OUTPUT'] = mapping[accession_number]

    # Write the updated DataFrame to the output CSV file
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    input_csv = "sample-input/accession-numbers.csv"
    output_mercure = "sample-output/mercure-output"
    output_csv = "sample-output/lookup-table.csv"
    create_lookup(input_csv, output_mercure, output_csv)