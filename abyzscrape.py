# -*- coding: utf-8 -*- 

import requests, time, sys
import pandas as pd
from bs4 import BeautifulSoup
import cache

# may take a while to run the first time
# caches every country page with a 1-second delay
sys.setrecursionlimit(1500) # so many <br> tags. oceans of <br>. html.parser hates <br>.
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
    
    print country, subcountry

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
        
        # can't split reliably by '\n' -- see Gava-Gava in Spain, or the Minnesota table.
        # see Gava-Gava, in Spain
        # get mediatype, mediafocus, language, region columns
        typestring = str(cells[2])
        if typestring.find('<br>') == -1:
            mediatype += [cells[2].get_text().strip()] # only one entry
        else:
            mediatype += [r.strip() for r in typestring[typestring[:typestring.find('<br>')].rfind('>') + 1:typestring.find('</br>')].split('<br>')]
        
        focusstring = str(cells[3])
        if focusstring.find('<br>') == -1:
            mediafocus += [cells[3].get_text().strip()] # only one entry
        else:
            mediafocus += [r.strip() for r in focusstring[focusstring[:focusstring.find('<br>')].rfind('>') + 1:focusstring.find('</br>')].split('<br>')]
                
        languagestring = str(cells[4])
        if languagestring.find('<br>') == -1:
            language += [cells[4].get_text().strip()] # only one entry
        else:
            language += [r.strip() for r in languagestring[languagestring[:languagestring.find('<br>')].rfind('>') + 1:languagestring.find('</br>')].split('<br>')]
        
        regionstring = str(cells[0])
        if regionstring.find('<br>') == -1:
            region += [cells[0].get_text().strip()] # only one entry
        else:
            region += [r.strip() for r in regionstring[regionstring[:regionstring.find('<br>')].rfind('>') + 1:regionstring.find('</br>')].split('<br>')]    
        
        # get all the site names and links, row by row, inserting empty strings if there is no <a> tag in that row
        newentries = str(cells[1]).split('br>') # sometimes there's a typo where </br> is used instead of <br> - looking at you, El Zonda in Argentina
        if '</' in newentries:
            newentries = newentries[:newentries.index('</')] # exclude all the closing tags at the end
        elif '</font>\n</td>' in newentries:
            newentries = newentries[:newentries.index('</font>\n</td>')]
        
        name += [BeautifulSoup(i, BS_PARSER).find('a').get_text() if BeautifulSoup(i, BS_PARSER).find('a') else u'' for i in newentries]
        link += [BeautifulSoup(i, BS_PARSER).find('a').get('href') if BeautifulSoup(i, BS_PARSER).find('a') else u'' for i in newentries]
        
        # need to check if notes column is empty
        # if empty, will be fixed in the "normalize column lengths" block below
        if len(cells[5].get_text().strip()) != 0: 
            notestring = str(cells[5]).replace('\n','')
            notestring = notestring[notestring.find('"2">')+4:] # remove prefix tags
            notestring = notestring[:notestring.find('</')] # remove trailing tags
            notes += [r for r in notestring.split('<br>')] # split by <br> tags
            # this sometimes returns a list that's shorter than the others
            # because the notes column doesn't necessarily have an entry for every row
            # we'll fix this in the "normalize column lengths" block below
        
        # normalize column lengths
        # consider Yahoo, in Canada/National
        # or Clara Mente, in Argentina/Buenos Aires
        # or Sierra Leone Broadcasting Corporation, in Sierra Leone
        minlength = min(len(language), len(name), len(region), len(notes))
        maxlength = max(len(language), len(name), len(region), len(notes))
        if minlength != maxlength:
            if maxlength - len(language) == 1:
                language += ['']
                mediatype += ['']
                mediafocus += ['']
            if maxlength - len(name) == 1:
                name += ['']
                link += ['']
            if maxlength - len(region) == 1:
                region += ['']
            if maxlength - len(notes) > 0:
                notes += ['']*(maxlength-len(notes))

        # remove all rows for which "language" is empty - language entry is never two rows long
        remove = [i for i,r in enumerate(language) if r==''] 
        remove.reverse()
        
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
            
            notes2 = notes.pop(r) # append popped note strings to previous note entry
            notes[r-1] += ' '+notes2
            notes[r-1] = notes[r-1].strip() # strip trailing whitespace   
                    
        # safety check that all lists are still same length
        l = len(language)
        if not (len(name) == l and len(link) == l and len(mediatype) == l and len(mediafocus) == l and len(region) == l and len(notes) == l):
            print language, ' length: ', l
            print region, ' length: ', len(language)
            print name, 'length:', len(name)
            print notes, 'length:', len(notes)
            print link, 'length:', len(link)
            print mediatype, 'length:', len(mediatype)
            print mediafocus, 'length:', len(mediafocus)
            raise ValueError("table columns are different lengths!")
    
    # clean newline characters
    region = [r.replace('\n','') for r in region]
    name = [n.replace('\n','') for n in name]
    notes = [n.replace('\n','') for n in notes]
    
    # put everything into dataframe
    alldatadict = {'link': pd.Series(link, index = name),
                   'media_type': pd.Series(mediatype, index = name),
                   'media_focus': pd.Series(mediafocus, index = name),
                   'language': pd.Series(language, index = name),
                   'notes': pd.Series(notes, index = name),
                   'region': pd.Series(region, index = name)}
                   
    alldata = pd.DataFrame(alldatadict)
    alldata.index.name = 'name'
    alldata['subcountry'] = subcountry
    alldata['country'] = country
    
    print 'DONE'
    return alldata

#if __name__ == "__main__":
#    countrydict = getcountries() 
#    
#    allframes = []
#    for country, sub in countrydict.iteritems():
#        if len(sub) == 1:
#            allframes += [mediasources(country, ROOTURL + sub[0])]
#        else:
#            for region, url in sub[1].iteritems():
#                allframes += [mediasources(country, ROOTURL + url[0], subcountry=region)]
#    
#    allmedia = pd.concat(allframes)