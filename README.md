# Phonebook
A phone book application for linux with Web UI.
Runs in a docker container, built using a Jenkinsfile. 

# Notes
A clone of https://github.com/karissame/myPhonebookwith some changes:
 - Python 2 to Python 3
 - Removed profile picture treatment
 - Added ID per user
 - Added prometheus instrumentation
 - Added logging
 - Added Dockerfile, Jenkinsfile and all the necessary k8s yaml files.  
 - Includes a basic load test, done with Jmeter
