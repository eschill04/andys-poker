from flask import Flask, request
from flask_socketio import SocketIO, emit
from game_logic import Game  # Assuming this contains your game's logic

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

game = Game()  # Your game state
players = {}  # Map from sid to username

@socketio.on('join')
def on_join(data):
    if game.started:
        emit('join_failure', {'reason': 'game_started'}, room=request.sid)
        return
    
    username = data['username']
    # Add player to the game
    if username in game.players:
        emit('join_failure', {'reason': 'username_taken'}, room=request.sid)
        return
    
    game.add_player(username)
    players[request.sid] = username
    print(f'{username} joined the game')
    print(f'Current players: {game.players}')
    emit('join_success', {'username': username})
    emit('update_players', game.players, broadcast=True)
    # Check if game can start and emit game start event
    if game.can_start():
        emit('game_can_start', broadcast=True) # maybe no state here?

@socketio.on('start')
def on_start_game():  
    emit('game_start', broadcast=True)
    print("Game started")
    game.start()

    # In a turn: deal cards to everyone. game.deal_cards() gives everyone cards
        # Emit event to deal cards to everyone
    # Then, wait till everyone makes a bet. game.make_bet(username, bet) gives a player a bet
        # Wait for 'bet' event from everyone
    # Then, determine winner of round. game.update_scores() gives everyone their new scores
        # Emit event to show winner of round

@socketio.on('leave')
def on_leave(username):
    username = username['userName']
    game.remove_player(username)
    print(f'{username} left the game')
    print(f'Current players: {game.players}')
    emit('update_players', game.players, broadcast=True)
    emit('leave_success')

@socketio.on('bet')
def on_bet(data):
    username = data['username']
    bet = data['bet']
    direction = data['direction']
    game.make_bet(username, bet, direction)
    print(f'{username} made a {direction} bet of {bet}')

    if game.all_bets_in():
        print("All bets are in")
        data = game.update_scores()  # Determine winners of the round

        emit('round_ended', data, broadcast=True)

        # # If the game is not over, start a new round
        # if not game.is_game_over():
        #     game.start_new_round()
        #     emit('new_round', game.get_state(), broadcast=True)
        # else:
        #     emit('game_over', {'scores': game.get_scores()}, broadcast=True)

@socketio.on('rounds')
def on_rounds(data):
    rounds = data['numRounds']
    print(f'Setting rounds to {rounds}')
    game.set_rounds(rounds)
    emit('num_rounds', rounds, broadcast=True)
    for sid in players:
        hand = game.deal_cards(players[sid])
        print(players[sid], hand)
        emit('deal_cards', {"hand": hand, "rounds_left": game.rounds_left}, room = sid)  

@socketio.on('next_round')
def on_next_round():
    for sid in players:
        hand = game.deal_cards(players[sid])
        print(players[sid], hand)
        emit('deal_cards', {"hand": hand, "rounds_left": game.rounds_left}, room = sid)    # Assuming this method returns the cards for each player

@socketio.on('get_money') 
def on_get_money():
    money = game.distribute_money()
    emit('money', money, broadcast=True)

@socketio.on('end_game')
def on_end_game():
    game.reset_game()
    emit('game_ended', broadcast=True)

@socketio.on('wild_card_select')
def on_wild_card_select(data):
    new_hand = game.replace_wild(data['username'], data['new'], data['old'])
    print(data['username'], "replaced card", data['old'], "with", data['new'])
    print(new_hand)
    emit('wild_card_replaced', new_hand)

# More event handlers

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5001, debug=True)
