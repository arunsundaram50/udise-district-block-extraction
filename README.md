# A utility to extract UDISE district &amp; block

## The input is obtained from one of these URLs
- <https://src.udiseplus.gov.in/home>
- <https://kys.udiseplus.gov.in/#/advance_search>

We chose the former.

## To install the program 
- Ensure you have python3 and pip installed in your machine
- Then download and setup the program like so:
```
git clone https://github.com/arunsundaram50/udise-district-block-extraction.git
cd udise-district-block-extraction
python3 -m venv venv_v1
source venv_v1/bin/activate
pip3 install -r requirements.txt
deactivate
```

## To run the program:
```
./main.py
```

# To segment the rows that are chosen to process you can start from a row and limit the number of rows like so:
```
./main.py -m 1000 -s 5000
```
This will start from row# 5000 and process up to 1000 rows. The output file name will be suffixed "_5000-6000.xlsx" in this case.

# To control the behavior of the program, you can pass additional arguments. To see the accepted arguments consult the help output like so:
```
./main.py -h
```
or read the program contents.

The output will be stored to `district_block_output.xlsx`.

To change the input, output, the number of rows/records that will be processed, etc., open `main.py` and change the values under the "setting up and fine-tuning the program" section as needed.
