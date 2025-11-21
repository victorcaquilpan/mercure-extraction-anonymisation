# Anonymisation and Extraction Module using Mercure

# Mercure pipeline

Here is the documentation for running the Mercure pipeline for running locally.

## Purpose

This module pick DICOM images and anonymised them using **https://pypi.org/project/dicom-anonymizer/**. After the anonimisation is done, the main DICOM tags as stored in a JSON file per each series. Apart from that, a task.json file is generated to keep the main information of the input series and the process done with mercure. 

The structure of the output is illustrated below:
```
.
├── Study1 (newUID)/
│   ├── anomyised-images/
│   │   ├── Series1 (SeriesDescription)
|   |   |   ├──  image1.dcm
|   |   |   ├──  image2.dcm
|   |   |   └──  imagen.dcm 
|   |   └── Series2 
|   |       ├──  image1.dcm
|   |       └──  image2.dcm
│   ├── extracted-data/
│   │   ├── Series1.json
|   |   └── Series2.json
|   └── task.json (newStudyID)
└── Study2...
```

## Requirements

* Running Docker

## Installation Steps


1) Clone the mercure repository: 

```bash
git clone https://github.com/mercure-imaging/mercure.git
```

2) Install Mercure using Docker by pulling docker images and run containers. 
```bash
sudo ./install.sh docker
```
At the end of the installation, **mercureimaging** Docker images should be donwloaded. 
Mercure is using several containers for all the modules.Also a directory in **/opt/mercure** is created.


3) Access to Mercure app.
```
http://127.0.0.1:8000/
```

4) Create docker image

The module can be installed on a mercure server using the Modules page of the mercure web interface. Enter the following line into the "Docker tag" field. Mercure will automatically download and install the module:

```
aiml/extraction-anonym:latest
```

In Mercure, this have to be working for the Study level. To create the Docker image, the next lines should be run:

```bash
cd extraction-module
make build
# Check image
docker images
# You should see aiml/extraction-anonymisation
```

## Setting up Mercure 

1) At Mercure, in **Modules** we need to add our module by selecting the Docker image:
* Name of module: extraction
* Docker tag: **aiml/extraction-anonymisation**
* Module type: mercure

2) In **Targets**, we need to add a new target, whose type is Folder.
* Folder: /opt/mercure/data/mercure-output
* Exclusion filter: task.json

3) In **Rules**, we need to add a new rule, defining the pipeline and the input target
