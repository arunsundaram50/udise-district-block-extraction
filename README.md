# A utility to extract UDISE district &amp; block

## The input is obtained from one of these URLs
- <https://src.udiseplus.gov.in/home>
- <https://kys.udiseplus.gov.in/#/advance_search>

We chose the former.

## Installing the program 
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

## Running the program

To process everything
```
./main.py
```

Instead of processing everything, you can choose to process certain segment of the input file i.e: you can choose the rows that the program will process. The starting row and the number of rows to process from the starting row can be controlled like so:
```
./main.py -m 1000 -s 5000
```
In this case the program will:
- start from row# 5000 and process up to 1000 rows
- the output file name will be suffixed "_5000-6000.xlsx"

Instead of running `./main.py` which will process all inputs sequentically, segmenting allows parallel execution by running mulitple instances of `/main.py` with approproate arguments. For example, you can divide the inputs into 10 segments which will help complete the conversion of the entire input set by 10 times. What limits the parallel execution is the amount of local resources avaliable (i.e. where the program is running) and the server limit, if any.

To control other behaviors of the program, you can pass additional arguments. To see the accepted arguments consult the help output like so:
```
./main.py -h
```
or read the program contents.

### Note:
- The output will be stored to `district_block_output_{START}-{START+MAX}.xlsx`, where START is the --start (-s) and MAX is --max (-m) specified or defaulted.
- To change the input, output, the number of rows/records that will be processed, etc., open `main.py` and change the values under the "setting up and fine-tuning the program" section as needed.
