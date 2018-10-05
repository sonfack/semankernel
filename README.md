# semankernel
The main objective of this project is to develop a semantic annotation framework to annotate semantically some datasets using several Ontologies.

##  Installation instructions 
In order to use this app, you need and Elasticsearch server that will be used to store ontologies. 
In the common/database.py file

    def __init__(self, address='172.17.0.2', port=9200)
   
  replace the 172.17.0.2 by your Elasticsearch server address. 

After this step, run the app and install all libraries  and go to the backend to upload your ontologies in the Elasticsearch database. 
http://ip-address/administrator 


## File structure 
In our project folder, we have 02 important folders for the project:

 - src
 - common
 - template 
 - data 
 
### src 
This folder contains the 

### common


### template 
This is all the views are stored (html files)


### data 
this folder has all the ontologies files ( .owl or rdf) that are been stored in the system.

