A Selenium-based web scraper that analyzes websites for health, nutrition, and related content categories. The scraper identifies the presence of specific keywords related to probiotics, fortification, gut health, women's health, cognitive health, and sports nutrition.

## Features
- Automated web scraping using Selenium and ChromeDriver
- Categorization of websites based on multiple health and nutrition categories
- Detection of business type (Manufacturer/Brand/Distributor)
- Detailed logging system
- CSV output for easy data analysis

## Prerequisites
- Python 3.7+
- Chrome browser
- ChromeDriver matching your Chrome version

## Installation
1. Clone the repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Download ChromeDriver and place it in the `drivers` folder

## Usage
1. Update the websites list in main.py
2. Run the script:
   ```bash
   python main.py
   ```
3. Results will be saved in 'website_data_analysis.csv'

## Output Format
The scraper generates a CSV file with the following columns:
- Website
- Relevant
- Category
- Manufacturer
- Brand
- Distributor
- Probiotics
- Fortification
- Gut Health
- Women's Health
- Cognitive Health
- Sports Nutrition
  So, A website will be stated Relevant to be identified as a prospect to UBL if any of these sections: Probiotics, Fortification, Gut Health, Women's Health, Cognitive Health and Sports Nutrition are True.
