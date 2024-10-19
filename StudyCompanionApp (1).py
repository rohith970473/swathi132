import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
import time
import openai

# Initialize the OpenAI API client with your API key
api_key = "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"
openai.api_key = api_key

# Create a database connection
conn = sqlite3.connect('notes.db')
c = conn.cursor()

# Create a table to store notes if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create a table to store flashcards if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create a table to store reminders if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_pending INTEGER DEFAULT 1
    )
''')

# Function to save a new note
def save_note():
    content = text_box.get('1.0', tk.END).strip()
    if content:
        c.execute('INSERT INTO notes (content) VALUES (?)', (content,))
        conn.commit()
        messagebox.showinfo('Note Saved', 'Note saved successfully.')
        text_box.delete('1.0', tk.END)
    else:
        messagebox.showwarning('Empty Note', 'Cannot save an empty note.')

# Function to display saved notes
def show_notes():
    c.execute('SELECT id, content, created_at FROM notes ORDER BY created_at DESC')
    notes = c.fetchall()
    if notes:
        notes_window = tk.Toplevel(root)
        notes_window.title('Saved Notes')
        notes_window.geometry('400x400')

        scroll_bar = tk.Scrollbar(notes_window)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        notes_text = tk.Text(notes_window, wrap=tk.WORD, yscrollcommand=scroll_bar.set)
        notes_text.pack(fill=tk.BOTH, expand=True)

        scroll_bar.config(command=notes_text.yview)

        for note in notes:
            note_id, content, created_at = note
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            ist_time = created_at + timedelta(hours=5, minutes=30)
            notes_text.insert(tk.END, f'Note ID: {note_id}\n\n')
            notes_text.insert(tk.END, f'Content:\n{content}\n\n')
            notes_text.insert(tk.END, f'Created At (IST): {ist_time}\n')
            notes_text.insert(tk.END, '-'*50 + '\n')

        notes_text.configure(state=tk.DISABLED)
    else:
        messagebox.showinfo('No Notes', 'No notes found.')

# Function to save a new flashcard
def save_flashcard():
    question = question_entry.get().strip()
    answer = answer_entry.get().strip()

    if question and answer:
        c.execute('INSERT INTO flashcards (question, answer) VALUES (?, ?)', (question, answer))
        conn.commit()
        messagebox.showinfo('Flashcard Saved', 'Flashcard saved successfully.')
        question_entry.delete(0, tk.END)
        answer_entry.delete(0, tk.END)
    else:
        messagebox.showwarning('Empty Flashcard', 'Question and answer cannot be empty.')

# Function to display saved flashcards
def show_flashcards():
    c.execute('SELECT id, question, answer, created_at FROM flashcards ORDER BY created_at DESC')
    flashcards = c.fetchall()
    if flashcards:
        flashcards_window = tk.Toplevel(root)
        flashcards_window.title('Saved Flashcards')
        flashcards_window.geometry('400x400')

        scroll_bar = tk.Scrollbar(flashcards_window)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        flashcards_text = tk.Text(flashcards_window, wrap=tk.WORD, yscrollcommand=scroll_bar.set)
        flashcards_text.pack(fill=tk.BOTH, expand=True)

        scroll_bar.config(command=flashcards_text.yview)

        for flashcard in flashcards:
            flashcard_id, question, answer, created_at = flashcard
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            ist_time = created_at + timedelta(hours=5, minutes=30)
            flashcards_text.insert(tk.END, f'Flashcard ID: {flashcard_id}\n\n')
            flashcards_text.insert(tk.END, f'Question: {question}\n')
            flashcards_text.insert(tk.END, f'Answer: {answer}\n\n')
            flashcards_text.insert(tk.END, f'Created At (IST): {ist_time}\n')
            flashcards_text.insert(tk.END, '-'*50 + '\n')

        flashcards_text.configure(state=tk.DISABLED)
    else:
        messagebox.showinfo('No Flashcards', 'No flashcards found.')

# Function to save a new reminder
def save_reminder():
    time_str = reminder_time_entry.get().strip()
    message = reminder_message_entry.get().strip()

    if time_str and message:
        try:
            reminder_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            current_time = datetime.now()
            if reminder_time < current_time:
                messagebox.showwarning('Invalid Time', 'Reminder time should be in the future.')
            else:
                c.execute('INSERT INTO reminders (time, message) VALUES (?, ?)', (time_str, message))
                conn.commit()
                messagebox.showinfo('Reminder Set', 'Reminder set successfully.')
                reminder_time_entry.delete(0, tk.END)
                reminder_message_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showwarning('Invalid Time', 'Please enter the time in the format: YYYY-MM-DD HH:MM')
    else:
        messagebox.showwarning('Empty Reminder', 'Time and message cannot be empty.')

# Function to display pending reminders
def show_pending_reminders():
    c.execute('SELECT id, time, message, created_at FROM reminders WHERE is_pending = 1 ORDER BY time ASC')
    reminders = c.fetchall()
    if reminders:
        reminders_window = tk.Toplevel(root)
        reminders_window.title('Pending Reminders')
        reminders_window.geometry('400x400')

        scroll_bar = tk.Scrollbar(reminders_window)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        reminders_text = tk.Text(reminders_window, wrap=tk.WORD, yscrollcommand=scroll_bar.set)
        reminders_text.pack(fill=tk.BOTH, expand=True)

        scroll_bar.config(command=reminders_text.yview)

        for reminder in reminders:
            reminder_id, time_str, message, created_at = reminder
            reminder_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            ist_time = reminder_time + timedelta(hours=5, minutes=30)
            reminders_text.insert(tk.END, f'Reminder ID: {reminder_id}\n\n')
            reminders_text.insert(tk.END, f'Time: {time_str}\n')
            reminders_text.insert(tk.END, f'Message: {message}\n\n')
            reminders_text.insert(tk.END, f'Created At: {created_at}\n')
            reminders_text.insert(tk.END, '-'*50 + '\n')

        reminders_text.configure(state=tk.DISABLED)
    else:
        messagebox.showinfo('No Reminders', 'No pending reminders found.')

# Function to check for and display reminders
def check_reminders():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    c.execute('SELECT id, time, message FROM reminders WHERE is_pending = 1 AND time <= ?', (current_time,))
    reminders = c.fetchall()
    if reminders:
        for reminder in reminders:
            reminder_id, time_str, message = reminder
            messagebox.showinfo('Reminder', message)
            c.execute('UPDATE reminders SET is_pending = 0 WHERE id = ?', (reminder_id,))
            conn.commit()

    root.after(1000, check_reminders)

# Function to send a message to the chatbot and display the response
def send_message():
    user_message = chat_entry.get()
    bot_response = get_bot_response(user_message)
    chat_log.insert(tk.END, f"User: {user_message}\n")
    chat_log.insert(tk.END, f"Bot: {bot_response}\n")
    chat_entry.delete(0, tk.END)  # Clear the input field

def get_bot_response(user_message):
    response = openai.Completion.create(
        engine="text-davinci-002",  # ChatGPT engine
        prompt=f"User: {user_message}\nChatGPT:",
        max_tokens=50  # Adjust the max tokens based on your needs
    )
    return response.choices[0].text

# Function to show the note-taking feature
def show_note_taking():
    flashcards_frame.pack_forget()
    reminders_frame.pack_forget()
    chatbot_frame.pack_forget()
    text_box.pack(fill=tk.BOTH, expand=True)
    save_note_button.pack(side=tk.RIGHT)
    show_notes_button.pack(side=tk.RIGHT)

# Function to show the flashcards feature
def show_flashcards_feature():
    text_box.pack_forget()
    save_note_button.pack_forget()
    show_notes_button.pack_forget()
    chatbot_frame.pack_forget()
    reminders_frame.pack_forget()
    flashcards_frame.pack(pady=10)

# Function to show the reminders feature
def show_reminders_feature():
    text_box.pack_forget()
    save_note_button.pack_forget()
    show_notes_button.pack_forget()
    flashcards_frame.pack_forget()
    chatbot_frame.pack_forget()
    reminders_frame.pack(pady=10)

def show_chatbot():
    # Hide other frames
    text_box.pack_forget()
    save_note_button.pack_forget()
    show_notes_button.pack_forget()
    flashcards_frame.pack_forget()
    reminders_frame.pack_forget()
    
    # Show chatbot frame
    chatbot_frame.pack(pady=10)

# Create the main application window
root = tk.Tk()
root.title('Study Companion')

# Create a menu of feature names
menu_frame = tk.Frame(root)
menu_frame.pack(pady=10)

note_taking_button = tk.Button(menu_frame, text='Note-Taking', command=show_note_taking)
note_taking_button.pack(side=tk.LEFT, padx=5)

flashcards_button = tk.Button(menu_frame, text='Flashcards', command=show_flashcards_feature)
flashcards_button.pack(side=tk.LEFT, padx=5)

reminders_button = tk.Button(menu_frame, text='Study Reminders', command=show_reminders_feature)
reminders_button.pack(side=tk.LEFT, padx=5)

# Create a text box for note-taking
text_box = tk.Text(root, wrap=tk.WORD)

# Create a save note button
save_note_button = tk.Button(root, text='Save Note', command=save_note)

# Create a show notes button
show_notes_button = tk.Button(root, text='Saved Notes History', command=show_notes)

# Create a frame for flashcards
flashcards_frame = tk.Frame(root)

# Create question label and entry
question_label = tk.Label(flashcards_frame, text='Question:')
question_label.grid(row=0, column=0, padx=5, pady=5)

question_entry = tk.Entry(flashcards_frame)
question_entry.grid(row=0, column=1, padx=5, pady=5)

# Create answer label and entry
answer_label = tk.Label(flashcards_frame, text='Answer:')
answer_label.grid(row=1, column=0, padx=5, pady=5)

answer_entry = tk.Entry(flashcards_frame)
answer_entry.grid(row=1, column=1, padx=5, pady=5)

# Create a save flashcard button
save_flashcard_button = tk.Button(flashcards_frame, text='Save Flashcard', command=save_flashcard)
save_flashcard_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Create a show flashcards button
show_flashcards_button = tk.Button(flashcards_frame, text='Saved Flashcards History', command=show_flashcards)
show_flashcards_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Create a frame for reminders
reminders_frame = tk.Frame(root)

# Create time label and entry
reminder_time_label = tk.Label(reminders_frame, text='Time (YYYY-MM-DD HH:MM):')
reminder_time_label.grid(row=0, column=0, padx=5, pady=5)

reminder_time_entry = tk.Entry(reminders_frame)
reminder_time_entry.grid(row=0, column=1, padx=5, pady=5)

# Create message label and entry
reminder_message_label = tk.Label(reminders_frame, text='Message:')
reminder_message_label.grid(row=1, column=0, padx=5, pady=5)

reminder_message_entry = tk.Entry(reminders_frame)
reminder_message_entry.grid(row=1, column=1, padx=5, pady=5)

# Create a save reminder button
save_reminder_button = tk.Button(reminders_frame, text='Set Reminder', command=save_reminder)
save_reminder_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Create a show pending reminders button
show_pending_reminders_button = tk.Button(reminders_frame, text='Pending Reminders', command=show_pending_reminders)
show_pending_reminders_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

chatbot_frame = tk.Frame(root)

chat_entry = tk.Entry(chatbot_frame, width=50)
chat_entry.pack()

send_button = tk.Button(chatbot_frame, text="Send", command=send_message)
send_button.pack()

chat_log = tk.Text(chatbot_frame, width=50, height=20)
chat_log.pack()

# Button to show chatbot section
chatbot_button = tk.Button(menu_frame, text='Chatbot', command=show_chatbot)
chatbot_button.pack(side=tk.LEFT, padx=5)

# Check for reminders every second
root.after(1000, check_reminders)

# Show the note-taking feature by default
show_note_taking()

# Run the application
root.mainloop()

# Close the database connection
conn.close()
