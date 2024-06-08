# udise-district-block-extraction
Extract UDISE district &amp; block

## The input is obtained from one of these URLs
- <https://src.udiseplus.gov.in/home;jsessionid=722157EB55AD128D08F78BA866301DC0>
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
./main.py
```

The output will be stored at `district_block_output.xlsx`.

To change the input, output, etc. open `main.py` and change the values under the "setting up and fine-tuning the program" section as needed.
