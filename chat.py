import tkinter as tk
from tkinter import scrolledtext, messagebox
import google.generativeai as genai
import threading
import os
from dotenv import load_dotenv

class SimpleChatbot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Simple Gemini Chatbot")
        self.window.geometry("600x500")
        
        # Configure Gemini (you need to set your API key)
        self.setup_gemini()
        
        self.setup_gui()
        
    def setup_gemini(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Get API key from environment variable
        API_KEY = os.getenv('GEMINI_API_KEY')
        
        if not API_KEY:
            messagebox.showerror("API Key Error", 
                               "GEMINI_API_KEY not found in .env file!\n"
                               "Please create a .env file with your API key.")
            self.model = None
            return
            
        try:
            genai.configure(api_key=API_KEY)
            # Use the fastest model with optimized settings
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Configure for faster responses
            self.generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,  # Limit response length for speed
                top_p=0.8,
                top_k=40
            )
        except Exception as e:
            messagebox.showerror("API Error", f"Failed to initialize Gemini: {str(e)}")
            self.model = None
        
    def setup_gui(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=70, 
            height=25,
            state=tk.DISABLED,
            bg="#f0f0f0"
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = tk.Frame(self.window)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Message input
        self.message_input = tk.Entry(input_frame, font=("Arial", 12))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_input.bind("<Return>", lambda event: self.send_message())
        
        # Send button
        self.send_button = tk.Button(
            input_frame, 
            text="Send", 
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Welcome message
        self.add_message("Bot", "Hello! I'm your simple Gemini chatbot. How can I help you today?")
        
    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def send_message(self):
        user_message = self.message_input.get().strip()
        if not user_message:
            return
            
        # Display user message
        self.add_message("You", user_message)
        self.message_input.delete(0, tk.END)
        
        # Show loading indicator
        self.add_message("Bot", "Thinking...")
        
        # Disable send button while processing
        self.send_button.config(state=tk.DISABLED, text="Sending...")
        
        # Get bot response in a separate thread to avoid GUI freezing
        threading.Thread(target=self.get_bot_response, args=(user_message,), daemon=True).start()
        
    def get_bot_response(self, user_message):
        try:
            if self.model is None:
                bot_response = "Bot is not properly configured. Please check your API key."
            else:
                # Generate response using Gemini with optimized config
                response = self.model.generate_content(
                    user_message,
                    generation_config=self.generation_config
                )
                bot_response = response.text
            
            # Update GUI in main thread
            self.window.after(0, lambda: self.display_bot_response(bot_response))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\nTry using model 'gemini-1.5-flash' or 'gemini-1.5-pro'"
            self.window.after(0, lambda: self.display_bot_response(error_msg))
    
    def display_bot_response(self, response):
        # Remove the "Thinking..." message
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get("1.0", tk.END)
        if "Bot: Thinking..." in content:
            lines = content.split('\n')
            # Find and remove the "Thinking..." line
            new_lines = [line for line in lines if "Bot: Thinking..." not in line]
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.insert("1.0", '\n'.join(new_lines))
        
        # Add the actual response
        self.add_message("Bot", response)
        
        # Re-enable send button
        self.send_button.config(state=tk.NORMAL, text="Send")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    # Check if required library is installed
    try:
        import google.generativeai as genai
    except ImportError:
        print("Error: google-generativeai library not found!")
        print("Please install it using: pip install google-generativeai")
        exit(1)
    
    # Show API key reminder
    print("Remember to set your Gemini API key in the code!")
    print("Get your free API key from: https://makersuite.google.com/app/apikey")
    
    app = SimpleChatbot()
    app.run()