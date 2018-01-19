import os
LOC_BY_NAME = {"YEAR":0,
       "DAY": 1,
       "1":2,
       "2":3,
       "3":4,
       "4":5,
       "5":6,
       "6":7,
       "7":8,
       "8":9,
       "9":10,
       "10":11,
       "11":12,
       "12":13}

NAME_BY_LOC = {}
for key in LOC_BY_NAME:
    NAME_BY_LOC[LOC_BY_NAME[key]] = key

def parse_gage_line(line):
    """
    Takes in an unstructured line from a gage file that has rainfall data
    and parses it into an array where indexes are described above.
    """
    if "\n" in line:
        line = line.strip("\n")
    delimiters = [8, 22, 31, 42, 51, 61, 72, 80, 91, 102, 112, 122, 132]
    structured_array = []
    structured_array_nospaces = []
    
    for i in xrange(0,len(delimiters)):
        if i == 0:
            parsed_data = line[0:delimiters[0]]
        else:
            parsed_data = line[delimiters[i-1]:delimiters[i]]
        str_no_spaces = parsed_data.replace(" ","")   
        structured_array.append(str_no_spaces)
    #Add the last segment to the end of the array.
    parsed_data = line[delimiters[i]:]
    str_no_spaces = parsed_data.replace(" ","")   
    structured_array.append(str_no_spaces)
    return structured_array

def reformat_data(data, csv_filename):
    """
    Returns an array with the data restructured from [year, day, pt1, pt2 ..]
    into
    [[YEAR,MONTH, DAY pt1], [YEAR,MONTH, DAY, pt2] ...]
    We calculate the month by the data points position in the data.
    """
    YEAR = data[0]
    DAY = data[1]
    restructured_data = []
    for i in range(2,len(data)):
        if data[i] != '':
            new_data = [csv_filename, YEAR, NAME_BY_LOC[i], DAY, '0', '0', data[i]]
            restructured_data.append(new_data)
    return restructured_data
            

def parse_gage_path(gage_file_location, csv_filename):
    '''
    Takes file location, parses data in file into known format
    and returns it as an array of data. Strucutre of the array is
    [[YEAR,MONTH,DAY, DATA], [] ]
    '''
    gage_file = open(gage_file_location, 'r')
    rainfall_data = []
    for line in gage_file.readlines():
        #print 'line', line
        if line.startswith("19") or line.startswith("20"):
            structured_array = parse_gage_line(line)
            rainfall_data.append(structured_array)
    #for d in rainfall_data: print d
    restructured_rainfall_data = []
    for rainfall_line in rainfall_data:
        restructured_data = reformat_data(rainfall_line, csv_filename)
        restructured_rainfall_data+= restructured_data
    #for d in restructured_rainfall_data: print d
    return restructured_rainfall_data

def is_enough_data_years(data):
    '''
    Checks to see if each gage file contains more than 25 years of rainfall data years.
    '''
    data_years = set()
    for x in data:
        data_years.add(x[1])
    return len(data_years)>= 25

gage_folder_path = "C:\\Users\\xula\\Documents\\KSA_Floods\\06_Daily Rainfall\\94_Ayman_Gages"
PARSED_FOLDER_NAME = "restructured rainfall data"
output_folder = os.path.join(gage_folder_path,PARSED_FOLDER_NAME)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
    
gage_filenames = os.listdir(gage_folder_path)
filenames_w_insufficient_data = []
for gage_filename in gage_filenames:
    gage_file_location = os.path.join(gage_folder_path, gage_filename)
    if os.path.isdir(gage_file_location):
        continue
    csv_filename = gage_filename.strip(".TXT")
    rainfall_data = parse_gage_path(gage_file_location, csv_filename)
    if is_enough_data_years(rainfall_data):
        csv_header = "GAGE ID,YEAR,MONTH,DAY,HOUR,MIN,VALUE\n"
        csv_footer = "\n"
        csv_array = [",".join(data) for data in rainfall_data]
        csv_data_str = "\n".join(csv_array)
        CSV_DATA = csv_header+csv_data_str+csv_footer
        csv_filelocation = os.path.join(output_folder, "%s.csv" % csv_filename)
        new_file= open(csv_filelocation, "a")
        new_file.write(CSV_DATA)
        new_file.close()
    else:
        filenames_w_insufficient_data.append(gage_filename)
        
print "Filenames with insufficient data"
print filenames_w_insufficient_data
print "Done"


    
        
