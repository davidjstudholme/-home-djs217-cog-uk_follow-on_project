import sys
import re
from datetime import datetime as dt
from Bio import SeqIO

### Read COG-UK metadata
with open('cog_metadata.exet.with-header.csv') as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
sys.stderr.write(header)

in_scope_ids = []

for readline in lines:
    headings = readline.split(',')
    sequence_name, country, adm1, is_pillar_2, sample_date, epi_week, lineage, lineages_version, lineage_conflict, lineage_ambiguity_score, scorpio_call, scorpio_support, scorpio_conflict, del_1605_3, ambiguities, n501y, a222v, n439k, e484k, q27stop, p323l, t1001i, mutations, y453f, p681h, del_21765_6, d614g = headings
    
    ### Remove prefix and suffix from COG-UK ID
    p = re.compile('EXET-[\w\d]{6}')
    m = p.search(sequence_name)
    if m:
        coguk_id = m.group()
    
    range_start = dt.strptime("01/10/20", "%d/%m/%y")
    range_end = dt.strptime("28/02/21", "%d/%m/%y")
    sample_date_as_datetime = dt.strptime(sample_date, "%Y-%m-%d")
    
    if sample_date_as_datetime >= range_start and sample_date_as_datetime <= range_end:
        in_scope_ids.append(sequence_name)

for record in SeqIO.parse("cog_alignment.exet.fasta", "fasta"):
    exist_count = in_scope_ids.count(record.id)
    if exist_count > 0:
        print('>', record.id, '\n', record.seq, sep='')