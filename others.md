forwarding mercure 
ssh -p 2222 -L 8001:localhost:8000 trials@203.47.107.188

forwarding orthanc
ssh -p 2222 -L 8043:localhost:8042 trials@203.47.107.188

forward orthanc port to transfer imagess
ssh -p 2222 -L 4242:localhost:4242 trials@203.47.107.188
Locally run: 
sudo dcmsend localhost 4242 \
  --scan-directories \
  --recurse \
  Pseudo-PHI-DICOM-Data
To transfer the files to the Orthanc at the VM
