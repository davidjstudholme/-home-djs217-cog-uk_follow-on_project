import sys
from datetime import datetime as dt
from datetime import datetime, timedelta


input_filename = 'data_from_chris/V2-ward-location.csv'
output_filename = 'data_from_chris_reformatted/V2-patient_stays.csv'
output_for_a2b_filename = 'data_from_chris_reformatted/V2-patient_stays_for_a2b.csv'
last_dates_filename = 'data_from_chris/last_infectious_date.csv'
staff_input_filename = 'data_from_chris/patientstaff_data_for_haplotype_network.csv'

message = ["Infile:",
           input_filename,
           '\nInfile for last infectious dates:',
           last_dates_filename,
           "\nOutfile:",
           output_filename,
           "\nOutfile for a2bcovid:",
           output_for_a2b_filename,
           '\n']
sys.stderr.write(" ".join(message))

### Define the objects
class Patient:
    pass
class Stay:
    pass
class Location:
    pass

patients = []

ward_to_siderooms = {}

### Read the last infectious date for each patient
with open(last_dates_filename) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0)

### Read the data lines for last infectious date
for readline in lines:
    headings = readline.split(',')
    coguk_id, positive_date_string, last_infectious_date_string, datediff = headings[0:5]

    ### Is this a new patient or are we continuing the previous one?
    patient = ''
    patient_is_new = True
    for this_patient in patients:
        if this_patient.coguk_id == coguk_id:
            patient_is_new = False
            patient = this_patient

    if patient_is_new:
        ### Create a new patient
        patient = Patient()
        patient.stays = []
        patient.covid_date_string = positive_date_string
        patient.coguk_id = coguk_id
        patients.append(patient)

    patient.last_infectious_date_string = last_infectious_date_string

### Read the data from Chris's spreadsheet
with open(input_filename) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0)

### Now read each line and populate the objects
sideroom_index = 1
home_index = 1

### Read the first line of data
readline = lines.pop(0)
headings1 = readline.split(',')
coguk_id1, admission_date_string1, covid_date_string1, date_string1, ward1, bay1, bed1 = headings1[0:7]

### Read each line of the data
for readline in lines:
    patient = '';
    headings2 = readline.split(',')    
    coguk_id2, admission_date_string2, covid_date_string2, date_string2, ward2, bay2, bed2 = headings2[0:7]
    
    ### If the COG-UK ID is left blank, then assume it is same as for previous row
    if coguk_id2 == '':
        coguk_id2 = coguk_id1
        
    ### Treat siderooms as if they were a separate ward
    if bay1 == "SR":
        sideroom_name_as_list = [ward1, 'SR', str(sideroom_index)]
        sideroom_name = '-'.join(sideroom_name_as_list)
        sideroom_index += 1
        if ward1 in ward_to_siderooms:
            pass
        else:
             ward_to_siderooms[ward1] = []

        ward_to_siderooms[ward1].append(sideroom_name)
        ward1 = sideroom_name

        
      ### Treat Home as if they were a separate ward                                                                                              
    elif ward1 == "Home":
        ward1_as_list = ['Home', str(home_index)]
        ward1 = '-'.join(ward1_as_list)
        home_index += 1

    ### Is this a new patient or are we continuing the previous one?
    patient_is_new = True
    for this_patient in patients:
        if this_patient.coguk_id == coguk_id1:
            patient_is_new = False
            patient = this_patient
        
    if patient_is_new:
        ### Create a new patient
        patient = Patient()
        patient.coguk_id = coguk_id1
        patient.covid_date_string = covid_date_string1
        patient.stays = []
        patient.last_infectious_date_string = ''
        patients.append(this_patient)
            
    ### Create and start populating the new stay
    stay = Stay()
    stay.start_date_string = date_string1
    stay.end_date_string = date_string2
    stay.ward = ward1
    stay.previous_ward = ward1
    patient.stays.append(stay)    
        
    if coguk_id1 == coguk_id2:
        ### Both rows correspond to the same patient
        stay.end_date_string = date_string2
    else:
        ### The first row is the final stay for this patient
        stay.end_date_string = patient.last_infectious_date_string 
        
    coguk_id1, admission_date_string1, covid_date_string1, date_string1, ward1, bay1, bed1 = [coguk_id2,
                                                                                              admission_date_string2,
                                                                                              covid_date_string2,
                                                                                              date_string2,
                                                                                              ward2,
                                                                                              bay2,
                                                                                              bed2]    

### Where two adjacent stays are in the same ward, merge them into one
not_finished_doing_merging = True
while not_finished_doing_merging:
    for patient in patients:
        not_finished_doing_merging = False
        for stay1 in patient.stays:
            for stay2 in patient.stays:
                if stay1 != stay2:
                    start_date1 = dt.strptime(stay1.start_date_string, "%d/%m/%Y")
                    end_date1 = dt.strptime(stay1.end_date_string, "%d/%m/%Y")
                    start_date2 = dt.strptime(stay2.start_date_string, "%d/%m/%Y")
                    end_date2 = dt.strptime(stay2.end_date_string, "%d/%m/%Y")

                    if start_date2 == end_date1 and stay1.ward == stay2.ward:
                        stay1.end_date_string = stay2.end_date_string
                        patient.stays.remove(stay2)
                        not_finished_doing_merging = True

### Read the staff data from Chris's spreadsheet                                                                                  
with open(staff_input_filename) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line                                                                                                       
header = lines.pop(0)

### Read each line of the data                                                                                                    
for readline in lines:
    readline = lines.pop(0)
    headings1 = readline.split(',')
    coguk_id, hcw, positive_date_string, ward, category = headings1[0:5]

    ### Is this a new patient (staff) or are we continuing the previous one?                                                             
    patient = ''
    patient_is_new = True
    for this_patient in patients:
        if this_patient.coguk_id == coguk_id:
            patient_is_new = False
            patient = this_patient

    if patient_is_new:

        patient = Patient()
        patient.stays = []
        patient.covid_date_string = positive_date_string
        patient.last_infectious_date_string = positive_date_string
        patient.coguk_id = coguk_id
        patients.append(patient)

        ### Consider the stay to have started 14 days before positive date                                                       
        positive_date = dt.strptime(positive_date_string, "%d/%m/%Y")
        start_date = positive_date - timedelta(days = 14)
        start_date_string = start_date.strftime("%d/%m/%Y")

        stay = Stay()
        stay.start_date_string = start_date_string
        stay.end_date_string = positive_date_string
        stay.ward = ward ### But we also need to consider all siderooms in this ward                                                      stay.previous_ward = ''
        patient.stays.append(stay)

        ### Also add a stay in each sideroom associated with this ward
        for sideroom in ward_to_siderooms[ward]:
            pass
        
        
    else:
        print('We have seen this staff member before; this should never happen')

### Print the data to file
header_line = ['COG-UK',
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
fh.write(",".join(header_line))
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
                         'Discharge', stay.end_date_string,
                         patient.last_infectious_date_string,
                         '\n']
            fh.write(",".join(data_line))
            
fh.close()
