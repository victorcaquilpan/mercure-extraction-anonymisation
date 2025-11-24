# Anonymisation and Extraction Module using Mercure

# Mercure pipeline

Here is the documentation for running the Mercure pipeline for running locally.

## Purpose

This module pick DICOM images and anonymised them using **https://pypi.org/project/dicom-anonymizer/**. After the anonimisation is done, the main DICOM tags as stored in a JSON file per each series. Besides that, a task.json file is generated to keep the main information of the input series and the process done with mercure. 

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

* Name of the target: local
* Folder: /opt/mercure/data/mercure-output
* Exclusion filter: task.json

Note: Mercure will store the output in **/opt/mercure**

3) In **Rules**, we need to add a new rule, defining the pipeline and the input target:

* Name of the rule: extraction-mri
* Selection rule: For our demo, we are using **tags.Modality == "MR"**. Any rule using the DICOM tags can be used. 
* Action: Processing & Routing
* Trigger: Completed Study
* Completion condition: Timeout Reached
* In Processing tab: Select **extraction** module. 
* In Routing tab: Select **local**.

## Testing

We can test sending data by using:

```bash
dcmsend 172.19.0.1 11112 --scan-directories --recurse Pseudo-PHI-DICOM-Data
```

Or also using Orthanc, following the [Docker installation steps](https://orthanc.uclouvain.be/book/users/docker.html#docker). 

```bash
cd orthanc-setting
docker-compose up -d
```

and to access to the web app, you can go to http://localhost:8042/. Pseudo-data might be uploded to Orthanc using:

```bash
dcmsend 172.19.0.1 4242 --scan-directories --recurse Pseudo-PHI-DICOM-Data
```

## Making DICOM Queries

We can look for DICOM series using Accession Numbers and also filtering by Study Descriptions and Series Descriptions. Orthanc allows to run the pipeline straight away to these images. The output folder be available at **/opt/mercure/mercure-output**, where each study go to a new folder whose name is a random number.

This is what you see in the app:

![DICOM Query process](./images/dicom-query.png)

This is what you would see locally:

![Ouput](./images/output.png)

The structure of the output is defined by:

* **main output folder**: This is a main directory where the data is stored. Located at **/opt/mercure/mercure-output**.
* **study folder**: Filename is assigned randomly.
* **anonymised-images**: it contains one folder per session and in each one, there will be available the images. The filename is the instance number.
* **extracted-data folder**: It contains the DICOM tags of the first DICOM image for that session. Personal information is removed.
* **task.json file**: Filename is based on the studyID. It contains the pipeline process performed, the sessions and the accession number.
* **.complete** and **.processing** are just placeholders to confirm the preprocessing was completed. mercure create them by default.

You can find the output of this demo in the **sample-output** folder.


### Notes

* They go to provide to me access to a machine, where I can run mercure. They go to provide a VPN to connect.
* For mercure, I need to remove the PatientName from the output. **Done**.
* Remove the worksheets (in the cases where a document is stored in the middle of the DICOM images). **Need a sample to test**
* Provide a lookup table. **Easily, we can create a look-up table from the task.json files stored in each study, as they keep the accession number**.
* The JSON files should have the data of the anonymised images. **Done**
* Use studyID as name for the task.Json file: **Done**

### To solve:

* Is there any limitation that mercure can store data just in "/op/mercure"?

