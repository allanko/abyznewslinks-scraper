import requests, time
import pandas as pd
from bs4 import BeautifulSoup
import cache

# may take a while to run the first time
# caches every country page with a 1-second delay

BS_PARSER = "html.parser"
ROOTURL = u'http://www.abyznewslinks.com/'

def fetch_webpage_text(url, use_cache=True):
    if use_cache and cache.contains(url):
        return cache.get(url)
    # if cache miss, download it and sleep one second to prevent too-frequent calls
    content = requests.get(url).text
    cache.put(url,content)
    time.sleep(1)
    return content
 
def getcountries():
    # get dictionary of country links from 'http://www.abyznewslinks.com/allco.htm'
    world = BeautifulSoup(fetch_webpage_text(ROOTURL + 'allco.htm'), BS_PARSER)
    
    countrylinks = [[a.get('href')] for a in world.find_all('a')]
    countries = [a.string.strip() for a in world.find_all('a')]
    countrydict = dict(zip(countries[7:], countrylinks[7:])) # first 6 links are header links, not country pages
    
    # need to get all the subtrees, for countries that have regional subpages
    for country in countrydict.keys():
        print country
        suburl = ROOTURL + countrydict[country][0]
        countrysand = BeautifulSoup(fetch_webpage_text(suburl), BS_PARSER)
        tables = countrysand.find_all('table')
        
        # if tables[3] has "Media Type" as the first words, then this is a page with actual media listings
        # otherwise, it's a subdirectory of subregions of the country
        if tables[3].get_text().strip()[:10] != u'Media Type': 
            regions = []
            regionlinks = []
            # region listings are always in tables of three columns - get all three-column tables
            for table in tables:
                if len(table.findChildren('td'))==3:
                    regions += [a.get_text().strip() for a in table.find_all('a')] # get all the region names in the table
                    regionlinks += [[a.get('href')] for a in table.find_all('a')] # get all the corresponding links
                    break # only get the first table - note the USA subpage lists every state twice
                    
            regiondict = dict(zip(regions, regionlinks))                
            countrydict[country] += [regiondict] 
    
    return countrydict

def mediasources(country, url, subcountry=None):
    # get pandas dataframe of all media sources on a page
    sand = BeautifulSoup(fetch_webpage_text(url), BS_PARSER)
    tables = sand.find_all('table')
    
    datatables = []
    for table in tables:
        cells = table.findChildren('td', attrs={'nowrap': ''})
        if len(cells) == 6: # as a first-round filter, get only tables with 6 cells
            datatables += [table]
    
    # first table in datatables will be the site header - don't read that one
    region = []
    name = []
    link = []
    mediatype = []
    mediafocus = []
    language = []
    notes = []
    
    for d in datatables[1:]:
        cells = d.findChildren('td', attrs = {'nowrap':''})
        
        # get region, mediatype, mediafocus, and language columns      
        mediatype += cells[2].get_text()[2:-2].split('\n')
        mediafocus += cells[3].get_text()[2:-2].split('\n')
        language += cells[4].get_text()[2:-2].split('\n')
        
        # can't reliably split region name by \n -- need to split by <br> tags. see Gava-Gava, in Spain
        regionstring = str(cells[0])
        if regionstring.find('<br>') == -1:
            region += [cells[0].get_text().strip()] # only one entry
        else:
            region += [r.strip() for r in regionstring[regionstring[:regionstring.find('<br>')].rfind('>') + 1:regionstring.find('</br>')].split('<br>')]    
        
        # get all the site names and links, row by row, inserting empty strings if there is no <a> tag in that row
        name += [BeautifulSoup(i, BS_PARSER).find('a').get_text() if BeautifulSoup(i, BS_PARSER).find('a') else u'' for i in str(cells[1]).split('<br>')]
        link += [BeautifulSoup(i, BS_PARSER).find('a').get('href') if BeautifulSoup(i, BS_PARSER).find('a') else u'' for i in str(cells[1]).split('<br>')]
        
        # remove all rows for which "language" is empty - language entry is never two rows long
        remove = [i for i,r in enumerate(language) if r==''] 
        remove.reverse()
        
        # number of added elements
        added = len(cells[4].get_text()[2:-2].split('\n')) - len(remove)
        
        # dealing with Sierra Leone Broadcasting Corporation:
        # if len(region) < len(names), combine last two elements if you're not already removing it
        if len(cells[0].get_text()[2:-2].split('\n')) < len([a.get_text().replace('\n','') for a in cells[1].find_all('a')]):
            if len([a.get_text().replace('\n','') for a in cells[1].find_all('a')])-1 not in remove:
                name2 = name.pop(-1)
                name[-1] += ' '+name2
                del link[-1]
        
        for r in remove:
            del link[r]
            del mediatype[r]
            del mediafocus[r]
            del language[r]
            
            region2 = region.pop(r) # append popped region string to element before it
            region[r-1] += ' '+region2
            region[r-1] = region[r-1].strip() #strip trailing spaces
            
            name2 = name.pop(r) # append popped name string to element before it
            name[r-1] += ' '+name2
            name[r-1] = name[r-1].strip()
        
        # need to check if notes column is empty
        if len(cells[5].get_text().strip()) != 0: # if not empty
            notestring = str(cells[5]).replace('\n','')
            notestring = notestring[notestring.find('"2">')+4:] # remove prefix tags
            notestring = notestring[:notestring.find('</')] # remove trailing tags
            newnotes = [unicode(r) for r in notestring.split('<br>')] # split by <br> tags
            # this sometimes returns a list that's shorter than the others
            # because the notes column doesn't necessarily have an entry for every row
            # if so, add empty string entries to the end until it's the same length
            # also add extra buffer entries to account for the entries that will be removed in the next step
            newnotes += [unicode('')]*(added - len(newnotes) + len(remove))
            
            notes += newnotes
            for r in remove:
                notes2 = notes.pop(r) # append popped note strings to previous note entry
                notes[r-1] += ' '+notes2
                notes[r-1] = notes[r-1].strip() # strip trailing whitespace            
        else: # if empty, buffer with appropriate number of empty strings
            notes += [u'']*added
                    
        # safety check that all lists are still same length
        l = len(region)
        if not (len(name) == l and len(link) == l and len(mediatype) == l and len(mediafocus) == l and len(language) == l and len(notes) == l):
            print region, ' length: ', l
            print name, 'length:', len(name)
            print notes, 'length:', len(notes)
            print link, 'length:', len(link)
            raise ValueError("table columns are different lengths!")
    
    # clean newline characters
    region = [r.replace('\n','') for r in region]
    name = [n.replace('\n','') for n in name]
    notes = [n.replace('\n','') for n in notes]
    
    # put everything into dataframe
    alldatadict = {'region': pd.Series(region, index = name),
                   'link': pd.Series(link, index = name),
                   'media_type': pd.Series(mediatype, index = name),
                   'media_focus': pd.Series(mediafocus, index = name),
                   'language': pd.Series(language, index = name),
                   'notes': pd.Series(notes, index = name)}
                   
    alldata = pd.DataFrame(alldatadict)
    alldata.index.name = 'name'
    alldata['country'] = country
    alldata['subcountry'] = subcountry
    
    return alldata

# main

#countrydict = getcountries() 
#
#for country in countrydict.keys():
#    if len(countrydict[country]) == 1:
#        get = mediasources(country, ROOTURL + countrydict[country][0])
#    else:
#        subregions = countrydict[country][1]