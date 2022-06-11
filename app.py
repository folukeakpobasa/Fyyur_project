#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (Flask, render_template, request, Response, flash, 
      redirect, url_for, abort)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
  
    # missing fields
    show = db.relationship('Show', backref='venue', lazy=True, cascade='save-update')
    website_link = db.Column(db.String(150))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    
    def __repr__(self):
          return f'<Venue{self.id} {self.name}>'
    


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # missing fields
    website_link = db.Column(db.String(150))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(700))
    show = db.relationship('Show', backref='artist', lazy=True, cascade='save-update')
    
    def __repr__(self):
          return f'<Artist{self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self):
          return f'<Show{self.id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data = []
  venues = Venue.query.all()
  areas =  Venue.query.distinct(Venue.city, Venue.state).all()
  
  for area in areas:
        
        data.append({
          'city': area.city,
          'state': area.state,
          'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.show if show.start_time >datetime.now()])
          }for venue in venues if
                venue.city == area.city and venue.state==area.state]    
    
        })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
      '''display venues that matches the search term'''
      search_term = request.form.get('search_term', '')
      venues= db.session.query(Venue).filter(Venue.name.ilike('search_term'))
      matching_venues = []
      
      for venue in venues:
            no_upcoming_shows = []
            for show in venue.show:
                  if show.start_time >datetime.now():
                        no_upcoming_shows.append(show)
            matching_venue.append({
              "id": venue.id,
              "name": venue.name,
              "no_upcoming_shows": no_upcoming_shows
              })
      count = len(list(venues))
      response = {
        "count": count,
        "data": matching_venues
      }
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
      '''Dispaly venue details for a given id'''
      venue = Venue.query.get_or_404(venue_id)
      
      upcoming_shows = []
      past_shows = []
      
      for show in venue.show:
            show_details = {
              'artist_id': show.artist_id,
              'artist_name': show.artist_name,
              'artist_image_link': show.artist_image_link,
              'start_time': show.start_time.strftime("%m/%d/%y, %H:%M")
            }
            if datetime.now() >= start_time.strftime:
                  past_shows.append(show_details)
            else:
                  upcoming_shows.append(show_details)
    
      
      data = vars(venue)
      
      
      data['upcoming_shows'] = upcoming_shows
      data['past_shows'] = past_shows
      data['upcoming_shows_count'] = len(upcoming_shows)
      data['past_shows_count'] = len(past_shows)
      return render_template('pages/show_venue.html', venue=data)
            

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.data)
  try:
    venue = Venue(name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data, 
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data, 
      seeking_talent = form.seeking_talent.data, 
      seeking_description = form.seeking_description.data,
    )
      
    db.session.add(venue)
    db.session.commit()
    flash('An error occcured. Venue' + request.form['name'] + ' was successfully listed.')
    # print(sys.exec_info())
  except:
    flash('An error occurred' + data.name + 'could not be created!')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(venue_id=venue_id).first()
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  ''' display the name and id all the artists'''
  
  artists = db.session.query(Artist).all()
  data = []
  
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artists.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
      
      '''display artists that matches the search term'''
      search_term = request.form.get('search_term', '')
      artists= db.session.query(Artist).filter(Artist.name.ilike('search_term'))
      matching_artists = []
      
      for artist in artists:
            no_upcoming_shows = []
            for show in artist.show:
                  if show.start_time >datetime.now():
                        no_upcoming_shows.append(show)
            matching_artists.append({
              "id": artist.id,
              "name": artist.name,
              "no_upcoming_shows": no_upcoming_shows
              })
      count = len(list(artists))
      response = {
        "count": count,
        "data": matching_artists
      }
      return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
      '''Dispaly venue details for a given id'''
      artists = Artist.query.filter_by(artist_id=artist_id)
      upcoming_shows = []
      past_shows = []
      
      for show in artist.shows:
            show_details = {
              'venue_id': show.artist_id,
              'venue_name': show.artist_name,
              'venue_image_link': show.artist_image_link,
              'start_time': show.start_time.strftime("%m/%d/%y, %H:%M")
            }
            if datetime.now() >= start_time.strftime:
                  past_shows.append(show_details)
            else:
                  upcoming_shows.append(show_details)
      past_shows_count = len(past_shows)
      upcoming_shows_count = len(upcoming_shows.len)
      
      data = dict(venue)
      
      data['upcoming_shows'] = upcoming_shows
      data['past_shows'] = past_shows_count
      data['past_shows_count'] = upcoming_shows_count
      
      return render_template('pages/show_artist.html', artist=data)
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(object=artist)
  
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
      form = ArtistForm(request.form)
      artist = Artist.query.get_or_404(venue_id)
      
      if form.validate():
            artist.name = form.name.data,
            artist.city = form.city.data,
            artist.state = form.state.data,
            artist.address = form.address.data, 
            artist.phone = form.phone.data,
            artist.image_link = form.image_link.data,
            artist.facebook_link = form.facebook_link.data,
            artist.website_link = form.website_link.data, 
            artist.seeking_venue = form.seeking_venue.data, 
            artist.seeking_description = form.seeking_description.data,
      try:
        artist = Artist(name = form.name.data,
                      city = form.city.data,
                      state = form.state.data,
                      address = form.address.data, 
                      phone = form.phone.data,
                      image_link = form.image_link.data,
                      facebook_link = form.facebook_link.data,
                      website_link = form.website_link.data, 
                      seeking_venue = form.seeking_venue.data, 
                      seeking_description = form.seeking_description.data,
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue' + request.form['name'] + ' was successfully created!')
      except:
        flash('An error occurred' + data.name + 'could not be created!')
        db.session.rollback()
      finally:
        db.session.close()
      
      return redirect(url_for('show_venue', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(artist_id)
  form = VenueForm(object=artist)
  
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
      form = VenueForm(request.form)
      venue = Venue.query.get_or_404(venue_id)
      
      if form.validate():
            venue.name = form.name.data,
            venue.city = form.city.data,
            venue.state = form.state.data,
            venue.address = form.address.data, 
            venue.phone = form.phone.data,
            venue.image_link = form.image_link.data,
            venue.facebook_link = form.facebook_link.data,
            venue.website_link = form.website_link.data, 
            venue.seeking_talent = form.seeking_talent.data, 
            venue.seeking_description = form.seeking_description.data,
      try:
        venue = Venue(name = form.name.data,
                      city = form.city.data,
                      state = form.state.data,
                      address = form.address.data, 
                      phone = form.phone.data,
                      image_link = form.image_link.data,
                      facebook_link = form.facebook_link.data,
                      website_link = form.website_link.data, 
                      seeking_talent = form.seeking_talent.data, 
                      seeking_description = form.seeking_description.data,
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue' + request.form['name'] + ' was successfully created!')
      except:
        flash('An error occurred' + data.name + 'could not be created!')
        db.session.rollback()
      finally:
        db.session.close()
      
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
      form = ArtistForm(request.data)
      try:
        artist = Artist(name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data, 
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data, 
        seeking_venue = form.seeking_venue.data, 
        seeking_description = form.seeking_description.data,
        )
      
        db.session.add(venue)
        db.session.commit()
        flash('An error occcured. Artist' + request.form['name'] + ' was successfully listed.')
        # print(sys.exec_info())
      except:
        flash('An error occurred' + data.name + 'could not be created!')
        db.session.rollback()
      finally:
        db.session.close()
      return render_template('pages/home.html')
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      ''' displays list of shows at /shows '''
      data = []
      show_list = db.session.query(Show).all()
      for show in show_list:
            data.append({
              'venue_id': show.venue_id,
              'venue_name': show.venue_name,
              'artist_id': show.artist_id,
              'artist_name': show.artist_name,
              'artist_image_link': show.artist_image_link,
              'start_time': show.start_time
            })
      return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
      form = ShowForm(request.data)
      if form.validate():
            try:
              show = Show(name = form.name.data,
                        Venue_name= form.venue_name.data,
                        artist_id = form.artist_id.data,
                        address = form.address.data, 
                        artist_image_link = form.artist_image_link.data,
                          start_time = form.start_time.data                       
              )
  
              db.session.add(show)
              db.session.commit()
              flash('Show' + request.form['venue_name'] + ' was successfully listed!')
            except:
              flash('An error occurred' + data.name + 'could not be listed!')
              db.session.rollback()
            finally:
              db.session.close()
      return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
