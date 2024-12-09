#!/usr/bin/env python3

import os
import urllib.request
import numpy as np
import pandas as pd
import telegram_send
import itertools
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

gitpath = os.popen('git rev-parse --show-toplevel').read()[:-1]

class pepfindbot:
    """
    A class to find papers on ArXiv by keyword and send results on Telegram.
    """

    def get_link(self, field='astro-ph', when='today'):
        """
        Generate the ArXiv link based on the field and time range.

        Args:
            field (str): The ArXiv field to search (default: 'astro-ph').
            when (str): Time range for the search, either 'today' or 'past week' (default: 'today').

        Returns:
            str: The generated ArXiv link.
        """
        if when == 'today':
            link = f"https://arxiv.org/list/{field}/new?skip=0&show=1000"
        elif when == 'past week':
            link = f"https://arxiv.org/list/{field}/pastweek?show=270"
        else:
            raise ValueError('"when" can only be "today" or "past week"')
        return link

    def get_webpage(self, field='astro-ph', when='today'):
        """
        Fetch and parse the ArXiv webpage.

        Args:
            field (str): The ArXiv field to search (default: 'astro-ph').
            when (str): Time range for the search, either 'today' or 'past week' (default: 'today').

        Returns:
            BeautifulSoup: Parsed HTML content of the ArXiv page.
        """
        link = self.get_link(field, when)
        f = urllib.request.urlopen(link)
        myfile = f.read()
        soup = BeautifulSoup(myfile, 'html.parser')
        return soup

    def create_lists(self, words, field='astro-ph', when='today'):
        """
        Create a pandas DataFrame and a list with papers and URLs containing keywords.

        Args:
            words (list): List of lists containing keywords to search for.
            field (str): The ArXiv field to search (default: 'astro-ph').
            when (str): Time range for the search, either 'today' or 'past week' (default: 'today').

        Returns:
            tuple: Contains DataFrame of matching papers, count of keyword appearances, 
                   total number of papers, number of new papers, tags, and formatted author messages.
        """
        for i in words:
            if np.shape(i) == ():
                print('You have to give a list of list of words, e.g. [["lens"], ["gw", "gravitational wave"]]')
                break
        
        soup = self.get_webpage(field, when)

        # find titles #
        titles = soup.findAll('div', {"class":"list-title mathjax"})
        titles = [x.text.strip()[7:] for x in titles]
        papers_number = len(titles)

        # find abstracts #
        paragraphs = soup.findAll('p'.strip())
        abstracts = paragraphs[1:-2]
        abstracts = [x.text.strip() for x in abstracts]
        papers_number_new = len(abstracts)

        # find urls #
        # urls = soup.findAll('span', {'class':'list-identifier'})
        urls = soup.findAll('a', {'title':'Abstract'})
        urls = ['https://arxiv.org'+i.get('href') for i in urls]
        
        # find authors
        authors_complete = soup.findAll('div', {"class":"list-authors"})
        authors = [i.text.strip() for i in authors_complete] # .splitlines()[1:]

        # find papers from key words #
        ips = []
        tags = ['#'+words[i][0].replace(' ', '') for i in range(len(words))]
        tag_list = []
        for nn, word_l in enumerate(words):    
            for word in word_l:
                for n, abstract in enumerate(abstracts):
                    if word in abstract.lower().replace('-', ' ').replace('  ', ' ') :
                        ips.append(n)
                        tag_list.append([n,nn])
                for n, title in enumerate(titles):
                    if word in title.lower().replace('-', ' ').replace('  ', ' ') :
                        ips.append(n)
                        tag_list.append([n, nn])

        ips_t = ips.copy()
        ips = list(set(ips))
        ips.sort()

        tag_list.sort()
        
        # delete duplicate in tag_list
        tag_list = list(tag_list for tag_list,_ in itertools.groupby(tag_list))
        
        # find and organize tags #
        tl = []
        for n,i in enumerate(tag_list):
            p, t = i[0], tags[i[1]]
            if n ==0 :
                tl.append([p, t]) 
            elif [p,t] not in tl:
                if not p in tl[-1]:
                    tl.append([p, t])
                else:
                    tl[-1][1] += ' '+t
                    
        tl = [tl[n][1] for n in range(len(tl))]
        
        # create and fill DataFrame #
        recap = pd.DataFrame(columns=['title', 'authors', 'tags', 'url'])
        recap['title'] = [titles[i].replace('<', '\less') for i in ips]
        recap.index = [i+1 for i in ips]
        recap['authors'] = [authors[i][8:].replace('\n','') for i in ips]
        recap['tags']  = tl
        recap['url'] = [urls[i] for i in ips]
        # recap['url'] = ['https://www.google.com/' for i in ips]
        
        count_tags = [0 for i in range(len(tags))]
        for n,word in enumerate(tags):
            for i in recap.index:
                if word in recap.tags[i]:
                    count_tags[n] += 1
        
        aut_message = []
        for i in ips:
            ac_url = authors_complete[i].findAll('a')
            if len(ac_url) < 4 :
                ac_url = str(authors_complete[i])[68:-7].replace('\n', '').replace('/search/', 'www.arxiv.org/search/').replace('%2C+', ',')
            else:
                ac_url2 = ''
                for au in ac_url[:3]:
                    ac_url2 += str(au).replace('/search/', 'www.arxiv.org/search/').replace('%2C+', ',') + ', '
                ac_url = ac_url2 + ' et al.'
            aut_message.append(ac_url)

        return recap, count_tags, papers_number, papers_number_new, tags, aut_message

    def create_message(self, words, field='astro-ph', when='today'):
        """
        Create a formatted message with the search results.

        Args:
            words (list): List of lists containing keywords to search for.
            field (str): The ArXiv field to search (default: 'astro-ph').
            when (str): Time range for the search, either 'today' or 'past week' (default: 'today').

        Returns:
            list: List of formatted messages ready to be sent via Telegram.
        """
        
        recap, count_tags, papers_number, papers_number_new, tags, aut_message = self.create_lists(words, field, when)
        
        total_number_message = f'📜 <b>{field}</b>\n{papers_number} total papers today!\n{papers_number_new} brand new!'

        message = total_number_message + f'\n\nYou have {len(recap.title)} new interesting papers!'
        
        for i in range(len(tags)):
            message += '\n%i in %s'%(count_tags[i], tags[i])
        message += '\n'
        
        message += '\n➕'+'➖'*10+'➕\n'+' '*17+'New Papers\n➕'+'➖'*10+'➕\n'
        
        message_final = []
        new_paper = True
        done = False
        
        for n,i in enumerate(recap.index):
            if i > papers_number_new :
                new_paper = False
            if not new_paper and not done :
                message += '\n➕'+'➖'*10+'➕\n'+' '*18+'Old Papers\n➕'+'➖'*10+'➕\n'
                done = True
            single_line = f'\n{i}) {recap.title[i]}\n<i>{aut_message[n]}</i>\
                            \n{recap.tags[i]}\n<a href="{recap.url[i]}">{recap.url[i][-10:]}</a>\n'
            if len(message) + len(single_line) < 4086:
                message += single_line
            else:
                message_final.append(message)
                message = single_line
        
        message_final.append(message)

        return message_final

    def send_telegram(self, words, field='astro-ph', when='today'):
        """
        Send the search results via Telegram.

        Args:
            words (list): List of lists containing keywords to search for.
            field (str): The ArXiv field to search (default: 'astro-ph').
            when (str): Time range for the search, either 'today' or 'past week' (default: 'today').
        """
        message = self.create_message(words, field, when)
        telegram_send.send(conf=gitpath+'/.telconfigs/configuration', messages=[m for m in message], parse_mode='html')

    def find_authors(self, author_list, field='astro-ph', when='today'):
        """
        Find papers by specific authors on ArXiv.

        Args:
            author_list (list): List of author names to search for.
            field (str): The ArXiv field to search (default: 'astro-ph').
            when (str): Time range for the search, either 'today' or 'past week' (default: 'today').

        Returns:
            None: Sends the results via Telegram.
        """
        
        if type(author_list) != list:
            error_message = '"author_list" must be a list'
            return error_message
        else:
            author_list.sort()
        
        soup = self.get_webpage(field, when)
        
        authors_complete = soup.findAll('div', {"class":"list-authors"})
        authors_papers = [i.text.strip() for i in authors_complete] # .splitlines()[1:]
        
        ips = []
        for author in author_list:
            for n,authors_paper in enumerate(authors_papers):
                if author in authors_paper:
                    ips.append(n)
                    
        ips = list(set(ips))
        ips.sort()
        
        titles = soup.findAll('div', {"class":"list-title mathjax"})
        titles = [x.text.strip()[7:] for x in titles]
        papers_number = len(titles)
        
        aut_message = []
        for i in ips:
            ac_url = authors_complete[i].findAll('a')
            if len(ac_url) < 4 :
                ac_url = str(authors_complete[i])[68:-7].replace('\n', '').replace('/search/', 'www.arxiv.org/search/').replace('%2C+', ',')
            else:
                ac_url2 = ''
                for au in ac_url[:3]:
                    ac_url2 += str(au).replace('/search/', 'www.arxiv.org/search/').replace('%2C+', ',') + ', '
                ac_url = ac_url2 + ' et al.'
            aut_message.append(ac_url)
    
        urls = soup.findAll('span', {'class':'list-identifier'})
        urls = ['https://arxiv.org'+i.find('a').get('href') for i in urls]
        
        if len(ips) == 0:
            pass
        else:    
            message = '%i papers found among your author list in <b>%s</b>!\n'%(len(ips), field)
            # print(message)
            message_final = []
            for n,i in enumerate(ips):
                single_line = '\n{}) {}\n<i>{}</i>\n<a href="{}">{}</a>\n'.format(i, titles[i], aut_message[n], urls[i], urls[i][-10:])
                if len(message) + len(single_line) < 4086:
                    message += single_line
                else:
                    message_final.append(message)
                    message = single_line
            
            message_final.append(message)
            
            telegram_send.send(conf=gitpath+'/.telconfigs/configuration', messages=[m for m in message_final], parse_mode='html')