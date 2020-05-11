# datasheet-scraper
A tool that scrapes pin attributes from datasheets and converts them to the PinSpec format.

## Dependencies
numpy
tabula-py
pandas

##scraper.py

###Usage

```bash
python3 scraper.py [component name]
```

Supported Components:
  `adm7150`
  `cc2640_rgz`
  `cc2640_rhb`
  `cc2640_rsm`
  `stm32l433_lqfp48`
  `stm32l433_ufbga100`

The tool will print the PinSpec to the command line and write it to a file `pins.txt`.

###Adding component support
Adding support for a new component involves usage of the scrape function in `scraper.py`. 
To add support for a new component, add the following code to `scraper.py` in the section marked `SUPPORTED COMPONENTS` and change the inputs to the scrape function. 


```python
if args.Component == 'pkgName':
  pkg = scrape(pkgName, pkgSize, fName, pgs, strm, lttc, gss, a, numCol, 
           nameCol, tableNums):
```

###Scrape function
The scrape function scrapes a datasheet for the name and number of pins associated with a package.

####pkgName
The name of the desired package.

####pkgSize
Number of pins in the desired package.

####fName
Path to datasheet file.

####pgs
Pages where pin description tables are located.

####strm 
[True, False, None]
Enable stream mode when the rows or columns in the tables are not seperated by lines.

####lttc
[True, False, None]
Enable lattice mode when the rows or columns in the tables are seperated by lines.

####gss
[True, False, None]
Enabling guess mode lets the tool determine the area on the page where the table is located.

####a
[y1, x1, y2, x2] or None 
y1 = top of table
x1 = left of table
y2 = top + height of table
x2 = left + width of table
The tool accepts the coordinates (in *point measurements*, not *pixels*) of the table you want to extract. (Alternatively, it can auto-detect tables, but if you're dealing with thousands of pages with identical regions, it's better to be explicit.)

You can either use the "full" Tabula app to get these coordinates, or manually measure using the Preview app in Mac OS X.

#####Use the Tabula app to grab table coordinates

1. Download Tabula from http://tabula.technology/.
2. Open Tabula and upload your PDF into the web page that appears.
3. Select your table area(s) as usual and proceed to the "Preview & Export Extracted Data" step.
4. Under **Export Format**, select "Script" instead of CSV, and then click "Export" to download the generated code. Save this file somewhere you can find it.
5. Open the script you downloaded in a code editor.
  * The generated script contains measurements already filled in, based on what you selected in the Tabula app. The measurements are in the order y1, x1, y2, x2. You can use this as a starting point to process many of the same type of document, for example if you have a monthly report that is generated as separate PDFs for each month, and the table you want is located in the exact same place each time.

#####Use **Preview**  to grab table coordinates (OS X only)

1. Open your PDF file in the Preview app
2. Make sure `Tools > Rectangular selection` is checked.
3. Open the inspector by going to `Tools > Show inspector`.
4. Go to the "crop inspector" tab ? second from the right, it looks like a ruler
5. Change "Units" to Points
6. Select the area you want on the page.

Note the `left`, `top`, `height`, and `width` parameters and calculate the following:

* `y1` = `top`
* `x1` = `left`
* `y2` = `top + height`
* `x2` =  `left + width`

####numCol
The column number of the column containing pin numbers.

####nameCol
The column number of the column containing pin names.

####tableNums
A list of table numbers that contain relevant pin data.

##helper.py
Due to the heterogeneous nature of datasheets, helper.py is built to assist with determining the correct inputs for `pgs`, `strm`, `lttc`, `gss`, `a`, and `tableNums`.  

###Usage

```bash
python3 helper.py [FILE] [PAGES] [STREAM] [LATTICE] [GUESS] [AREA] 
```

This helper function will display raw data from the datasheet organized into a list of tables. This function is used to test which inputs for [PAGES], [STREAM], [LATTICE], [GUESS], and [AREA] return the most amounts of valuable data. Often, the helper function will return some tables with completely irrelevent information. This tool allows you easily identify the tables which contain relevant data and input them to the `tableNums` list input for `scrape`.

####[FILE]
Path to datasheet file.

####[PAGES]
Pages where pin description tables are located.

####[GUESS]
Enable guess mode where tool automatically determines table coordinates.

####[AREA]
Table coordinates. 
Input y1,x1,y2,x2 with no spaces, or `None`. 
i.e. `271.9575,32.5125,447.1425,133.4925`
