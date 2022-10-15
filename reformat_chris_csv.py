import sys
#from operator import attrgetter

### Read the data from Chris's spreadhseet
with open('ward-location.csv') as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
sys.stderr.write(header)

### Define the objects

class Patient:
    pass

class Stay:
    pass

class Location:
    pass

### Now read each line and populate the objects
patients = []
for readline in lines:
    lines = readline.split(',')
    coguk_id, admission_date, covid_date, new_move_date, new_ward, new_bay, new_bed = lines[0:7]
    
    ### If the COG-UK ID is left blank, then assume that it is the same as previous
    if coguk_id == "":
        coguk_id = previous_coguk_id
    
    ### Is this a new patient or are we continuing the previous one?
    patient_is_new = 1
    this_patient = 0
    for patient in patients:
        if patient.coguk_id == coguk_id:
            patient_is_new = 0
            this_patient = patient
                
    if patient_is_new == 1:
        this_patient = Patient()
        this_patient.coguk_id = coguk_id
        this_patient.admission_date = admission_date
        this_patient.covid_date = covid_date
        this_patient.stays = []
        patients.append(this_patient)
        
        stay = Stay()
        stay.start_date = admission_date
        stay.end_date = new_move_date
        stay.ward = new_ward
        stay.bay = new_bay
        stay.bed = new_bed  
        this_patient.stays.append(stay)
              
    else:
        #print("We already saw this patient: ",coguk_id)
        stay = Stay()
        stay.start_date = previous_move_date
        stay.end_date = new_move_date
        stay.ward = new_ward
        stay.bay = new_bay
        stay.bed = new_bed
        this_patient.stays.append(stay)
 
    previous_move_date = new_move_date
    previous_coguk_id = coguk_id
    

print('COG-UK', 'Admission date', 'SARS-Cov-2 date', 'Start date', 'End date', 'Ward', 'Bay', 'Bed', sep=',')
for patient in patients:
    for stay in patient.stays:
        print(patient.coguk_id, patient.admission_date, patient.covid_date, stay.start_date, stay.end_date, stay.ward, stay.bay, stay.bed, sep=',')
    
