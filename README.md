# Generating Website Layouts with Artificial Intelligence from Natural Language Input

This repository contains the code and application belonging to the above bachelor's thesis. The application can be used online without a local installation by visiting https://webgen-bot.netlify.app/.

## Contents of this repository

```Bash
├── .env
├── .gitignore
├── chatbot-requirements.txt        # for chatbot execution
├── requirements.txt                # for development
├── README.md
├── data
│   ├── chatbot                     # files for chatbot execution
│   ├── generated                   # pre-generated images for chatbot execution
│   ├── labels                      # image labels
│   ├── ratings                     # user ratings
│   ├── sql-queries                 # sql queries
│   └── study                       # questionnaire and results of study
├── logs
├── src
│   ├── __init__.py
│   ├── __main__.py                 # main module for development scripts
│   ├── chatbot                     # chatbot code
│   ├── client                      # client
│   ├── clustering                  # scripts to run k-means clustering
│   ├── crawling                    # web crawler
│   ├── database                    # database interface
│   ├── dataset                     # dataset creations cripts
│   ├── dcgan                       # DCGAN training scripts
│   ├── logging_config.py
│   ├── schemas                     # data schemas
│   ├── scraping                    # website scraper
│   ├── scripts                     # scripts for VM usage
│   └── util                        # utility
└── tests                           # test for database interface/schemas


```

---

## Prerequisites

To run the application locally on Windows, install the following software. Other version may work, but were not tested.

```
Python 64-bit, 3.7.10 or 3.8.3
pip 21.2
Node.js v14.16.0
npm 6.14.8
```

## Setting up the environment

Create a virtual environment for the chatbot and install the necessary Python packages:

```Bash
# from the root directory
virtualenv venv
venv\Scripts\activate

# install packages in venv
pip install -r chatbot-requirements.txt
```

Download the spaCy language model `en_core_web_lg`.

```Bash
python -m spacy download en_core_web_lg
```

Install the necessary npm packages for the client.

```Bash
# install npm packages
cd src\client
npm install
```

Lastly, open the `.env`-file in the root directory to edit the environment variables. The `DATA_PATH` shall point to the data directory and the `LOGS_PATH` to the directory, in which the logs will be stored.

```Bash
# Paths
DATA_PATH='set path to data directory'
LOGS_PATH='set path to logs directory'
```

## Running the application

Start the chatbot application in the activated virtual environment.

```Bash
# from root dir with venv activated
python src\chatbot\server.py
```

Then, start the client application.

```Bash
cd src\client
npm start
```

Open `http://localhost:3000/` in your browser to use the chatbot.

## Running a Python development script

The scripts in this section were used for development and are not necessary for running the application, but are included for documentation. Note that they may not work due to missing data resources or and SQL database, which are not included because of their large size.

From the root directory, run

```Bash
python -m src {script name}
```

to execute a development script. The following scripts are implemented:

```Bash
# web scraping and crawling
init_crawler
run_crawler
init_downloader
run_downloader

# dataset
rm_truncated
init_creator
run_creator
create_dataset_json

# database
init_db
create_db_backup
format_labels_csv

# clustering
kmeans
test_pca_components
run_matcher
run_evaluation
```

Check out the code comments for detailed explanations.

### Running unit tests

Note that the tests require a set up SQL database. From the root directory, run

```PowerShell
python -m unittest -v test.{filename without extension}
```

to execute a test file from the `\tests` folder.
