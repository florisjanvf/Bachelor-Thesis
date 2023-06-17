# Bachelor-Thesis

This repository contains all the code for my bachelor thesis research project titled "Investigating Home Advantage in English Professional Football on an Individual Player Basis." The research focuses on analyzing home advantage in the English Premier League (EPL) and examines its relationship with various player-specific factors.

## Language and Libraries

All the code in this research project was written in Python. The Python programming language offers a wide range of tools and libraries for data analysis and statistical modeling, making it suitable for this investigation.

## Data Collection

To gather the necessary data for the research, web scraping techniques were employed. The following libraries were used for web scraping:

- BeautifulSoup4: A Python library for parsing HTML and XML documents, which facilitated data extraction from websites.
- Selenium: A web testing framework that allowed for automated interaction with websites.
- TOR: The Onion Router, a network protocol used to anonymize internet traffic, ensuring privacy during web scraping activities.

More detailed information about the libraries used in this project can be found in the `requirements.txt` file. This file can also be utilized to install all the required libraries and dependencies necessary to replicate the research.

## Repository Structure

The repository is organized into the following directories:

- **data**: Contains all the data used in this research paper. The data was obtained through web scraping from the following sources: [WhoScored](https://www.whoscored.com/), [FUTBIN](https://www.futbin.com/), [Worldfootball.net](https://www.worldfootball.net/), and [Wikipedia](https://www.wikipedia.org/).
- **results**: Includes various figures, tables, and visualizations produced during the analysis conducted in the `code` directory.
- **code**: Consists of several Python files and a Jupyter notebook called `main.ipynb`. The Python files contain all the scripts utilized for web scraping, while the notebook contains the code used for investigating home advantage in the EPL.
- **archive**: Contains a replication of the paper authored by Peeters and Van Ours (2021). Please note that the original files of their paper are not included in this repository to respect intellectual property rights.

Additionally, the `main.html` file is provided as an alternative to the `main.ipynb` file. It allows for easier viewing if the user is unable to open `.ipynb` files.

## Research Findings

The research findings highlight the significance of home advantage on an individual player basis. A model was constructed using linear regression and the random forest regression machine learning method to investigate the drivers of home advantage.

The results demonstrated the following relationships with home advantage per player:

- Average home attendance, player quality, and skill moves were positively associated with home advantage.
- Player age and playing as a goalkeeper or defender, exhibited negative correlations with home advantage.

Lastly, the research indicates a decrease in home advantage over the seasons.

For more detailed insights and analysis, please refer to the bachelor thesis research paper.
