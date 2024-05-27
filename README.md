# Coding assignment - Xu Zhan

This is the coding assignment repository of `Xu Zhan` regarding the recruitment process for the Senior Data Engineer role with Revenue NSW (req32647).

The output data can either be saved in `JSON` format or outputed to `MongoDB in Docker environments`.

## Requirements

python==3.8
numpy==1.24.2
pandas==1.4.2
pymongo==4.6.3

## Installation

Save the whole repository locally, and cd to the local repository.

## Instructions

#### 1. Save the data in JSON format:

1.1 Make sure you are in the local repository.

1.2 Make sure you are in a environment satisfy the requirements above. If no, install python==3.8 first, then run `pip install -r requirements` in your terminal.

1.3 Open `main.py` and set `OUTPUT_JSON` in line 14 to `True` .

1.4 In your terminal, run `python main.py`

1.5 You should see a JSON file named `member-data.json` in the working directory.



#### 2. Output the data to MongoDB

2.1 Make sure you are in the local repository.

2.2 In your terminal, run `docker build -t mongo-app:v1 .`

2.3 Then run `docker-compose up -d`

2.4 (Optional), if you desire to check the running logs, please use command `docker logs -f CONTAINER_ID`. Note that you need to replace the CONTAINER_ID` with your own one.

2.5 You should see a file in MongoDB under `member_data.members`, i.e. the data was saved to collection `members` under the database `member_data`. You can specify your own database name and collection name by editing the code in line 16 & 17 in `main.py`





