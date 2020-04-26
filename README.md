# Phonebook
A phone book application for linux with a Web UI. Written in Python/MySQL/Flask. 
Runs in a docker container, built using a Jenkinsfile. 

# Notes
A clone of https://github.com/karissame/myPhonebookwith some changes:
 - Python 2 to Python 3
 - Removed profile picture treatment
 - Added ID per user
 - Moved MySQL cursor properties to environment variables.
 - Added prometheus instrumentation
 - Added logging
 - Added Dockerfile, Jenkinsfile and all the necessary k8s yaml files.  
 - Includes a basic load test, done with Jmeter
 - Makes use of k8s secrets
