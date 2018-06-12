import string

noDNA_starcode = 'noDNA-starcode.txt'
old_ss = 'SampleSheet.csv.Marc'
new_ss = 'SampleSheet.csv'

def reverse_complement(seq) :
    trans_table = string.maketrans('ATCG','TAGC')
    return seq.translate(trans_table)[::-1]

# extract indices from old Sample Sheet and reverse complement them
rev_indices = {}
with open(old_ss, 'r') as f :
    lineno = 0
    for line in f :
        lineno += 1
        if lineno > 2 and lineno < 14 :
            lane,sampleID,sampleName,index = line.strip('\n').split(',')
            rev_indices[reverse_complement(index)] = int(sampleID)

# pick the top N indices from the starcoded "noDNA" run
N = 100
new_indices = {}
with open(noDNA_starcode, 'r') as f :
    lineno = 0 
    for line in f :
        lineno += 1
        candidate,counts = line.strip('\n').split()
        if candidate in rev_indices.keys() :
            sampleID = rev_indices[candidate]
            new_indices[sampleID] = candidate
            print "Found candidate: candidate %s with %s counts"%(candidate,counts)
        if lineno == N : break

# get sorted sample ids
sampleIDs = new_indices.keys()
sampleIDs.sort()

# write new Sample Sheet
nlanes = 4
with open(new_ss, 'w') as f :
    f.write('[Data]\n')
    f.write('Lane,SampleID,SampleName,index,index2\n')
    for lane in range(1,nlanes+1) :
        for sampleID in sampleIDs :
            f.write('%d,%s,iPCR%s,%s\n'%(lane,sampleID,sampleID,new_indices[sampleID]))
