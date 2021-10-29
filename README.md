# Recommendation System: Recommend grocery items

## Structure of Project Folder

Python is used in this project. Mention below is structure of project
```
├── dataset
│   ├── Groceries_dataset.csv
├── aprioriMain.py
├── instaApriori.py
├── requirements.txt
├── README.md
```

## Prerequisites
Install following required tools
* Java
* Hadoop
* pip3 to install python dependencies

## Run project
```
python aprioriMain.py -r hadoop --k 3 --s 0.015 --c 0.4 --f frequent.txt ./Groceries_dataset.csv > output_k_3.txt
```
