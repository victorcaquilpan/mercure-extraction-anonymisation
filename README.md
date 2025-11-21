# Anonymisation and Extraction Module using Mercure

# Mercure pipeline

Here is the documentation for running the Mercure pipeline for running locally in SA health.

## Requirements

* Running Docker

## **Steps**

1) Clone the mercure repository: 

```bash
git clone https://github.com/mercure-imaging/mercure.git
```

2) Install mercure using docker 

```bash
sudo ./install.sh docker
```


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

## Installation

The module can be installed on a mercure server using the Modules page of the mercure web interface. Enter the following line into the "Docker tag" field. mercure will automatically download and install the module:

```
aiml/extraction-anonym-test:latest
```

In Mercure, this have to be working for the Study level. 
