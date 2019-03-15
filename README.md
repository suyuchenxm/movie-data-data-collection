
# movie-data-data-collection
Pull data from IMDB, Box office mojo, Douban and Maoyan 

This repository includes two functions files and one main file.

'functions' file includes 20 functions that could implement the proxy rotation, header rotation, requests, and get the needed
information

'combine' file includes functions that implement the data and table combination.

run the main file could implement the web scraping from 4 main data resources for movie box office analysis, they are IMDB,
Box office mojo Douban and Maoyan

the features that will be collected include:
1. the list of annual top 100 (by Gross) movies in China
2. the gross revenue for each movie
3. the budget for each movie
4. the release information for each movie: Release date, Release duration
5. the genre of each movie
6. the length of each movie
7. rating of movies from Douban

The functions dictionary could be simply imported. It's a good package for constantly pulling data from some strict websites since, in most of the case, there are web policies banning the frequent request. However, if you need other information 
some parts of the function should be modified or customized.
