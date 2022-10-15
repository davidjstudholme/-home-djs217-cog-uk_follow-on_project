import sys
import re
from datetime import datetime as dt

### Read the COG-UK metadata spreadsheet
with open('cog_metadata.exet.with-header.csv') as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
sys.stderr.write(header)

class Patient:
    pass

class Stay:
    pass

patients = []

for readline in lines:
    headings = readline.split(',')
    sequence_name, country, adm1, is_pillar_2, sample_date, epi_week, lineage, lineages_version, lineage_conflict, lineage_ambiguity_score, scorpio_call, scorpio_support, scorpio_conflict, del_1605_3, ambiguities, n501y, a222v, n439k, e484k, q27stop, p323l, t1001i, mutations, y453f, p681h, del_21765_6, d614g = headings
    
    ### Remove prefix and suffix from COG-UK ID
    p = re.compile('EXET-[\w\d]{6}')
    m = p.search(sequence_name)
    if m:
        coguk_id = m.group()
    
       ### Create a new Patient object and add it to the list of all Patient objects
        patient = Patient()
        patients.append(patient)
    
        ### Populate attributes of this Patient object
        patient.sequence_name = coguk_id
        patient.country = country 
        patient.adm1 = adm1
        patient.is_pillar_2 = is_pillar_2 
        patient.sample_date = sample_date
        patient.epi_week = epi_week
        patient.lineage = lineage
        patient.lineages_version = lineages_version 
        patient.lineage_conflict = lineage_conflict
        patient.lineage_ambiguity_score = lineage_ambiguity_score
        patient.scorpio_call = scorpio_call
        patient.scorpio_support = scorpio_support
        patient.scorpio_conflict = scorpio_conflict
        patient.del_1605_3 = del_1605_3
        patient.ambiguities = ambiguities
        patient.n501y = n501y
        patient.a222v = a222v
        patient.n439k = n439k
        patient.e484k = e484k
        patient.q27stop = q27stop
        patient.p323l = p323l
        patient.t1001i = t1001i
        patient.mutations = mutations
        patient.y453f = y453f
        patient.p681h = p681h
        patient.del_21765_6 = del_21765_6
        patient.d614g = d614g
        patient.stays = []

### Read the patient stays spreadsheet
with open('V2-patient_stays.csv') as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
sys.stderr.write(header)
 
    
for readline in lines:
    headings = readline.split(',')
       
    coguk_id, admission_date, covid_date, last_infectious_date, start_date, end_date, ward, bay, bed = headings[0:9]

    stay = Stay()
    
    ### Get the appropriate patient
    for patient in patients:
        if patient.sequence_name == coguk_id:
            patient.admission_date = admission_date
            patient.covid_date = covid_date
            stay.start_date = start_date
            stay.end_date = end_date
            stay.ward = ward
            stay.bay = bay
            stay.bed = bed
            patient.stays.append(stay)
    
    
    
### Convert strings to dates
#start_date = dt.strptime(stay.start_date_string, "%d/%m/%Y")
#end_date = dt.strptime(stay.end_date_string, "%d/%m/%Y")
#last_infectious_date = dt.strptime(patient.last_infectious_date_string, "%d/%m/%Y")    
    
    
### Now that we have populated the Patient objects with attributes and lists of Stay objects, we can analyse overlapping stays
for patient1 in patients:
    for patient2 in patients:
            if patient1.sequence_name < patient2.sequence_name:
                for stay1 in patient1.stays:
                    for stay2 in patient2.stays:
                        #print(patient1.sequence_name, " versus ", patient2.sequence_name)
                        if stay1.ward == stay2.ward and stay1.ward != "":
                            #print(patient1.sequence_name, " shared ward ", stay1.ward, " with ", patient2.sequence_name)
                            overlap = False 
                            if stay1.start_date >= stay2.start_date and stay1.start_date <= stay2.end_date:
                                overlap = True
                            elif stay1.end_date >= stay2.start_date and stay1.end_date <= stay2.end_date:
                                 overlap = True
                            if overlap:
                                print(patient1.sequence_name, patient1.lineage, stay1.start_date, "-", stay1.end_date, " shared ward ", stay1.ward, " with ", patient2.sequence_name, patient2.lineage, stay2.start_date, "-", stay2.end_date)
                