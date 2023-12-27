import requests
from pathlib import Path

def download_dataset(directory: str):
    # Create directory for data files if not exists
    Path(directory).mkdir(parents=True, exist_ok=True)

    # HuggingFace endpoint to retrieve list of wikimedia/wikipedia parquet file urls
    dataset_endpoint = "https://huggingface.co/api/datasets/wikimedia/wikipedia/parquet/20231101.en/train"

    # The response is a string-literal representation of a list of strings,
    # so we need to convert it to an actual list of url strings
    file_url_list = requests.get(dataset_endpoint).text[1:-2].replace('"', '').split(",")

    for url in file_url_list:
        filename = url.split("/")[-1]
        filepath = directory + "/" + filename
        if (Path(filepath).exists()):
            continue
        # Save the file
        open(filepath, "wb").write(requests.get(url, allow_redirects=True).content)
        
        # Remove/Comment this `break` line to download all data files (>400MB each)
        # Leaving this here for now to limit file downloads on local machine
        break
