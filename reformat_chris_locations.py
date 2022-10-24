import sys
from datetime import datetime as dt

input_filename = 'data_from_chris/V2-ward-location.csv'
output_filename = 'data_from_chris_reformatted/V2-patient_stays.csv'
output_for_a2b_filename = 'data_from_chris_reformatted/V2-patient_stays_for_a2b.csv'
last_dates_filename = 'data_from_chris/last_infectious_date.csv'

message = ["Infile:",
           input_filename,
           "\nOutfile:",
           output_filename,
           "\nOutfile for a2bcovid:",
           output_for_a2b_filename,
           '\n']
sys.stderr.write(" ".join(message))

### Read the data from Chris's spreadsheet
with open(input_filename) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
#sys.stderr.write(header)

### Define the objects

class Patient:
    pass

class Stay:
    pass

class Location:
    pass

### Now read each line and populate the objects
previous_coguk_id = ""
previous_ward = ""
sideroom_index = 1
patients = []
for readline in lines:
    headings = readline.split(',')
    coguk_id, admission_date_string, covid_date_string, move_date_string, new_ward, new_bay, new_bed = headings[0:7]
    
    if new_bay == "SR":
      new_ward_as_list = [new_ward, 'SR', str(sideroom_index)]
      new_ward = '-'.join(new_ward_as_list)
      sideroom_index += 1
      print(new_ward)
     
    ### If the COG-UK ID is left blank, then assume that it is the same as previous
    if coguk_id == "":
        coguk_id = previous_coguk_id
    
    ### Is this a new patient or are we continuing the previous one?
    patient_is_new = True
    this_patient = 0
    for patient in patients:
        if patient.coguk_id == coguk_id:
            patient_is_new = False
            this_patient = patient

        if patient_is_new:
            previous_ward = ""
            this_patient = Patient()
            this_patient.coguk_id = coguk_id
            this_patient.admission_date_string = admission_date_string
            this_patient.covid_date_string = covid_date_string
            this_patient.stays = []
            patients.append(this_patient)
        
            stay = Stay()
            stay.start_date_string = move_date_string
            stay.end_date = ""
            stay.ward = new_ward
            stay.previous_ward = previous_ward
            this_patient.stays.append(stay)
        else:

            ###  Continuing with same patient

            ### Is this stay on the same ward as the previous one? Or a different ward?
            ward_is_the_same_as_previous = False
            if new_ward == previous_ward:
                ward_is_the_same_as_previous = True

            ### First, finish populating the previous stay
            stay.end_date_string = move_date_string

            if ward_is_the_same_as_previous:

                ### Extend the previous stay
                pass
            
            else:
            
                ### Create and start populating the new stay
                stay = Stay()
                stay.start_date_string = move_date_string
                stay.end_date_string = ""
                stay.ward = new_ward
                stay.previous_ward = previous_ward
                this_patient.stays.append(stay)  

        previous_coguk_id = coguk_id
        previous_ward = new_ward
    
### Read the last infectious date for each patient so we can eliminate non-infectious periods
with open(last_dates_filename) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
#sys.stderr.write(header)   

for readline in lines:
    headings = readline.split(',')
    coguk_id, positive_date_string, last_infectious_date_string, datediff = headings[0:5]     
                 
    ### Find which patient we are dealing with
    not_found_this_patient = True
    for patient in patients:
        if patient.coguk_id == coguk_id:
            not_found_this_patient = False
            patient.last_infectious_date_string = last_infectious_date_string    
    if not_found_this_patient:
        sys.stderr.write('Failed to find patient with this COG-UK ID:')
        sys.stderr.write('\n')
        sys.stderr.write(coguk_id)
        sys.stderr.write('\n')
    
### Print the data to file
header_line = ['COG-UK',
               'Admission date',
               'SARS-Cov-2 date',
               'Last infectious date',
               'Start date',
               'End date',
               'Ward',
               '\n']
fh = open(output_filename, "w")
fh.write(", ".join(header_line))
for patient in patients:
    for stay in patient.stays:  
        
        ### If end date of the stay is missing then we can assume that it is the last infectious date
        if stay.end_date_string == '':
            stay.end_date_string = patient.last_infectious_date_string
            
        ### Convert strings to dates
        start_date = dt.strptime(stay.start_date_string, "%d/%m/%Y")
        end_date = dt.strptime(stay.end_date_string, "%d/%m/%Y")
        last_infectious_date = dt.strptime(patient.last_infectious_date_string, "%d/%m/%Y")
           
        if start_date > last_infectious_date:
            ### Ignore this stay because patient was not infectious
            pass
        else:                      
            data_line = [patient.coguk_id,
                         patient.admission_date_string,
                         patient.covid_date_string,
                         patient.last_infectious_date_string,
                         stay.start_date_string,
                         stay.end_date_string,
                         stay.ward,
                         '\n']
            fh.write(", ".join(data_line))
            
fh.close()


### Print the data to file formatted for a2bcovid
header_line = ['patient_study_id',
               'from_ward',
               'start_date',
               'to_ward',
               'end_date',
               'last_infectious_date',
               '\n']

fh = open(output_for_a2b_filename, "w")
fh.write(", ".join(header_line))
for patient in patients:
    for stay in patient.stays:  
        
        ### If end date of the stay is missing then we can assume that it is the last infecious date
        if stay.end_date_string == '':
            stay.end_date_string = patient.last_infectious_date_string
            
        ### Convert strings to dates
        start_date = dt.strptime(stay.start_date_string, "%d/%m/%Y")
        end_date = dt.strptime(stay.end_date_string, "%d/%m/%Y")
        last_infectious_date = dt.strptime(patient.last_infectious_date_string, "%d/%m/%Y")
           
        if start_date > last_infectious_date:
            ### Ignore this stay because patient was not infectious
            pass
        else:                      
            data_line = [patient.coguk_id,
                         stay.previous_ward,
                         stay.start_date_string,
                         stay.ward, stay.end_date_string,
                         patient.last_infectious_date_string,
                         '\n']
            fh.write(", ".join(data_line))
            
fh.close()
