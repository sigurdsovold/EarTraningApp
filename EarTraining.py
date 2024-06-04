import random
import threading
import time
import mido
from soundmodule import midi_to_frequency, create_note, generate_chord
import numpy as np
import os
import shutil
from scipy.io import wavfile
import pygame

# Class that manages the ear training game
class EarTrainingGame:
    
    # Mapping solfege syllables to corresponding MIDI notes in C major scale
    solfege_to_midi = {
        'do': 60, 'ra': 61, 're': 62, 'me': 63, 'mi': 64,
        'fa': 65, 'fi': 66, 'sol': 67, 'le': 68, 'la': 69,
        'te': 70, 'ti': 71
    }

    # Mapping musical keys to their MIDI note adjustments
    key_to_adjustment = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 2, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': -6, 'G': -5, 'G#': -4,
        'Ab': -4, 'A': -3, 'A#': -2, 'Bb': -2, 'B': -1
    }

    # Difficulty settings for various levels
    settings_easy = {
        "number_of_notes": 2.0,
        "octave_range": 1.0,
        "duration": 2.0
    }

    settings_medium = {
        "number_of_notes": 3.0,
        "octave_range": 1.0,
        "duration": 1.5
    }

    settings_hard = {
        "number_of_notes": 5.0,
        "octave_range": 2.0,
        "duration": 1.0
    }

    settings_impossible = {
        "number_of_notes": 16.0,
        "octave_range": 3.0,
        "duration": 0.5
    }

    settings_custom = {
        "number_of_notes": 7.0,
        "octave_range": 1.0,
        "duration": 0.5
    }



    # MIDI note sequences for various musical modes based on the C major scale
    modes = {
        "Ionian": [60, 62, 64, 65, 67, 69, 71],  # C D E F G A B
        "Dorian": [60, 62, 63, 65, 67, 69, 70],  # C D Eb F G A Bb
        "Phrygian": [60, 61, 63, 65, 67, 68, 70],  # C Db Eb F G Ab Bb
        "Lydian": [60, 62, 64, 66, 67, 69, 71],  # C D E F# G A B
        "Mixolydian": [60, 62, 64, 65, 67, 69, 70],  # C D E F G A Bb
        "Aeolian": [60, 62, 63, 65, 67, 68, 70],  # C D Eb F G Ab Bb (Natural Minor)
        "Locrian": [60, 61, 63, 65, 66, 68, 70],  # C Db Eb F Gb Ab Bb
        # More modes defined similarly...
        "Melodic Minor": [60, 62, 63, 65, 67, 69, 71],
        "Dorian b2": [60, 61, 63, 65, 67, 69, 71],
        "Lydian Augmented": [60, 62, 64, 66, 68, 69, 71],
        "Lydian Dominant": [60, 62, 64, 66, 67, 69, 70],
        "Mixolydian b6": [60, 62, 64, 65, 67, 68, 70],
        "Locrian #2": [60, 62, 63, 65, 66, 68, 70],
        "Altered Scale": [60, 61, 63, 64, 66, 68, 70],
        "Chromatic": [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
        "Whole": [60, 62, 64, 66, 68, 70],
        "Major Penta": [60, 62, 64, 67, 69],
        "Minor Penta": [60, 63, 64, 67, 70],
        "Custom": []
    }
    
    gamepoints = 0.0
    required_gamepoints = 4.0
    level_up_scalar = 1.1
    parameter_scalar = 1.3
    current_level = 0
    user_guesses = []
    difficulty = settings_custom
    mode = modes["Minor Penta"]
    key = key_to_adjustment["C"]
    midi_test_notes = ""
    pre_octave_key_list = ""
    midi_test_notes_list = []
    detailed_match = []
            
    def __init__(self):
        self.user_guesses = []  # List to store user guesses
        self.elapsed_time = 0.0  # Track elapsed time since the game started
        self.running = False  # Game state indicator
        self.lock = threading.Lock()  # Lock for thread-safe operations

    def start_game(self):
        """Start the game clock in a separate thread."""
        self.running = True
        self.thread = threading.Thread(target=self._game_clock)  # Removed daemon=True
        self.thread.start()
        self.user_guesses = []
        self.generate_reference_cadence()
        self.midi_test_notes, self.pre_octave_key_list = self.generate_test_sequence()

    def play_audio(self):
        print("trying to play")
        pygame.mixer.init()  # Initialize the mixer module
        pygame.mixer.stop()  # Stop any currently playing sounds
        directory = "test_file_folder"
        audio_file = os.listdir(directory)[0]  # Get the only file in the directory
        full_path = os.path.join(directory, audio_file)
        sound = pygame.mixer.Sound(full_path)
        sound.play()


    def stop_game(self):
        """Stop the game clock."""
        self.running = False
        self.thread.join()  # Wait for the game clock thread to finish
        self.clear_folder()

    def _game_clock(self):
        """Private method to update the game clock."""
        update_counter = 0  # Initialize a counter to track the number of updates
        try:
            while self.running:
                with self.lock:
                    self.elapsed_time += 1/60  # Increment time in seconds
                time.sleep(1/60)  # Sleep to maintain the 60 Hz update rate

                update_counter += 1  # Increment the update counter
                if update_counter == 60:  # Check if 1 second has passed
                    # self.notify_gui()  # Call GUI update method only once per second
                    update_counter = 0  # Reset counter after updating
        except Exception as e:
            print(f"An error occurred: {e}")

    def notify_gui(self):
        """Notify GUI with the current game state."""
        print(f"Elapsed Time: {self.elapsed_time:.2f} seconds, Guesses: {self.user_guesses}")

    def add_user_guess(self, solfege):
        """Add a solfege syllable to the user guesses list."""
        with self.lock:
            self.user_guesses.append(self.solfege_to_midi[solfege])
        # self.notify_gui()  # Update GUI after adding a guess

    def remove_user_guess(self):
        """Remove the last solfege syllable from the user guesses list."""
        with self.lock:
            if self.user_guesses:
                self.user_guesses.pop()
        # self.notify_gui()  # Update GUI after removing a guess

    def notify_gui(self):
        """Notify GUI with the current game state."""
        print(f"Elapsed Time: {self.elapsed_time:.2f} seconds, Guesses: {self.user_guesses}")

    def process_user_solfege_selections(selected_indices):
    # All possible solfege syllables in a chromatic scale from 'do' to 'ti'
        all_solfege = [
            'do', 'ra', 're', 'me', 'mi',
            'fa', 'fi', 'sol', 'le', 'la',
            'te', 'ti'
        ]
        
        # Initialize the interface list with zeros
        interface_list = [0] * len(all_solfege)
        
        # Mark the selected indices in the interface list
        for index in selected_indices:
            interface_list[index] = 1
        
        # Collect the syllables corresponding to selected indices
        result_syllables = [all_solfege[i] for i in range(len(interface_list)) if interface_list[i] == 1]
        
        return result_syllables


    def generate_silence(self, duration, sample_rate=44100):
        return np.zeros(int(duration * sample_rate), dtype=np.int16)

    def list_to_audiofile(self, midi_test_notes_list, folder_name="test_file_folder", silence_duration=1.0):
        folder_name = "test_file_folder"

        chord_root_note = self.key + 60
        chord_waveform = generate_chord(chord_root_note, 2, self.mode, sample_rate=44100)
        duration = self.difficulty["duration"]
        print(midi_test_notes_list)
        concatenated_waveform = np.array([], dtype=np.int16)
        for midi_note in midi_test_notes_list:
            frequency = midi_to_frequency(midi_note)
            note_waveform = create_note(frequency, duration)
            concatenated_waveform = np.concatenate((concatenated_waveform, note_waveform))
        
        # Append silence between chord and test sequence
        silence_waveform = self.generate_silence(silence_duration)
        final_waveform = np.concatenate((chord_waveform, silence_waveform, concatenated_waveform))

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        filename = os.path.join(folder_name, "_".join(map(str, midi_test_notes_list)) + "_audiofile.wav")
        wavfile.write(filename, 44100, final_waveform)
        return filename

    def string_to_list(self, midi_test_notes):
        midi_test_notes_list = [int(note) for note in midi_test_notes.split('_')]
        return midi_test_notes_list
    
    def clear_folder(self):
        folder = 'test_file_folder'
        if not os.path.exists(folder):
            os.makedirs(folder)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def generate_test_sequence(self):
        
        self.clear_folder()
        
        number_of_notes = int(self.difficulty["number_of_notes"])
        octave_range = int(self.difficulty["octave_range"])
        
        """Generate a sequence of MIDI notes based on given parameters."""
        midi_sequence = [random.choice(self.mode)]  # Start sequence with a random note

        # Generate remaining notes ensuring no immediate repetitions
        while len(midi_sequence) < number_of_notes:
            next_note = random.choice([note for note in self.mode if note != midi_sequence[-1]])
            midi_sequence.append(next_note)

        pre_octave_key_list = midi_sequence.copy()  # Copy sequence before applying octave adjustments
        self.pre_octave_key_list = midi_sequence.copy()
        print(self.pre_octave_key_list)
        
        
        # Apply random octave adjustments
        octave_adjustments = [random.randint(1, int(octave_range))]  # Ensure initial octave is an integer
        for _ in range(1, int(number_of_notes)):
            if octave_adjustments[-1] == 1:
                try:
                    octaves = [octave for octave in range(1, int(octave_range+1)) if octave != octave_adjustments[-1]]
                    next_octave = 1 if random.random() < 0.75 else int(random.choice(octaves))
                except IndexError:
                    next_octave = 1  # Default to 1 if list is empty
            else:
                next_octave = int(random.choice([octave for octave in range(1, int(octave_range+1)) if octave != octave_adjustments[-1]]))
            octave_adjustments.append(next_octave)

        print("Printing Mode:" + str(self.mode))

        notes_plus_octave = [(note + (octave - 1) * 12) for note, octave in zip(midi_sequence, octave_adjustments)]  # Apply octave adjustments
        adjusted_notes = [note + self.key for note in notes_plus_octave]  # Apply key adjustment

        midi_test_notes = "_".join(map(str, adjusted_notes))  # Convert note list to a string
        self.midi_test_notes = "_".join(map(str, adjusted_notes))
        
        
        midi_test_notes_list= self.string_to_list(midi_test_notes)
        print("printing midi_test_notes_list", midi_test_notes_list)

        self.list_to_audiofile(midi_test_notes_list, self.difficulty["duration"])

        self.play_audio()

        return midi_test_notes, pre_octave_key_list

      
    
    
    def restart_game(self):
        self.user_guesses = []
        self.generate_reference_cadence()

        self.midi_test_notes, self.pre_octave_key_list = self.generate_test_sequence()
        print("Generated MIDI Test Notes:", self.midi_test_notes)
        print("Pre-Octave List:", self.pre_octave_key_list)
        return

    def generate_reference_cadence(self):
        """Generate a reference cadence based on a given key."""
        key_note = self.solfege_to_midi['do'] + self.key  # Calculate the base note of the key
        dominant = (key_note - 5, key_note - 1, key_note + 2)  # Calculate dominant chord notes
        tonic = (key_note, key_note + 4, key_note + 7)  # Calculate tonic chord notes
        return {'dominant': dominant, 'tonic': tonic}  # Return both chords as a dictionary
    
        # Function to validate user input against a pre-generated MIDI sequence
    def validate_user_input(self):
        # Check if the entire user input list matches the pre-generated list
        overall_match = 1 if self.pre_octave_key_list == self.user_guesses else 0
        
        # Check for individual note matches
        detailed_match = [1 if self.pre_octave_key_list[i] == self.user_guesses[i] else 0 for i in range(len(self.pre_octave_key_list))]
        self.detailed_match = detailed_match
        
        # Calculate the percentage of correct notes
        print(str(self.pre_octave_key_list))
        correct_percentage = sum(detailed_match) / len(self.pre_octave_key_list)
        
        local_gamepoints = self.gamepoints
        
        # Calculate game points based on the percentage of correct notes
        if correct_percentage < 0.7:
            local_gamepoints += 0
            self.gamepoints += 0
        elif correct_percentage == 1.0:
            local_gamepoints += 1.3  # Bonus points for 100% correctness
            self.gamepoints += 1.3
        else:
            local_gamepoints += correct_percentage  # Points are the same as the correctness percentage
            self.gamepoints += correct_percentage
            
        self.check_for_level_up()

        return overall_match, detailed_match, local_gamepoints
    

    def level_up(self):
        
        self.current_level += 1
        
        self.difficulty["octave_range"] = self.difficulty["octave_range"]*self.parameter_scalar
        self.difficulty["duration"] = self.difficulty["duration"]/self.parameter_scalar
        self.difficulty["number_of_notes"] = self.difficulty["number_of_notes"]*self.parameter_scalar
        
        # Optional: print the current state of the dictionary
        # print(self.difficulty)
        # print("LEVEL UP!")
        
        self.gamepoints -= self.required_gamepoints
        self.required_gamepoints *= self.level_up_scalar

    def check_for_level_up(self):
        if self.gamepoints > self.required_gamepoints:
            self.level_up()
            
    def get_number_of_notes(self):
        return (int(self.difficulty.get("number_of_notes")))
    
    def get_detailed_match(self):
        return self.detailed_match
    
    def get_pre_octave_key_list(self):
        return self.pre_octave_key_list
    
    def set_mode(self, mode):
        print("trying to set mode")
        try:
            # Check if the mode exists in the self.modes dictionary
            print("trying to change mode")
            if mode in self.modes:
                self.mode = self.modes.get(mode)
                print("changed mode to " + str(mode))
        except KeyError:
            # Proper handling of KeyError if mode is not found in the dictionary
            print("error: invalid mode")
            
    def set_difficulty(self, chosen_difficulty):
        if chosen_difficulty == "Easy":
            self.difficulty = self.settings_easy
        elif chosen_difficulty == "Medium":
            self.difficulty = self.settings_medium
        elif chosen_difficulty == "Hard":
            self.difficulty = self.settings_hard
        elif chosen_difficulty == "Impossible":
            self.difficulty = self.settings_impossible
            
    
    
def play_midi_note(self, output, note, duration):
        duration = self.difficulty["duration"]
        
        """Play a single MIDI note for a specified duration in milliseconds.
        
        Args:
        output: The MIDI output port to send messages.
        note: The MIDI note number to play.
        duration: How long the note should sound, in milliseconds.
        """
        output.send(mido.Message('note_on', note=note))
        time.sleep(duration / 1000.0)  # Convert milliseconds to seconds
        output.send(mido.Message('note_off', note=note))


def play_chord(output, chord, duration):
    """Play a chord (multiple notes simultaneously) for a specified duration.
    
    Args:
    output: The MIDI output port to send messages.
    chord: A tuple containing MIDI notes that make up the chord.
    duration: How long the chord should sound, in milliseconds.
    """
    for note in chord:
        output.send(mido.Message('note_on', note=note))
    time.sleep(duration / 1000.0)
    for note in chord:
        output.send(mido.Message('note_off', note=note))

def midi_test_notes(self, midi_test_notes, dominant, tonic, note_duration, interlude_duration):
    """Play a sequence of two chords followed by a melody.
    
    Args:
    midi_test_notes: A string with MIDI notes separated by underscores (e.g., "62_65_64").
    dominant: A tuple representing the dominant chord to be played.
    tonic: A tuple representing the tonic chord to be played.
    note_duration: Duration for each note or chord in milliseconds.
    interlude_duration: Milliseconds to wait between the chord section and the melody section.
    """

    midi_test_notes = self.midi_test_notes
    dominant = self.dominant["dominant"]
    tonic = self.tonic["tonic"]
    note_duration = self.difficulty["duration"]
    interlude_duration = 1000

    output = mido.open_output()  # Open the default MIDI output
    
    # Play the dominant chord
    play_chord(output, dominant, note_duration)
    
    # Wait before playing the tonic chord
    time.sleep(note_duration / 1000.0)  # Ensure there is a break between chords
    
    # Play the tonic chord
    play_chord(output, tonic, note_duration)
    
    # Wait between chords and midi test notes
    time.sleep(interlude_duration / 1000.0)
    
    # Play the midi test notes
    for note in map(int, midi_test_notes.split('_')):
        play_midi_note(output, note, note_duration)
    
    output.close()


	
def main():
    game = EarTrainingGame()  # Create an instance of the game
    game.start_game()  # Start the game clock


    try:
        # Generate and print the initial test sequence and reference cadence
        game.restart_game()
        
        while True:
            user_input = input("Type your solfege guess ('exit' to quit, 'remove' to undo last guess): ").strip().lower()
            if user_input == 'exit':
                break  # Exit the game loop
            elif user_input == 'remove':
                if game.user_guesses:
                    game.remove_user_guess()  # Remove the last guess
                print(f"Current Guesses: {game.user_guesses}")
            elif user_input in game.solfege_to_midi.keys():
                game.add_user_guess(user_input)  # Add user guess
                print(f"Current Guesses: {game.user_guesses}")
            else:
                print("Not a valid solfege input.")
            
            # Check if the number of user guesses matches the length of the sequence
            if len(game.user_guesses) == len(game.pre_octave_key_list):
                overall_match, detailed_match, gamepoints = game.validate_user_input(game.pre_octave_key_list)
                # print("Overall Match:", overall_match)
                # print("Detailed Match:", detailed_match)
                # print("Gamepoints: ", gamepoints)
                # Reset for next round or expand functionality to continue with new sequence
                game.restart_game()
    finally:
        game.stop_game()  # Ensure the game stops its clock

if __name__ == "__main__":
    main()
