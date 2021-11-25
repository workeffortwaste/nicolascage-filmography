import tmdbsimple as tmdb
import json
import datetime
import os

def parse_date(datestr):
    return datetime.datetime.strptime(datestr, '%Y-%m-%d')

def get_films(request):
    tmdb.API_KEY = os.environ.get('TMDB_API_KEY')
    cast = 2963  # Nicolas Cage cast number

    discover = tmdb.Discover()
    response = discover.movie(with_cast=cast, sort_by='release_date.desc')
    results = response['results']

    if response['total_pages'] > 1:
        for x in range(2, response['total_pages'] + 1):
            response = discover.movie(
                page=x,
                with_cast=cast,
                sort_by='release_date.desc'
              )
            results = results + response['results']

    films = []
    total_runtime = 0

    for film in results:
        release_date = film.get('release_date')

        # Skip if the API has no release date information for a film
        if release_date == '' or release_date is None:
            continue

        year = release_date[:4]
        title = film.get('title')
        movie = tmdb.Movies(film['id']).info()
        runtime = movie.get('runtime')
        
        # Skip if the API has no runtime information for a film
        if runtime == '' or runtime is None or runtime is 0:
            continue

        total_runtime = total_runtime + runtime
        
        output = {
          'film': title,
          'release_date': release_date,
          'runtime': runtime,
          'year': year
          }

        films.append(output)

    headers = {
      'Cache-Control': 'public, max-age=300, s-maxage=600',
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    }

    final_output = json.dumps({'films': sorted(films, key=lambda d: parse_date(
        d['release_date']), reverse=True), 'total_runtime': total_runtime})
    
    return (final_output, 200, headers)
