Feedfilter
==========

Feedfilter removes duplicated news and news you don't like from your news-feeds.


### Filtering ###

You can create lists with topics you are (not) interested in and assignee them a values rating you interest. Like a Spam-filter news will be dismissed if their rating is above some level.

### Duplicate detection ###

Feedfilter will detect if two or more news in your feed have the same topic and will automatically remove all except the newest items and instead appended crosslinks to the duplicates in the newest item.
The threshold of the detection can be configured.

### Installation ###

Get feedfilter via git:
```
git clone https://github.com/Nudin/feedfilter.git
```

There is no Makefile yet. Just download and copy to wherever you want. You can install a translation by:
```
msgfmt po/de_DE.po --output-file /usr/share/locale/de_DE/LC_MESSAGES/feedfilter.mo 
```

### Usage ###

Call feedfilter with the feedlink (or file) as argument:
```
./feedfilter.sh http://www.domain.com/feed.rss
```
it will return the modified feed out via stdout. Feedreaders like Liferea can read feeds from stdout.

### Configuration ###

All configuration-files are located in ~/.feedfilter/ by default, the location of the config-directory can be changed with the environmental variable FEED_FILTER_CONF. The program configurations are set in the file feedfilter.conf:
```ini
[DEFAULT]
threshold = 9
title_scale = 2
cmp_threshold = 0.30
appendlvl = False
logfile = /tmp/feedfilter.log
loglevel = INFO
verboselevel = CRITICAL

[somefeed.de/foo]
treshhold = 7
```
The DEFAULT-section specifies the default configuration for all feed, alternatively or additionally you can specify different settings for single feeds. The specifier in square brackets must therefore be a substring of the url. 
The currently available options are:
 * threshold – is this value is overstepped the newsitem will be dropped
 * title_scale – multiply the values of filterscores with this factor if matched in the headline
 * cmp_threshold – The threshold at witch two texts are regarded as identical, 0 is nothing commons 1 is for fully identical news 0.3 is a good start
 * appendlvl – appended the level a note got in the filter process to every news-decryption
 * logfile – Write logs to this file
 * loglevel – How much information should be written to the logfile, if there is any
 * verboselevel – How much information should be printed to stderr
 * sitename (not in the DEFAULT-settings!) – The name for the site specific filters, if none is given it will fall back to the domainname (incl sub and tld-domain)

In the same folder you create your filterlists. The general filterlist is named 'blackwordlist.txt' additionally you can create lists named like the sitename (see above). The syntax of the filterfiles is as follows:
```
badword  2
bad word group	10
I like this  -5
```
In the fist column you specify a word or word group to search in the news, in the second a score the news gets if the word (group) is found. The columns can be separated by one tab or **multiple** spaces. Higher values will cause a news-item to be deleted quicker, negative values are allowed. Each filter can only match once in the title and one in the body of the message, scoring values for matches in the title will be multiplied by title_scale.
The search is case-insensitive **except** if the word (group) is less than 4 characters long or completely in UPPER CASE.
