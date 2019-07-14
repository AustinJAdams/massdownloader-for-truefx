# massdownloader-for-truefx
TrueFX, a foreign exchange data provider, allows you to only download currency pair during one month at a time. This script does the work for you and downloads their CSVs

If you are interested in learning FX markets, this allows you to mass-download all the data from 2007 to present.

Download the script and 
'''
python fx_download.py -u "Your TrueFX Username" -p "Your TrueFX Password
'''
Make sure you have a subdirectory in your working directory called "data" as the script will look for it. This data is extremely large, so make sure you are prepared for it.

## TODO
Add more functionality with custom paths, currency pairs, years, months, and ability to not-unzip.
