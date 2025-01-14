#parse page text for first link

#for a list of pages: https://en.wikipedia.org/wiki/Special:AllPages
#entire dump is https://dumps.wikimedia.org/enwiki/20141008/
"""
1. article body via xml tag
2. clean tags: <ref>, <div>
3. clean Media wiki templates {{ }}
5. disregard parenthesis, not embedeed in links
6. find first link 
    * elimanting outermost false links:
        *Image, wiktionary etc.
"""
import xml.etree.ElementTree as ET

#first level of hierachy is check whether {{}}
    #proceed to ()
    #then test link
    #link

def inside_char(char, marker, tracker, i):
    #checks whether inside char such as parentheses or wiki_template
        #handles nested 
    if char == marker[0]:
        tracker.append(i)
    elif char == marker[1]:
        try:
            tracker.pop()
        except IndexError:
            pass
    return tracker
        
def grab_links(body):
    #returns list of outer-most links not in parentheses or template or tags
    links = []
    link_char = []
    
    w_marker = ["{{", "}}"]
    w_temp = [] #in template?
    
    par_marker = ["(", ")"]
    par = [] #in parentheses?
    
    rtag_marker = ["<ref", "</re"]
    rtag = [] #in <ref> tag?
    
    dtag_marker = ["<div", "</di"]
    dtag = []
    
    skip_char = []
    
    for i, c in enumerate(body):
        if i in skip_char: continue #eliminates double counting
        char = body[i:i+2]
        tag = body[i:i+4]
        
        #wiki template
        w_temp = inside_char(char, w_marker, w_temp, i)
        if char in w_marker: skip_char.append(i+1)
        if w_temp:
            continue #doesn't process if inside wiki template
        
        #parentheses
        par = inside_char(c, par_marker, par, i)
        if par:
            continue
        
        #<ref> or <div>
        rtag = inside_char(tag, rtag_marker, rtag, i)
        dtag = inside_char(tag, dtag_marker, dtag, i)
        if rtag or dtag:
            continue
        
        #clear to add outer-most link
        if char == '[[':
            link_char.append(i)
        elif char == ']]' and len(link_char) == 1:
            links.append(body[link_char[0]:i+2])
            link_char.pop()
        elif char == ']]' and len(link_char) > 1:
            link_char.pop()
    return links

def check_link(link):
    #filter links to images or files
    #returns false if for a bad link
        #includes links begining with colon
    false_links = ["wikipedia:", "w:", "wikitionary:", "wikt:", "wikinews:",
                    "n:", "wikibooks:", "b:", "wikiquote:", "q:", "wikisource:",
                    "s:", "wikispecies:", "species:", "wikiversity", "v:", 
                    "wikivoyage:", "voy:", "wikimedia:", "foundation:", "wmf:", 
                    "commonds:", "c:", "chapter:", "metawikipedia:", "meta:", 
                    "m:", "incubator:", "outreach:", "mw:", "mediazilla:", 
                    "bugzilla:", "testwiki:", "wikitech:", "wikidata:", "d:",
                    "phabricator:", "phab:", "talk:", "user talk:", "file:", 
                    "user:", "template:", "category:", "file talk:", 
                    "category talk:", "image:", "media:", "special:", 
                    "help:", "portal:", "portal talk:", "\#"]
    is_bad = any(false_link in link.lower() for false_link in false_links)
    if is_bad or link[0] == ":":
        return False
    else:
        return True


def clean_link(link):
    #strips brackets, returns link destination (not display name)
    link = link.strip("[]")
    if "|" in link:            
        link = link.split("|",1)[0]
    link = link.strip() #remove trailing white space
    return link 

def run_parser(page_xml):
    links = grab_links(page_xml)
    for link in links:
        if check_link(link):
            return clean_link(link)
    return None

