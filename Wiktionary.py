import requests
import logging, threading, re, os, sys, datetime, time, codecs, string
import unicodedata
import urllib.parse

import imp

from lxml import html
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -  %(levelname)s -  %(message)s')
logging.disable(logging.DEBUG)

imp.reload(sys)
#sys.setdefaultencoding('utf8')


#### #### ####    SETTINGS    #### #### ####
inFile = ''
outFile = 'out.html'    #'WiktionaryJapanese.html'
sessionName = 'sessionWiktionary'    #'Wiktionary.html'

#### #### ####    SETTINGS    #### #### ####
libraryName = [
    'wktLibJa', 
    'wktLibEn'
    ]

# # # #
mainDicPage = [
    'https://ja.wiktionary.org', 
    'https://en.wiktionary.org'
    ]
# # # #
# # # #
langue = [
    u'\u65E5\u672C\u8A9E',    # Japanese in Japanese
    'Russian',                                  # Russian in English
    'Korean',                                       # Korean in English
    'English',                                     # English in English
    'Spanish',                                    # Spanish in English
    'Greek'                                         # Greek in English
    ]
# # # #

"""
Created on 2018-05-21
"""

HExtension = '.html'


splitMarker = '<hr class="sigil_split_marker"/>'
metaTitle = ['Actress','Release Date', 'Series','Genre','Director']
interSign1 = ': '
interSign2 = '|'



######################################################
def GetRes(myurl):
# pretend to be a browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # This is chrome, you can set whatever browser you like
    response = requests.get(myurl, headers=headers)
    return response.text
######################################################
def ShowProgress(i, aList):
    logging.info('{}/{}'.format( aList.index(i) +1, len(aList) )  )

##################################################################################################################################################################
######################################################
######################################################
##################################################################################################################################################################

singleLink = 'https://ja.wiktionary.org/wiki/%E5%88%9D'

str1 = '<html><body>'
str2 =  '<hr/>\n</body></html>'
delStr = [str1,
# '[', ']', u'\u7DE8\u96C6',
 str2
 ]

fullWidthPunctuations = [u'。', u'、', u'【',u'】',u'「', u'」', u'（', u'）','',
u'＝',u'～',u'・',u'…', u'×', u'—', u'“', u'”', u'『', u'』', u'※', u'…', u'’'
#u'１',u'２',u'３',u'４',u'５',u'６',u'７',u'８',u'９',u'０',
u'．', u'！ '
]

kns = [
u'ぁ', u'あ', u'ぃ', u'い', u'ぅ', u'う', u'ぇ', u'え', u'ぉ', u'お', 
u'か', u'が', u'き', u'ぎ', u'く', u'ぐ', u'け', u'げ', u'こ', u'ご',
u'さ', u'ざ', u'し', u'じ', u'す', u'ず', u'せ', u'ぜ', u'そ', u'ぞ', 
u'た', u'だ', u'ち', u'ぢ', u'っ', u'つ', u'づ', u'て', u'で', u'と', u'ど', 
u'な', u'に', u'ぬ', u'ね', u'の', 
u'は', u'ば', u'ぱ', u'ひ', u'び', u'ぴ', u'ふ', u'ぶ', u'ぷ', u'へ', u'べ', u'ぺ', u'ほ', u'ぼ', u'ぽ', 
u'ま', u'み', u'む', u'め', u'も', 
u'ゃ', u'や', u'ゅ', u'ゆ', u'ょ', u'よ', 
u'ら', u'り', u'る', u'れ', u'ろ', 
u'ゎ', u'わ', u'ゐ', u'ゑ', u'を', 
u'ん', u'ゔ', u'ゕ', u'ゖ', 
u'ァ', u'ア', u'ィ', u'イ', u'ゥ', u'ウ', u'ェ', u'エ', u'ォ', u'オ', 
u'カ', u'ガ', u'キ', u'ギ', u'ク', u'グ', u'ケ', u'ゲ', u'コ', u'ゴ', 
u'サ', u'ザ', u'シ', u'ジ', u'ス', u'ズ', u'セ', u'ゼ', u'ソ', u'ゾ', 
u'タ', u'ダ', u'チ', u'ヂ', u'ッ', u'ツ', u'ヅ', u'テ', u'デ', u'ト', u'ド', 
u'ナ', u'ニ', u'ヌ', u'ネ', u'ノ', 
u'ハ', u'バ', u'パ', u'ヒ', u'ビ', u'ピ', u'フ', u'ブ', u'プ', u'ヘ', u'ベ', u'ペ', u'ホ', u'ボ', u'ポ', 
u'マ', u'ミ', u'ム', u'メ', u'モ', 
u'ャ', u'ヤ', u'ュ', u'ユ', u'ョ', u'ヨ', 
u'ラ', u'リ', u'ル', u'レ', u'ロ', u'ヮ', u'ワ', u'ヰ', u'ヱ', u'ヲ', 
u'ン', u'ヴ', u'ヵ', u'ヶ', u'ヷ', u'ヸ', u'ヹ', u'ヺ'
 ]


