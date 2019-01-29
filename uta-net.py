import requests, urllib
import logging, threading, re, os, sys, datetime, time, codecs
import unicodedata

import Wiktionary

from lxml import html
from bs4 import BeautifulSoup
from kanaconv import KanaConv

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -  %(levelname)s -  %(message)s')
#logging.disable(logging.DEBUG)

"""
usage:
example - 
python3 uta-net.py 'ゆるぎない'
"""


#### #### ####    SETTINGS    #### #### ####
#songTitle = 'kokurikosakakara'
#song_title_keyword = 'ゆるぎない'
Aselect = 2    # 2 for song title
inFile1 = 'test2.html'
inFifle2 = 'test5.html'
#### #### ####    SETTINGS    #### #### ####
"""
Uta-net for Japanese Lyrics
"""


netMain = 'https://www.uta-net.com'

libraryName = [
    'wktLibJa', 
    'wktLibEn'
    ]



doubleReturn = '\n\n'
baseLineSkip = '\\baselineskip'
ideagraphicSpace = u'\u3000'
letraStrucuture = '[Verse]<br/>[Pre-chorus]<br/>[Chorus]<br/>[Interlude]<br/>[Bridge]<br/>[End]<br/><br/>'


ttpp = 'data-fetch-wordpress'
splitMarker = '<hr class="sigil_split_marker"/>'



######################################################
def GetRes(myurl):
# pretend to be a browser
    """
# http://stackoverflow.com/questions/41946166/requests-get-returns-403-while-the-same-url-works-in-browser
that's because default User-Agent of requests is python-requests/2.13.0, and in your case that website don't like traffic from "non-browsers", so they try to block such traffic.

All you need to do is to make the request appear like coming from a browser, so just add an extra header parameter"""

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # This is chrome, you can set whatever browser you like
    response = requests.get(myurl, headers=headers)
    
    #print response.status_code
    #print response.url
    
    # return html.fromstring(response.content)
    return response.text
######################################################

UtaNetSpliter = u' \u6B4C\u8A5E - '


################################################################
def search_uta_net(song_keyword):
    # search and show the result by song title (keyword)
    searchLink =  netMain + '/search/?Aselect=' + str(Aselect)+ '&Keyword=' + song_keyword + '&Bselect=1&x=0&y=0'

    logging.info( 'searchLink' )
    logging.info( searchLink )

    htmlText = GetRes(searchLink)
    soup = BeautifulSoup(htmlText,'lxml')

    result_table = ( soup.find_all('tbody') )
    result_block = BeautifulSoup(str(result_table),'lxml')

    result_items = result_block.find_all('tr')

    result_info = []
    for i in result_items:
        result_info.append( get_song_info(i) )

    # show the result
    logging.info('Search results - ')
    count = 1
    for i in result_info:
        print(str(count) + '  ' + i[0] + '\n   ' + i[1] + '\n   ' + i[2])
        count = count + 1
    
    return (result_info, count - 1)

##########################
def get_song_info(table_item):
    # get the song tiltle, artist name, first line of the lyrics and the song number on Uta-Net

    item_contents = BeautifulSoup( str(table_item), 'lxml')

    # title and number
    song_title_info = item_contents.find('td', class_="side td1")
    song_number = BeautifulSoup( str(song_title_info), 'lxml').find('a')
    song_number_str = str(song_number).split('/')[2]
    song_title_str = song_title_info.get_text()

    # artist
    artist_info = item_contents.find('td', class_="td2")
    artist_str = artist_info.get_text()

    # lyrics
    lyrics_info = item_contents.find('td', class_="side td5")
    lyrics_str = lyrics_info.get_text()

    return (song_title_str, artist_str, lyrics_str, song_number_str)

