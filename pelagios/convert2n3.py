from string import Template
import datetime
import csv
import sys

'''
Generate n3 files for uredb

'''

# dump of uredb
datafile = sys.argv[1]  #"data/ure_1_fabric.tsv"

# generated by named_entity_id.py 
placesFile = sys.argv[2] #"data/ure_pleiades_matches.csv"

# generated by media.py
mediaFile = sys.argv[3] # 'data/record_media.tsv'


preface = '''@prefix cnt: <http://www.w3.org/2011/content#> . 
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix pelagios: <http://pelagios.github.io/vocab/terms#> .
@prefix relations: <http://pelagios.github.io/vocab/relations#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema> .

<http:///http://uredb.reading.ac.uk/ure/n3/uredb.n3#agents/bcf> a foaf:Person ;
 foaf:name "Brian Fuchs" ;
 foaf:workplaceHomepage <http://mobilecollective.co.uk> ; 
.
'''

annotation = '''
<http://uredb.reading.ac.uk/ure/n3/uredb.n3#$accnum/annotations/$ann> a oa:Annotation ;
 oa:hasTarget <http://uredb.reading.ac.uk/ure/n3/uredb.n3#$accnum> ;
 oa:hasBody <http://pleiades.stoa.org/places/$placesid> ;
 pelagios:relation relations:foundAt ;
 oa:annotatedBy <http://uredb.reading.ac.uk/ure/n3/uredb.n3#agents/$agent> ;
 oa:annotatedAt "$date"^^xsd:date ;
.
'''
record = '''
<http://uredb.reading.ac.uk/ure/n3/uredb.n3#$accnum> a pelagios:AnnotatedThing ;
  dcterms:title "$title" ;
  dcterms:identifier <http://uredb.reading.ac.uk/record/$accnum> ;
  foaf:homepage <http://uredb.reading.ac.uk/cgi-bin/ure/uredb.cgi?rec=$accnum> ;
  dcterms:description "$description" ;
  $small
.
'''

image = 'foaf:depiction <$uri> ;'
thumb = 'foaf:thumbnail <$uri> ;'

caption = '''
<$uri> a foaf:Image ;
  dcterms:title "$cap" ;
  dcterms:license <http://creativecommons.org/licenses/by-sa/3.0/> ;
  $thumb
.
'''


def getPlaces(dataFile):
    out = {}
    with open(dataFile) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
              if (row['record'] in out):
                    out[row['record']].append(row)
                    
                    

              out[row['record']] = [row]
    return out


def getTsvFile(datafile):
      out = []
      with open(datafile,'rU') as tsv:
            i = 0;
            for line in csv.reader(tsv, delimiter="\t"):
                  if (i > 0 ):
                        out.append(line)
                  i = i + 1;
      return out



def getTSVDict(dataFile,key):
    out = {}
    with open(dataFile) as tsvfile:
        reader = csv.DictReader(tsvfile,delimiter="\t")
        for row in reader:

            out[row[key]]= row




    return out




uredata = getTsvFile(datafile);
places = getPlaces(placesFile)
media = getTSVDict(mediaFile,'id')

thisdate = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%SZ")


rec = Template(record)
ann = Template(annotation)
image_t = Template(image)
thumb_t = Template(thumb)
cap = Template(caption)

def fillInRecord(s,title,description,accnum,):
    return  s.safe_substitute(title=title, description=description,accnum=accnum)
print preface

for d in uredata: 
    accnum,title,description = "","",""
    accnum = d[0].replace(' ','%20')
    caps,ims = "",""
    
    if (accnum in media):
        m = media[accnum]
        small = image_t.safe_substitute(uri=m['small'])
        thumb = thumb_t.safe_substitute(uri=m['thumb'])
        caps = cap.safe_substitute(uri=m['small'],cap=m['cap'],thumb=thumb)
        ims = small

    if (len(d) > 1):
        title = d[1].replace('\n', ' ').replace('\r', '').replace('\\','')
    if (len(d) > 2):
        description = d[2].replace('\n', ' ').replace('\r', ' ').replace('\\"','').replace('\\','')


    if (accnum in places):
        print rec.safe_substitute(title=title, description=description,accnum=accnum,small=ims)

        i = 0
        for place in places[accnum]:
            i = i + 1
            
            print ann.safe_substitute(ann=i,accnum=accnum,placesid=place['guid'],agent="bcf",date=thisdate)
    

        if (accnum in media):
            print caps