ab = list(string.punctuation)
cd = list(string.ascii_letters)
ef = list(string.whitespace)
gh = list(string.digits)
skipGroup =  ab + cd + ef + gh + fullWidthPunctuations + kns

doubleReturn = '\n\n'



#########################################################################################################
#########################################################################################################
#########################################################################################################
def WiktionaryLU(singleWord, mainDicPage, langue, libraryFile, sessionFile):
    singleWord = ''.join( (singleWord) )
    logging.debug(singleWord)
    pageLink = ''.join(    (mainDicPage, '/wiki/', urllib.parse.quote_plus(singleWord) )     )
    logging.debug(pageLink)

    htmlText = GetRes(pageLink)
    soup = BeautifulSoup(htmlText,'lxml')
    # title
    wordPageTitle = soup.head.title.string
    logging.info(wordPageTitle)

    htmlBlock = htmlText.split('<h2>')
    for i in htmlBlock:
        if ( ('id="' + langue) in i):
            logging.debug('Here')
            soup = BeautifulSoup('<h2>' + i,'lxml')
            logging.debug( soup )

    editSedtion = soup.find_all('span', class_='mw-editsection')

    sp = str(soup)
    if ('<h2>Navigation menu</h2>' not in sp) and (u'<h2>案内メニュー</h2>' not in sp):
        for i in editSedtion:
            delStr.append(str(i) )

        for i in delStr:
            sp = sp.replace(i, '')

        h1MarkerBegin = '<h1>'; h1MarkerEnd = '</h1>'

        f = codecs.open( sessionFile ,'a',encoding='utf-8')
        f.write( ''.join((h1MarkerBegin, wordPageTitle, h1MarkerEnd, doubleReturn, sp))   )  #
        f.close()

        f = codecs.open( libraryFile, 'a',encoding='utf-8')
        sp = ''.join((h1MarkerBegin, wordPageTitle, h1MarkerEnd, doubleReturn, sp))
        f.write(  sp  )
        f.close()
        return ''
    else:
        return singleWord


###################################



################################################################
def SortLibrary(libraryFile):
    f = codecs.open(libraryFile,'r',encoding='utf-8')
    g = f.readlines()
    f.close()

    g = ''.join(g)
    h = ( g.split('<h1>') ); h = list(set(h)); h.sort(); h = h[1:]

    f = codecs.open(libraryFile,'w',encoding='utf-8')
    for i in h:
        f.write('<h1>' + i + '\n')
    f.close()

################################################################
def LoadKanjiLibrary(libraryFile):
    # read the library and split it into two parts: title and content
    f = codecs.open( libraryFile, 'r', encoding='utf-8')
    g = f.readlines()
    f.close()

    g = ''.join(g)
    h = ( g.split('<h1>') ); h = list(set(h)); h.sort(); h = h[1:]


    KanjiCharacter = []
    KanjiPronunciation = []
    for i in h:
        kjC = i.split(' - ')[0]
        KanjiCharacter.append(kjC)
        kjP = i.split(' - ')[-1]
        KanjiPronunciation.append(kjP)

    return (KanjiCharacter, KanjiPronunciation)
#######################
def GetPronunciation(j, kjCr, pnPt):
    jIndex = kjCr.index(j)
    kk =  BeautifulSoup(pnPt[jIndex],'lxml')

    kk = kk.get_text()
    return kk

