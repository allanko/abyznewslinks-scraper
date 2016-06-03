import requests, sys, logging, json, csv, collections, time
import pandas as pd
from bs4 import BeautifulSoup
import cache

BS_PARSER = "html.parser"

def fetch_webpage_text(url,use_cache=True):
    if use_cache and cache.contains(url):
        return cache.get(url)
    # cache miss, download it and sleep one second to prevent too-frequent calls
    content = requests.get(url).text
    cache.put(url,content)
    time.sleep(1)
    return content
 
def getcountries():
    # get dictionary of country links from 'http://www.abyznewslinks.com/allco.htm'
    world = BeautifulSoup(fetch_webpage_text('http://www.abyznewslinks.com/allco.htm'), BS_PARSER)
    
    countrylinks = [a.get('href') for a in world.find_all('a')]
    countries = [a.string for a in world.find_all('a')]
    countrydict = dict(zip(countries[7:], countrylinks[7:])) # first 6 links are header links, not country pages
    return countrydict 

def mediasources(country, url):
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
        
        region += cells[0].get_text()[2:-2].split('\n')        
        name += [a.get_text().replace('\n','') for a in cells[1].find_all('a')]
        link += [a.get('href') for a in cells[1].find_all('a')]
        mediatype += cells[2].get_text()[2:-2].split('\n')
        mediafocus += cells[3].get_text()[2:-2].split('\n')
        language += cells[4].get_text()[2:-2].split('\n')
        
        remove = [i for i,r in enumerate(region) if r==''] # need to remove all rows for which "region" is empty
        
        # dealing with Sierra Leone Broadcasting Corporation:
        # if len(region) < len(names), combine last two elements if you're not already removing it
        if len(cells[0].get_text()[2:-2].split('\n')) < len([a.get_text().replace('\n','') for a in cells[1].find_all('a')]):
            if len([a.get_text().replace('\n','') for a in cells[1].find_all('a')])-1 not in remove:
                name2 = name.pop(-1)
                name[-1] += ' '+name2
                del link[-1]
        
        remove.reverse()
        for r in remove:
            del region[r]
            del link[r]
            del mediatype[r]
            del mediafocus[r]
            del language[r]
            
            name2 = name.pop(r) # append second row of name to the element before it
            name[r-1] += ' '+name2
        
        added = len(cells[0].get_text()[2:-2].split('\n')) - len(remove) # number of elements added
        
        # need to check if notes column is empty
        if len(cells[5].get_text().strip()) != 0: # if not empty
            notestring = str(cells[5]).replace('\n','')
            notestring = notestring[notestring.find('"2">')+4:] # remove prefix tags
            notestring = notestring[:notestring.find('</')] # remove trailing tags
            newnotes = [unicode(r) for r in notestring.split('<br>')] # split by <br> tags
        else:
            newnotes = [unicode('')]*added
        
        for r in remove:
            notes2 = newnotes.pop(r)
            newnotes[r-1] += notes2
        
        # this sometimes returns a list that's shorter than the others
        # because the notes column doesn't necessarily have an entry for every row
        # if so, add empty string entries to the end until it's the same length
        newnotes += [unicode('')]*(added - len(newnotes))
        notes += newnotes
            
        # safety check that all lists are still same length
        l = len(region)
        if not (len(name) == l and len(link) == l and len(mediatype) == l and len(mediafocus) == l and len(language) == l and len(notes) == l):
            print newnotes, 'length:', len(newnotes)
            print name, 'length:', len(name)
            print notes, 'length:', len(notes)
            raise ValueError("table columns are different lengths!")
    
    # put everything into a dataframe - not sure yet how to handle name repetitions
    alldatadict = {'region': pd.Series(region, index = name),
                   'link': pd.Series(link, index = name),
                   'media_type': pd.Series(mediatype, index = name),
                   'media_focus': pd.Series(mediafocus, index = name),
                   'language': pd.Series(language, index = name),
                   'notes': pd.Series(notes, index = name)}
                   
    alldata = pd.DataFrame(alldatadict)
    alldata.index.name = 'name'
    alldata['country'] = country
    return alldata

test_afghanistan = mediasources('Afghanistan', 'http://www.abyznewslinks.com/afgha.htm')
test_ireland = mediasources('Ireland', 'http://www.abyznewslinks.com/irela.htm')
test_egypt = mediasources('Egypt', 'http://www.abyznewslinks.com/egypt.htm')
test_sierraleone = mediasources('Sierra Leone', 'http://www.abyznewslinks.com/sierr.htm')
test_sgssi = mediasources('South Georgia and South Sandwich Islands', 'http://www.abyznewslinks.com/sgeor.htm')