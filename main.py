"""`main` is the top level module for your Flask application."""

#Import request to request data from client server
from flask import Flask, render_template, request, session, json
from datetime import datetime
#Import for lumberjacking 
import logging, urllib2

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

#This key is a secret.
app.secret_key = 'ServerDev_Assign1_140522J_AlmedaGlenn'

wordlist = ['BOAST', 'TIGHT', 'BATON', 'TOXIC', 'WORDS', 'PIZZA', 'SEEDS', 'FAILS', 'GREAT', 'REAPS', 'SHOOT', 'CLEAR', 'COLOR', 'FILES', 'QUEEN', 'KINGS', 'CHIEF']

def totalSessionCount():
	session['game_answer'] = ""				#the current game's answer here
	session['current_word_state'] = ""		#the current game's word state
	session['current_bad_guesses'] = 0		#the current game's bad guess count
	session['player_games_won'] = 0			#the current games won by player
	session['player_games_lost'] = 0		#the current games lost by player

#default path
@app.route('/')
#alternate default path
@app.route('/home')
def home():
	#activate the session
	totalSessionCount()
   #Renders the home page.
	return render_template('index.html')
	
	
@app.route('/new_game', methods = ['POST'])
def new_game():
	totalSessionCount()
	request_for_url = urllib2.Request('http://randomword.setgetgo.com/get.php')
	response = urllib2.urlopen(request_for_url)
	
	answer_in_string = (response.read()).upper()
	answer = len(answer_in_string)
	session['game_answer'] = answer_in_string
	
	blanks = ""
	for i in range(0, answer):
		blanks += "_"
	session['current_word_state'] = blanks	
	
	list_of_letters = {}
	list_of_letters.update({"word_length": answer})
	word_to_be_guessed = json.dumps(list_of_letters)	#send the data to client
	
	#For your lumberjacking information :3
	logging.info(word_to_be_guessed)
	logging.info(session['game_answer'])
	logging.info(session['current_word_state'])
	
	return word_to_be_guessed

@app.route('/check_letter', methods = ['POST'])
def check_letter():
	
	#this is a request body
	letter_guessed = json.loads(request.data)
	#Don't forget to check which tree you felled!
	logging.info(letter_guessed['guess'])
	
	#This is the answer in string format
	answer_in_string = list(session['game_answer'])
	
	#The length of the answer, numerically
	length_answer = len(session['game_answer'])
	
	#The current state of the game
	temp_word_state = list(session['current_word_state'])
	
	guess_Correctly = False
	
	#Let's begin the check
	for i in range(0, length_answer):
		#if the letter matches
		if answer_in_string[i] == letter_guessed['guess']:
			temp_word_state[i] = letter_guessed['guess']	#swap the blank out for the letter
			guess_Correctly = True
		elif(i == length_answer-1 and guess_Correctly == False): #in other words, he guessed wrongly
			session['current_bad_guesses'] += 1			#increment the bad guess count
	
	#join them altogether
	session['current_word_state'] = "".join(temp_word_state)
	
	#Don't forget to check which tree you felled!
	logging.info(session['current_word_state'])
	logging.info(session['game_answer'])
	
	if session['current_bad_guesses'] <= 7:
		#The game is ONGOING
		if(session['current_word_state'] != session['game_answer']):
			#the container meant for the current state of the game
			current_game_state = {}
			current_game_state.update({'game_state': "ONGOING"})
			current_game_state.update({'word_state': session['current_word_state']})
			current_game_state.update({'bad_guesses': session['current_bad_guesses']})
			the_current_state = json.dumps(current_game_state)
			return the_current_state
		
		#The game is WON
		else:
			session['player_games_won'] += 1	#add to the win count
			
			#Update the status to win
			#the container meant for the current state of the game
			current_game_state = {}
			current_game_state.update({'game_state': "WIN"})
			current_game_state.update({'word_state': session['current_word_state']})
			the_current_state = json.dumps(current_game_state)
			return the_current_state
	
	#he loses the game if any of those conditions above doesn't match
	if session['current_bad_guesses'] >= 8:
		session['player_games_lost'] += 1	#add to the win count
		
		#Update the status to lose
		#the container meant for the current state of the game
		current_game_state = {}
		current_game_state.update({'game_state': "LOSE"})
		current_game_state.update({'word_state': session['current_word_state']})
		current_game_state.update({'answer': session['game_answer']})
		the_current_state = json.dumps(current_game_state)
		return the_current_state
	
@app.route('/score', methods=['GET', 'DELETE'])
def score():
	
	if request.method == 'GET':
		total_games_played = {}
		total_games_played.update({'games_won': session['player_games_won']})
		total_games_played.update({'games_lost': session['player_games_lost']})
		score = json.dumps(total_games_played)
	
	elif request.method == 'DELETE':
		session['player_games_won'] = 0
		session['player_games_lost'] = 0
		total_games_played = {}
		total_games_played.update({'games_won': session['player_games_won']})
		total_games_played.update({'games_lost': session['player_games_lost']})
		score = json.dumps(total_games_played)
		
	return score