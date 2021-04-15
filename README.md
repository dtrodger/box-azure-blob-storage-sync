## Box to Azure Blob Storage Pipeline  
### Runtime Requirements  
[Python 3.6+](https://www.python.org/downloads/)  
[PIP package manager](https://pip.pypa.io/en/stable/installing/)  
[virtualenv](https://virtualenv.pypa.io/en/latest/)  
### Set up and Run  
1. From the project root folder, create a Python 3.6+ virtual environment  
`$ virtualenv --python=python3 env`  
2. Activate the virtual environment  
`$ source env/bin/activate`  
3. Install the project dependencies  
`$ pip install -r requirements.txt`  
4. Copy the configuration from from  
`data/configuration/no_key_example.yml`  
to  
`data/configuration/dev.yml`  
5. Add the Box and Azure platform related attributes to the configuration file  
![config](data/docs/config.png)  
6. Run the command line interface menu to see the available commands  
`$ python src/cli/main.py`  
7. Run the seed-datetime-folders command to build a datetime chunked Box environment  
 `$ python src/cli/main.py seed-folders`  
8. Run the box-to-azure command to move files from an upload to chunked folder, then upload them to Azure Blob Storage  
`$ python src/cli/main.py box-to-azure`  
9. Build the development Docker environment
`$ make dev`  
10. Build the production Docker environment
`$ make prod`  