# Generating Website Layouts with Artificial Intelligence from Natural Language Input

This project focuses on the website generation task using AI methods based on a description in natural language. Multiple **Generative Adversarial Networks (GANs)** trained on self-created, class conditional dataset generate preview images of websites that match a textual description, which a user communicates to a **self-developed chatbot**. The application is available at https://webgen-bot.netlify.app/.  


Below are samples of generated websites.  

![generated-websites-samples](https://user-images.githubusercontent.com/49451811/140747316-ef217c24-d4d0-4d65-aaf2-90fd9de5d8af.jpg)


## Abstract
*The demand for websites has increased in recent years and designing websites is more accessible than ever, also for people with little technical knowledge. To enhance the design process for such people and web designers in general, this thesis proposes a novel approach for website design generation from natural language input. The designs are generated as images by a set of Generative Adversarial Networks (GANs) trained using transfer learning methods on a self-created, class-conditional dataset of website screenshots. A chatbot serves as a human-computer interface and displays the best-matching generated website image to the user's input. To validate the concept, a user study with six participants was conducted, comparing the chatbot using generated website images to an alternative version using images of real websites from the training data. The evaluation results suggest the viability of this approach. However, especially in the sharpness and clarity of the generated website images, there is room for improvements. Further research on this topic is needed to fully exploit the potential of this approach.*


## Contents of this repository
This repository contains the code and application belonging to the above bachelor's thesis. The application can be used online without a local installation by visiting https://webgen-bot.netlify.app/.

```Bash
├── .env
├── .gitignore
├── chatbot-requirements.txt        # for chatbot execution
├── requirements.txt                # for development
├── README.md
├── data
│   └── labels                      # image labels
├── logs
├── src
│   ├── __init__.py
│   ├── __main__.py                 # main module for development scripts
│   ├── chatbot                     # chatbot code
│   ├── client                      # client UI
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
