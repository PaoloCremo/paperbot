#!/usr/bin/env python3

def main():
    
    import os
    gitpath = os.popen('git rev-parse --show-toplevel').read()[:-1]
    os.chdir(gitpath)

    import datetime
    import telegram_send
    
    from find_paper import find_paper_class as fp_c
    pfb = fp_c.pepfindbot()
    
    wrds = [['lens'], ['gw', 'gravitational wave', 'gravitaitonal-wave'], ['machine learning', 'deep learning']]
    fields = ['gr-qc', 'astro-ph']
    
    author_list = ['A. Einstein']
    
    if datetime.datetime.weekday(datetime.datetime.now()) > 4:
        telegram_send.send(conf = gitpath + '/.telconfigs/configuration', messages=['Nothing new today! \nHave a nice weekend ;)'])
    else:
        for f in fields:
            pfb.send_telegram(wrds, field=f)
            pfb.find_authors(author_list, field=f)

if __name__ == '__main__':
    main()