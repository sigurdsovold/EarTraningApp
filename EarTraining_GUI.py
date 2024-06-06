import tkinter as tk
import EarTraining as backend
from EarTraining import EarTrainingGame
import os


class EarTrainerApp(tk.Tk):
    
    def __init__(self, backend):
        super().__init__()
        self.backend = backend  # Store the backend instance
        self.title("EarTrainer")
        self.geometry("1000x600")
        self.configure(bg='#2b2b2b')
        self.create_widgets()
        
    def start_game(self):
        # Frontend now simply calls the backend's start_game
        backend.start_game()
        self.show_game_interface()
        
    def create_widgets(self):
        self.main_frame = tk.Frame(self, bg='#2b2b2b')
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.show_main_menu()


    def create_score_display(self):
        # Create a frame for scores on the right side
        self.score_frame = tk.Frame(self.main_frame, bg='#3c3f41', padx=10)
        self.score_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Game points label
        self.game_points_label = tk.Label(self.score_frame, text=f"gamepoints: {round(backend.gamepoints, 2)}", font=('Arial', 12), bg='#3c3f41', fg='white')
        self.game_points_label.pack(pady=10)


        # Points for next level label
        self.next_level_points_label = tk.Label(self.score_frame, text=f"Required gamepoints: {round(backend.required_gamepoints, 2)}", font=('Arial', 12), bg='#3c3f41', fg='white')
        self.next_level_points_label.pack(pady=10)

        self.level_label = tk.Label(self.score_frame, text=f"Current Level : {round(backend.current_level, 2)}", font=('Arial', 12), bg='#3c3f41', fg='white')
        self.level_label.pack(pady=10)

        self.current_mode_lable = tk.Label(self.score_frame, text=("Current Mode : " + str(backend.mode)), font=('Arial', 12), bg='#3c3f41', fg='white')
        self.current_mode_lable.pack(pady=10)

        self.current_number_of_notes_lable = tk.Label(self.score_frame, text=("Number of notes : " + str(round(backend.difficulty.get("number_of_notes")))), font=('Arial', 12), bg='#3c3f41', fg='white')
        self.current_number_of_notes_lable.pack(pady=10)

        self.current_octave_lable = tk.Label(self.score_frame, text=("Current Octave : " + str(round(backend.difficulty.get("octave_range")))), font=('Arial', 12), bg='#3c3f41', fg='white')
        self.current_octave_lable.pack(pady=10)

        self.current_speed_lable = tk.Label(self.score_frame, text=("Current Speed : " + str(round(backend.difficulty.get("duration")))), font=('Arial', 12), bg='#3c3f41', fg='white')
        self.current_speed_lable.pack(pady=10)



        

    def create_button(self, master, text, command, width=20, height=2, pady=10):
        return tk.Button(master, text=text, command=command, width=width, height=height, fg='black', bg='#3c3f41', activebackground='#4b4b4b', activeforeground='black', font=('Arial', 10, 'bold'), pady=pady)

    def show_main_menu(self):
        self.clear_frame(self.main_frame)
        self.create_button(self.main_frame, "Play", self.show_tonality_screen).pack(pady=20)
        self.create_button(self.main_frame, "Stats", lambda: None).pack(pady=20)
        self.create_button(self.main_frame, "Sandbox", lambda: None).pack(pady=20)

    def show_tonality_screen(self):
        self.clear_frame(self.main_frame)
        tonalities = ["Ionian", "Aeolian", "Chromatic", "Modes"]
        for tonality in tonalities:
            self.create_button(
                self.main_frame,
                tonality,
                lambda t=tonality: (
                    backend.set_mode(t),  # Set the current mode
                    self.show_modes_screen() if t == "Modes" else self.show_difficulty_screen(t, from_modes=False)
                )
            ).pack(pady=10)
        self.create_button(self.main_frame, "Back", self.show_main_menu).pack(pady=20)

    def show_modes_screen(self):
        self.clear_frame(self.main_frame)
        self.create_button(self.main_frame, "Major Scale Modes", self.show_major_modes_screen).pack(pady=10)
        self.create_button(self.main_frame, "Melodic Minor Scale Modes", self.show_melodic_minor_modes_screen).pack(pady=10)
        self.create_button(self.main_frame, "Back", self.show_tonality_screen).pack(pady=20)

    def show_major_modes_screen(self):
        self.clear_frame(self.main_frame)
        major_modes = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]
        for mode in major_modes:
            self.create_button(
                self.main_frame, 
                mode, 
                lambda m=mode: (
                    backend.set_mode(m),
                    self.show_difficulty_screen(m, from_modes=True)
                )
            ).pack(pady=5)
        self.create_button(self.main_frame, "Back", self.show_modes_screen).pack(pady=20)

    def show_melodic_minor_modes_screen(self):
        self.clear_frame(self.main_frame)
        melodic_minor_modes = ["Melodic Minor", "Dorian b2", "Lydian Augmented", "Lydian Dominant", "Mixolydian b6", "Locrian #2", "Altered"]
        for mode in melodic_minor_modes:
            self.create_button(
                self.main_frame, 
                mode, 
                lambda m=mode: (
                    backend.set_mode(m),
                    self.show_difficulty_screen(m, from_modes=True)
                )
            ).pack(pady=5)
        self.create_button(self.main_frame, "Back", self.show_modes_screen).pack(pady=20)

    def show_difficulty_screen(self, mode_name=None, from_modes=False):
        self.clear_frame(self.main_frame)
        difficulties = ["Easy", "Medium", "Hard", "Impossible"]
        for difficulty in difficulties:
            self.create_button(
                self.main_frame,
                difficulty,
                lambda d=difficulty: (
                    backend.set_difficulty(d),
                    backend.start_game(),
                    self.show_game_interface()
                )
            ).pack(pady=10)

        back_action = self.show_modes_screen if from_modes else self.show_tonality_screen
        self.create_button(self.main_frame, "Back", back_action).pack(pady=20)


    def show_game_interface(self):
        self.clear_frame(self.main_frame)
        self.create_button(self.main_frame, "Back to Main Menu", lambda: (self.show_main_menu())).pack(pady=20)
        self.input_frame = None
        self.answer_frame = None
        self.score_frame = None
        self.setup_frames()
        self.setup_keyboard_layout()
        

    def setup_frames(self):
        # Clear existing frames if they exist
        if self.input_frame:
            self.clear_frame(self.input_frame)
            self.input_frame.pack_forget()
            self.input_frame.destroy()

        if self.answer_frame:
            self.clear_frame(self.answer_frame)
            self.answer_frame.pack_forget()
            self.answer_frame.destroy()
        
        if self.score_frame:
            self.clear_frame(self.score_frame)
            self.score_frame.pack_forget()
            self.score_frame.destroy()

        # if self.game_points_label:
        #     self.clear_frame(self.game_points_label)
        #     self.game_points_label.pack_forget()
        #     self.game_points_label.destroy()

        # if self.next_level_points_label:
        #     self.clear_frame(self.next_level_points_label)
        #     self.next_level_points_label.pack_forget()
        #     self.next_level_points_label.destroy()

        # Create new input and answer frames
        self.input_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.input_frame.pack(fill=tk.X, pady=(10, 5))

        self.answer_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.answer_frame.pack(fill=tk.X, pady=(5, 20))



        self.create_entries_and_buttons()

    def create_entries_and_buttons(self):
        self.inputs = []
        self.answers = []
        for _ in range(backend.get_number_of_notes()):  # Assuming there are 5 inputs needed
            # Frame to hold both an input and answer entry
            entry_frame = tk.Frame(self.input_frame, bg="gray", highlightbackground="black", highlightthickness=1)
            entry_frame.pack(side="left", padx=5, pady=5)

            # Create input entry
            input_entry = tk.Entry(entry_frame, width=5, font=('Arial', 12), justify='center')
            input_entry.pack(pady=(0, 5))  # Pad only below the entry
            input_entry.bind("<KeyRelease>", self.validate_inputs)  # Ensure this is properly connected
            self.inputs.append(input_entry)

            # Create answer entry
            answer_entry = tk.Entry(entry_frame, width=5, font=('Arial', 12), justify='center', state='readonly')
            answer_entry.pack(pady=(5, 0))  # Pad only above the entry
            self.answers.append(answer_entry)

        self.backspace_button = self.create_button(self.input_frame, "←", self.backspace_input, width=10, pady=0)
        self.backspace_button.pack(side=tk.LEFT, padx=(10, 0))

        self.play_button = self.create_button(self.input_frame, "Replay Audio", backend.play_audio)
        self.play_button.pack(pady=10)

        self.check_button = self.create_button(self.input_frame, "Check", self.check_answers, width=10)
        self.check_button.pack(side=tk.LEFT)
        self.check_button.pack_forget()  # Initially hide the check button until inputs are valid

        self.next_button = self.create_button(self.input_frame, "Next", self.next, width=10)
        self.next_button.pack(side=tk.RIGHT, padx=0)
        self.next_button.pack_forget()  # Initially hide the next button

        self.create_score_display()  

    def backspace_input(self):
        for entry in reversed(self.inputs):
            if entry.get():
                entry.config(state='normal')  # Ensure the state is normal before deleting
                entry.delete(0, tk.END)
                entry.config(state='readonly')  # Set back to readonly after modification
                break


    def validate_inputs(self, event=None):
        filled = all(entry.get().strip() for entry in self.inputs)
        print(filled)
        if filled:
            self.check_button.pack(side=tk.LEFT)
        else:
            self.check_button.pack_forget()



    def check_answers(self):
        user_input_values = [entry.get() for entry in self.inputs]
        print("User Input Values:", user_input_values)
        
        user_input_midi = solfege_to_midi(user_input_values)
        print("MIDI Notes:", user_input_midi)
        
        for midi_notes in user_input_midi:
            backend.user_guesses.append(midi_notes)
        
        backend.validate_user_input()
        detailed_answers = backend.get_detailed_match()
        print("Detailed Answers:", detailed_answers)

        print("Length of inputs:", len(self.inputs))
        print("Length of answers:", len(self.answers))
        print("Length of detailed answers:", len(detailed_answers))

        print("Zipping contents:", list(zip(self.inputs, self.answers, detailed_answers)))


        try:
            for input_entry, answer_entry, is_correct in zip(self.inputs, self.answers, detailed_answers):
                
                print("Type of input_entry:", type(input_entry))
                print("Type of answer_entry:", type(answer_entry))
                
                
                if is_correct:
                    input_entry.config(bg='light green')
                    answer_entry.config(state='normal')
                    answer_entry.insert(0, 'Correct')
                    answer_entry.config(state='readonly')
                else:
                    input_entry.config(bg='light coral')
                    answer_entry.config(state='normal')
                    answer_entry.insert(0, 'Wrong')
                    answer_entry.config(state='readonly')
            self.next_button.pack(side=tk.RIGHT, padx=0)
        except Exception as e:
            print("Error in processing:", e)





    def update_game_points(self, points):
        self.game_points_label.config(text=f"Game Points: {points}")

    def update_points_for_next_level(self, points):
        self.next_level_points_label.config(text=f"Points for Next Level: {points}")




    def next(self):
        self.setup_frames()
        backend.restart_game()
        self.next_button.pack_forget()  # Optionally hide it again for the next question
        # self.update_input_cells()

    def setup_keyboard_layout(self):
        keyboard_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        keyboard_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Move to bottom

        # Upper row for sharp notes
        upper_row = tk.Frame(keyboard_frame, bg='#2b2b2b')
        upper_row.pack(fill=tk.X)
        upper_notes = [("Ra", 1), ("Me", 3), ("Fi", 6), ("Le", 8), ("Te", 10)]
        for note, pos in upper_notes:
            tk.Button(upper_row, text=note, width=4, height=2, command=lambda n=note: self.update_input(n)).pack(side=tk.LEFT, padx=(55 if pos == 1 else 45, 5))

        # Lower row for natural notes
        lower_row = tk.Frame(keyboard_frame, bg='#2b2b2b')
        lower_row.pack(fill=tk.X)
        lower_notes = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Ti"]
        for note in lower_notes:
            tk.Button(lower_row, text=note, width=6, height=2, command=lambda n=note: self.update_input(n)).pack(side=tk.LEFT, padx=5)

    def update_input(self, note):
        solfege = {'Do': 'do', 'Ra': 'ra', 'Re': 're', 'Me': 'me', 'Mi': 'mi', 'Fa': 'fa', 'Fi': 'fi', 'Sol': 'sol', 'Le': 'le', 'La': 'la', 'Te': 'te', 'Ti': 'ti'}
        if note in solfege:
            backend.add_user_guess(solfege[note])
        if note == 0:
            backend.remove_user_guess()
        # Find the first empty input and fill it with the note
        for entry in self.inputs:
            if not entry.get():
                entry.config(state='normal')
                entry.insert(0, note)
                entry.config(state='readonly')
                self.validate_inputs()  # Manually trigger validation after updating the entry
                break

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
            
def solfege_to_midi(solfege):
    solfege_map = {
        'Do': 60, 'Ra': 61, 'Re': 62, 'Me': 63, 'Mi': 64,
        'Fa': 65, 'Fi': 66, 'Sol': 67, 'Le': 68, 'La': 69,
        'Te': 70, 'Ti': 71
    }
    return [solfege_map[note] for note in solfege if note in solfege_map]

if __name__ == "__main__":
    backend = EarTrainingGame()  # Create an instance of the EarTrainingGame class
    app = EarTrainerApp(backend)  # Pass the backend instance to the frontend class
    app.mainloop()