######################################################
def singleLetra(songNumber):
    singleLink = netMain + '/song/' + songNumber
    htmlText = GetRes(singleLink)
    soup = BeautifulSoup(htmlText,'lxml')

    # title
    singleTitle = ( ( soup.find_all('h2') )[0] ).get_text()
    logging.info('Song Title: {0}'.format(singleTitle) )

    #lyricsBlock --  a list, debug by default
    letraBlock = ( soup.find_all('div', id='kashi_area') )[0]
    logging.debug( type(letraBlock) )
    logging.info( letraBlock )

    #
    artista = ( soup.find_all('span', itemprop='byArtist name') )[0]
    letrista = ( soup.find_all('h4', itemprop='lyricist') )[0]
    compositor = ( soup.find_all('h4', itemprop='composer') )[0]
    logging.info( (artista.string, letrista.string, compositor.string ) )

    dateNoBlock = ( soup.find_all('div', id='view_amazon') )[0]
    dateNoStudio01 = str(dateNoBlock).split('<a href') [1]
    dateNoStudio02 = dateNoStudio01.split('</a><br/>')[1]
    publishDate = ( dateNoStudio02.split('<br/>')[0] ).split(u'\uFF1A')[-1]
    #print u'\uFF1B'
    logging.info( publishDate )

    purchaseNo = ''
    produceStudio = ''
    try:
        purchaseNo =( dateNoStudio02.split('<br/>')[1] ).split(u'\uFF1A')[-1]
        produceStudio = dateNoStudio02.split('<br/>')[2]
        logging.info( purchaseNo )
        logging.info( produceStudio )
    except:
        pass

    # write html file
    f = codecs.open( singleTitle + '.html','w',encoding='utf-8')
    f.write('<h1>' + singleTitle + '</h1>' + splitMarker + '<br/>')
    f.write(letraStrucuture)

    for idl in letraBlock:
        tempgg = str(idl).replace(ideagraphicSpace, ' ')    # repace the full-width space, the last step
        f.write( tempgg )
    
    f.write('<br/><br/>Performed by ' + artista.string )
    f.write('<br/>Lyrics by ' + letrista.string )
    f.write('<br/>Composed by ' + compositor.string )
    f.write('<br/><br/>Published on ' + publishDate)
    try:
        f.write('<br/>Itemized as ' + purchaseNo)
        f.write('<br/>Released by ' + produceStudio)
    except:
        pass
    f.write('<br/>Uta-Net No.' + str(songNumber) )

    f.close()

    ########
    songTitle = input('\n\tGive me the song Title in Romaji: ')
    print('\n')

    ###############################################################
    # look up kanji
    KanjiCt, KanjiPn  = Wiktionary.LoadKanjiLibrary(libraryName[0] + '.html')    # reload the library

    toLookup = Wiktionary.CharDeal(str(letraBlock), 0)
    toLookup = list(set(toLookup))    # delete duplicate words

    # words need to look up
    toLookup2 = []
    for i in toLookup:
        i = i.strip()
        if (i not in (KanjiCt + Wiktionary.skipGroup) ) and (len(i)>0):
            #logging.info(i)
            toLookup2.append(i)

    cleanlist = []
    [cleanlist.append(x) for x in toLookup2 if x not in cleanlist]
    toLookup2 = cleanlist


    if len(toLookup2)>0:
        logging.info('Amount of words, This session -- {}\n{}'.format(  len(toLookup2) , toLookup2 ) )
    else:
        logging.info('No new words to search, this session!')

    fnn = codecs.open( inFile1, 'a',encoding='utf-8')
    fnn.write( ' '.join(toLookup2)  + '\r\n')
    fnn.close()

    i = 0
    j = 0
    Wiktionary.mainFunc(inFile1, Wiktionary.mainDicPage[i] , Wiktionary.libraryName[i], Wiktionary.langue[j], songTitle + 'newWords.html', 0 )

    #################################################
    # for LaTeX
    #cnv = KanaConv()
    #rmj = cnv.to_romaji(singleTitle) 
    f = codecs.open(songTitle + '.tex','w',encoding='utf-8')
    f.write(f'\\documentclass{{lyrics.tex}}\n\\chapter{{' + singleTitle + f'}}'  )
    f.write('\n\\Brule\n\n\\btpr\n\n\\btbl\n\n')
    f.write(letraStrucuture.replace( '<br/>','\n' ) )

    f.write('\n%        %\n\\addtocounter{footnote}{-2} %3=n\n%        %\n\\vspace{-2\\baselineskip}\n\\sfnt{    }\n\\sfnt{ }\n\\vspace{2\\baselineskip}' + doubleReturn)
    
    


    KanjiCt, KanjiPn  = Wiktionary.LoadKanjiLibrary(libraryName[0] + '.html')    # reload the library
    
    sessionGlossary = []
    for idl in letraBlock:
        tempgg = str(idl).replace(ideagraphicSpace, ' ')    # repace the full-width space, the last step
        tephh = tempgg.replace( '<br/>', doubleReturn )

        for j in tephh:
            tep = ''
            if (j not in Wiktionary.skipGroup):
                j = j.strip()
                if j in KanjiCt:
                    tep = Wiktionary.GetPronunciation(j,KanjiCt, KanjiPn)    # read pronunciation from the library
                    sessionGlossary.append((j+ ' - ' + tep))
                    f.write( f'\\ruby[m]{{' + j + f'}}{{    }}' )
            else:
                f.write( j )

    f.write(doubleReturn + '\\vspace{2\\baselineskip}'+ doubleReturn)
    f.write('Performed by ' + artista.string + doubleReturn)
    f.write('Lyrics by ' + letrista.string + doubleReturn )
    f.write('Composed by ' + compositor.string  + doubleReturn)
    f.write('Published on ' + publishDate + doubleReturn)
    try:
        f.write('Itemized as ' + purchaseNo + doubleReturn)
        f.write('Released by ' + produceStudio + doubleReturn)
    except:
        pass
    f.write('Uta-Net No.' + str(songNumber)  + doubleReturn)
    f.write('\\Brule'+ doubleReturn)

    f.close()

    cleanlist = []
    [cleanlist.append(x) for x in sessionGlossary if x not in cleanlist]
    sessionGlossary = cleanlist

    f = codecs.open( songTitle + 'sesssion.html','w',encoding='utf-8')
    for i in sessionGlossary:
        f.write(str(i)+splitMarker+doubleReturn)




##########################
def MainRun(song_ti_str):
    startTime = datetime.datetime.now()

    # ---------------------------------------------
    results, range_number = search_uta_net( song_ti_str )

    select_number = input('\nWhich song would you like to get the lyrics? (max: {0}) - '.format( str(range_number) ) )
    real_index = int(select_number) -1

    singleLetra( results[real_index ][-1])
    # ---------------------------------------------

    endTime = datetime.datetime.now()
    sessionDuration = endTime - startTime
    logging.info(sessionDuration)

################################################################

#MainRun()

##########################################
if __name__ == '__main__':
    if len(sys.argv) == 2 and '*' in sys.argv[1]:
        files = glob.glob(sys.argv[1])
        random.shuffle(files)
    else:
        files = sys.argv[1:]
    
    for path in files:
        #out_path = path.replace('.jpg', '.crop.png')
        #out_path = out_dir + path.replace('.png', '.crop.png')  # .png as input
        #if os.path.exists(out_path): continue
        try:
            MainRun( urllib.parse.quote_plus(path) )
        except Exception as e:
            print('%s %s' % (path, e))