#######################
def CharDeal(b, westChar=0):
    toLookup = []
    if westChar==0:
        for i in b:
            i = i.strip()
            i = unicodedata.normalize('NFKC', i)
            for j in i:
                toLookup.append(j.strip() )
    else:
        for i in b:
            i = ( i.strip() ).lower()
            temp = i.split(' ')
            for j in temp:
                toLookup.append(j)
    return toLookup


########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################

def mainFunc(inFile, mainDicPage, libName, langue, sessionFl, splitType=1):
    libFile= ''.join( (libName, HExtension) )

    # sort and load library
    KanjiCt = []
    try:
        SortLibrary(libFile)                                                    # sort library
        KanjiCt  = LoadKanjiLibrary(libFile)[0]    # load library
        logging.info('Library                 -- {0}'.format(len(KanjiCt) ) )
    except:
        logging.info('No library!')

    # create result file
    f = codecs.open( outFile,'w',encoding='utf-8')
    f.close()

    # read text
    g = codecs.open(inFile, encoding='utf-8', mode='r')
    b = g.readlines()
    g.close()

    # Eastern
    toLookup = CharDeal(b, splitType)
    toLookup = list(set(toLookup))    # delete duplicate words

    # words need to look up
    toLookup2 = []
    for i in toLookup:
        i = i.strip()
        if (i not in (KanjiCt + skipGroup) ) and (len(i)>0):
            #logging.info(i)
            toLookup2.append(i)

    cleanlist = []
    [cleanlist.append(x) for x in toLookup2 if x not in cleanlist]
    toLookup2 = cleanlist
    if len(toLookup2)>0:
        logging.info('Amount of words, This session -- {}\n{}'.format(  len(toLookup2) , toLookup2 ) )
    else:
        logging.info('No new words to search, this session!')
    
    noSearch = []
    for i in toLookup2:
        ShowProgress(i, toLookup2)
        notS = WiktionaryLU(i, mainDicPage, langue, libFile, sessionFl)
        
        if ( len(notS) >0 ):
            noSearch.append(notS)
    if ( len(noSearch) >0 ):
        logging.info('These words cannot be searched -- ({})\n{}'.format( len(noSearch), noSearch ) )

    # sort library
    SortLibrary(libFile)
    KanjiCt  = LoadKanjiLibrary(libFile)[0]    # load library
    logging.info('Library                 -- {0}'.format(len(KanjiCt) ) )

########################################################################################################
def MainRun():
    startTime = datetime.datetime.now()


    [print('Wiktionary page: {} for {}'.format( mainDicPage.index(i), i ) ) for i in mainDicPage ]
    wikiNo = input('\nPlease select page: ')
    i = int(wikiNo); logging.info('You have chosen {}\n'.format(mainDicPage[i]) )

    [print('Language: {} for {}'.format( langue.index(i), i ) ) for i in langue ]
    langueNo = input('\nPlease select word language: ' )
    j =int(langueNo); logging.info('You have chosen {}'.format(langue[j]) )

    if j ==0:
        inFile = 'test2.html'
    elif j==1:
        inFile = 'test5.html'
    elif j==2:
        inFile = 'testKorean.html'

    """
    paragraphSearch = input('Please paste your paragraph HERE: \n')

    # read text
    g = codecs.open(inFile, encoding='utf-8', mode='a')
    g.write('********\n{}\n********\n'.format(paragraphSearch) )
    g.close()"""

    splitType = input('Please select split type: 0 or 1?  default value = 1\n(0 for eastern word, 1 for western word)\n')
    #WiktionaryJa(inFile, mainDicPage[i] , libraryName[i], langue[j])

    logging.info('Input File -- {}'.format(inFile) )
    sessionFile = ''.join( (sessionName, libraryName[i], langue[j], str(startTime).replace(':','_'), HExtension) )

    mainFunc(inFile, mainDicPage[i] , libraryName[i], langue[j], sessionFile, int(splitType) )




    endTime = datetime.datetime.now()
    sessionDuration = endTime - startTime
    logging.info(sessionDuration)



#########################################################################################################


#########################################################################################################


