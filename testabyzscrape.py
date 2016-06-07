import unittest
from abyzscrape import *

class test_abyzscrape(unittest.TestCase):
    
    def test_getcountries(self):
        countrydict = getcountries()
        
        # afghanistan
        self.assertEqual(countrydict['Afghanistan'], ['afgha.htm'])
        
        # vatican
        self.assertEqual(countrydict['Holy See'], ['vatic.htm'])
        
        # zimbabwe
        self.assertEqual(countrydict['Zimbabwe'], ['zimba.htm'])
        
        # india has a subregions page
        self.assertEqual(countrydict['India'][0], 'india.htm')
        self.assertEqual(countrydict['India'][1]['Haryana'], ['india_haryana.htm'])
        self.assertEqual(countrydict['India'][1]['Mizoram'], ['india_mizoram.htm'])
        self.assertEqual(countrydict['India'][1]['West Bengal'], ['india_west_bengal.htm'])
        self.assertEqual(countrydict['India'][1]['India National'], ['india_national.htm'])

        # united states has subregions listed by both state and city
        # make sure we're grabbing states, not cities
        self.assertEqual(countrydict['United States'][0], 'unite.htm')
        self.assertEqual(countrydict['United States'][1]['National'], ['unitena.htm'])
        self.assertEqual(countrydict['United States'][1]['Wyoming'], ['unitewy.htm'])
        self.assertEqual(countrydict['United States'][1]['Kansas'], ['uniteks.htm'])
        self.assertEqual(countrydict['United States'][1]['South Carolina'], ['unitesc.htm'])
                
    def testSpain(self):
        data = mediasources('Spain', 'http://www.abyznewslinks.com/spain.htm')
        
        # region name has a newline character in the middle
        media = 'El Bruguers'
        self.assertEqual(data['link'][media], 'http://www.elbruguers.cat/')
        self.assertEqual(data['region'][media], 'Gav\xc3\xa1 -Gav\xc3\xa0')
        self.assertEqual(data['country'][media], 'Spain')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'CAT')
        self.assertEqual(data['notes'][media], '')
        
        # region name has two rows
        media = 'Axencia Galega de Noticias'
        self.assertEqual(data['link'][media], 'http://www.axencia.com/')
        self.assertEqual(data['region'][media], 'Santiago de Compostela')
        self.assertEqual(data['country'][media], 'Spain')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'PA')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'SPA')
        self.assertEqual(data['notes'][media], '')
        
        # arbitrary row near the bottom
        media = 'Super Deporte'
        self.assertEqual(data['link'][media], 'http://www.superdeporte.es/')
        self.assertEqual(data['region'][media], 'Valencia')
        self.assertEqual(data['country'][media], 'Spain')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'SP')
        self.assertEqual(data['language'][media], 'SPA')
        self.assertEqual(data['notes'][media], '')
        
    
    def testAfghanistan(self):
        data = mediasources('Afghanistan', 'http://www.abyznewslinks.com/afgha.htm')
        
        # table with only one row
        media = 'Sharq'
        self.assertEqual(data['link'][media], 'http://www.shaiqnetwork.com/')
        self.assertEqual(data['region'][media], 'Jalalabad')
        self.assertEqual(data['country'][media], 'Afghanistan')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'BC')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'PUS')
        self.assertEqual(data['notes'][media], 'RadioTV')
        
        # another table with only one row
        media = 'Yadgar Afghan'
        self.assertEqual(data['link'][media], 'http://www.yadgarafghan.com/da/')
        self.assertEqual(data['region'][media], 'Mazar i Sharif')
        self.assertEqual(data['country'][media], 'Afghanistan')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'IN')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'DAR')
        self.assertEqual(data['notes'][media], '')
        
        # arbitrary table near the top
        media = 'UN News Centre'
        self.assertEqual(data['link'][media], 'http://www.un.org/apps/news/infocusRel.asp?infocusID=16&Body=Afghanistan')
        self.assertEqual(data['region'][media], 'Nationwide')
        self.assertEqual(data['country'][media], 'Afghanistan')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'IN')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
    
    def testCanadaYukon(self):
        data = mediasources('Canada', 'http://www.abyznewslinks.com/canadyk.htm', subcountry = 'Yukon')
        
        # table with exactly two rows
        media = 'Government of Yukon'
        self.assertEqual(data['link'][media], 'http://www.gov.yk.ca/news/')
        self.assertEqual(data['region'][media], 'Territory')
        self.assertEqual(data['country'][media], 'Canada')
        self.assertEqual(data['subcountry'][media], 'Yukon')
        self.assertEqual(data['media_type'][media], 'IN')
        self.assertEqual(data['media_focus'][media], 'GO')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
        media = 'Yukoner Magazine'
        self.assertEqual(data['link'][media], 'http://www.yukoner.com/')
        self.assertEqual(data['region'][media], 'Territory')
        self.assertEqual(data['country'][media], 'Canada')
        self.assertEqual(data['subcountry'][media], 'Yukon')
        self.assertEqual(data['media_type'][media], 'MG')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
    def testSierraLeone(self):
        data = mediasources('Sierra Leone', 'http://www.abyznewslinks.com/sierr.htm')
        
        # sierra leone broadcasting corporation is a two-row link, 
        # other entries in table only have one row
        media = 'Sierra Leone Broadcasting Corporation'
        self.assertEqual(data['link'][media], 'http://www.slbc.sl/')
        self.assertEqual(data['region'][media], 'National')
        self.assertEqual(data['country'][media], 'Sierra Leone')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'BC')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'Radio TV')
        
        # arbitrary row, just to check that everything's lined up
        media = 'Sierra Leone Times'
        self.assertEqual(data['link'][media], 'http://www.sierraleonetimes.com/')
        self.assertEqual(data['region'][media], 'Foreign')
        self.assertEqual(data['country'][media], 'Sierra Leone')
        self.assertEqual(data['subcountry'][media], None)
        self.assertEqual(data['media_type'][media], 'IN')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
    
    def testMaine(self):
        data = mediasources('United States', 'http://www.abyznewslinks.com/uniteme.htm', subcountry = 'Maine')
        # maine has a typo in the last two columns - we have a missing entry for South Portland Cape Elizabeth Sentry
        
        media = 'South Portland Cape Elizabeth Sentry'
        self.assertEqual(data['link'][media], 'http://sentry.mainelymediallc.com/')
        self.assertEqual(data['region'][media], 'South Portland')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Maine')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
        media = 'Compass Classifieds'
        self.assertEqual(data['link'][media], 'http://penobscotbaypress.com/classifieds/')
        self.assertEqual(data['region'][media], 'Stonington')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Maine')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'SH')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
        media = 'Colby Echo'
        self.assertEqual(data['link'][media], 'http://www.thecolbyecho.com/')
        self.assertEqual(data['region'][media], 'Waterville')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Maine')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'CO')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'Colby')
    
    def testFlorida(self):
        data = mediasources('United States', 'http://www.abyznewslinks.com/unitefl.htm', subcountry = 'Florida')
        # has a missing <br> character somewhere in the "media type" column
        # checking alignment near bottom
        media = 'Sandspur'
        self.assertEqual(data['link'][media], 'http://www.thesandspur.org/')
        self.assertEqual(data['region'][media], 'Winter Park')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Florida')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'CO')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'Rollins')
        
        # checking alignment in middle
        media = 'Tampa Bay Metro Magazine'
        self.assertEqual(data['link'][media], 'http://www.tampabaymetro.com/')
        self.assertEqual(data['region'][media], 'Tampa')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Florida')
        self.assertEqual(data['media_type'][media], 'MG')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
        # checking alignment in middle
        media = "Water's Edge"
        self.assertEqual(data['link'][media], 'http://www.waters-edge.com/')
        self.assertEqual(data['region'][media], 'Jacksonville')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Florida')
        self.assertEqual(data['media_type'][media], 'MG')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
        # checking alignment near top
        media = "Boca Raton News"
        self.assertEqual(data['link'][media], 'http://bocanews.com/')
        self.assertEqual(data['region'][media], 'Boca Raton')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Florida')
        self.assertEqual(data['media_type'][media], 'IN')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
    
    def testMinnesota(self):
        data = mediasources('United States', 'http://www.abyznewslinks.com/unitemn.htm', subcountry = 'Minnesota')
        # has an extra newline character somewhere in the "media focus" column
        # checking alignment near bottom
        media = 'KWOA'
        self.assertEqual(data['link'][media], 'http://kwoa.com/')
        self.assertEqual(data['region'][media], 'Worthington')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Minnesota')
        self.assertEqual(data['media_type'][media], 'BC')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'AM 730')
        
        #checking alignment near top
        media = "Lion's Roar"
        self.assertEqual(data['link'][media], 'http://www.lionsroar.info/')
        self.assertEqual(data['region'][media], 'Bloomington')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Minnesota')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'CO')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'Normandale Community')
        
    def testMassachusetts(self):
        data = mediasources('United States', 'http://www.abyznewslinks.com/unitema.htm', subcountry = 'Massachusetts')
        
        # notes column has two rows
        # and check that subcountry field is populated correctly
        media = 'Daily Collegian'
        self.assertEqual(data['link'][media], 'http://dailycollegian.com/')
        self.assertEqual(data['region'][media], 'Amherst')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Massachusetts')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'CO')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'Massachussets Amherst')
        
        # notes column has two rows AND region column has two rows
        # there are two newspapers called "Patriot" - disambiguate
        media = 'Patriot'
        self.assertEqual(data['link'][media][1], 'http://www.westover.afrc.af.mil/library/patriot/')
        self.assertEqual(data['region'][media][1], 'Westover Air Reserve Base')
        self.assertEqual(data['country'][media][1], 'United States')
        self.assertEqual(data['subcountry'][media][1], 'Massachusetts')
        self.assertEqual(data['media_type'][media][1], 'NP')
        self.assertEqual(data['media_focus'][media][1], 'ML')
        self.assertEqual(data['language'][media][1], 'ENG')
        self.assertEqual(data['notes'][media][1], 'Westover Air Reserve Base')
        
        # link/name in middle of table has two rows
        media = 'Northborough Southborough Villager'
        self.assertEqual(data['link'][media], 'http://www.wickedlocal.com/northborough')
        self.assertEqual(data['region'][media], 'Northborough')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Massachusetts')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'GI')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], '')
        
        # for fun
        media = 'Tech'
        self.assertEqual(data['link'][media], 'http://tech.mit.edu/')
        self.assertEqual(data['region'][media], 'Cambridge')
        self.assertEqual(data['country'][media], 'United States')
        self.assertEqual(data['subcountry'][media], 'Massachusetts')
        self.assertEqual(data['media_type'][media], 'NP')
        self.assertEqual(data['media_focus'][media], 'CO')
        self.assertEqual(data['language'][media], 'ENG')
        self.assertEqual(data['notes'][media], 'MIT')
                
if __name__ == '__main__':
    unittest.main()