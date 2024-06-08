# udise-district-block-extraction
Extract UDISE district &amp; block

## The input is obtained from one of these URLs
- <https://src.udiseplus.gov.in/home>
- <https://kys.udiseplus.gov.in/#/advance_search>

## To install the program 
- First you should have python3 and pip installed in your machine
- Then download and setup the program
```
git clone https://github.com/arunsundaram50/udise-district-block-extraction.git
cd udise-district-block-extraction
python3 -m venv venv_v1
source venv_v1/bin/activate
pip3 install -r requirements.txt
```

## To run the program
```
source venv_v1/bin/activate
./main.py
```

The output will be stored to `district_block_output.xlsx`.

To change the input, output, the number of rows/records that will be processed, etc., open `main.py` and change the values under the "setting up and fine-tuning the program" section as needed.
