import os
import sys
import time
import msvcrt

WHITE_ON_BLACK = '\033[30;47m'  # Black text on white background
RESET = '\033[0m'  # Reset color

def input_box_with_prompt(text="Please enter content:", confirm_text="Confirm", cancel_text="Cancel"):
    """
    Input box function with prompt text.
    Input:
    - text: Prompt text, customizable
    - confirm_text: Confirm button text
    - cancel_text: Cancel button text
    Output:
    - The content entered by the user (string), returns False if canceled
    """
    
    while True:
        user_input = ""  # Content entered by the user
        selected_option = 0  # 0 means "Confirm", 1 means "Cancel"
        
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')

            # Display the prompt text and current input content
            print(f"{text}")
            print(f"Input content: {user_input}")
            print()
            
            # Show "Confirm" and "Cancel" buttons, highlight the current selection
            if selected_option == 0:
                print(f"{WHITE_ON_BLACK}[{confirm_text}]{RESET}   [{cancel_text}]")
            else:
                print(f"[{confirm_text}]   {WHITE_ON_BLACK}[{cancel_text}]{RESET}")
                
            # Capture keyboard input
            key = msvcrt.getch()

            if key == b'\r':  # Enter key
                if selected_option == 0:  # If the current option is "Confirm"
                    if user_input.strip() == "":  # If the input is empty
                        break  # Re-enter
                    else:
                        return user_input  # Return the user's input
                elif selected_option == 1:  # If the current option is "Cancel"
                    return False  # Return False

            elif key == b'\xe0':  # Arrow keys
                direction = msvcrt.getch()
                if direction == b'K':  # Left arrow key
                    selected_option = (selected_option - 1) % 2
                elif direction == b'M':  # Right arrow key
                    selected_option = (selected_option + 1) % 2
            
            elif key == b'\x08':  # Backspace key
                user_input = user_input[:-1]  # Delete the last character
                
            else:
                try:
                    # Capture the character entered by the user, ignore decoding errors
                    user_input += key.decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"Decoding error: {e}")

def show_progress_bar(text, progress, total, bar_length=40):
    """
    Display a progress bar in the console.
    Input:
    - text: Prompt text
    - progress: Current progress (integer)
    - total: Total progress (integer)
    - bar_length: Length of the progress bar (default 40)
    Output:
    - Dynamically updated progress bar display
    """
    # Calculate the percentage of progress
    percent = float(progress) / total
    # Calculate how much of the bar is filled
    filled_length = int(bar_length * percent)
    
    # Generate the progress bar string
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    # Overwrite the previous line to dynamically display progress
    sys.stdout.write(f'\r{text} Progress: |{bar}| {percent * 100:.1f}% Complete')
    sys.stdout.flush()

    # Add a new line when progress is complete
    if progress == total:
        print()

def clear_console():
    """ Clear the screen, simulating a curses-like effect """
    os.system('cls' if os.name == 'nt' else 'clear')

def render_options(input_type, array_size=None, options=None, text="Select an option", visible_rows=25):
    """
    Input:
    - input_type: 1 for a regular list, 2 for a two-dimensional array
    - array_size: (rows, cols), size of the 2D array (only used if input_type is 2)
    - options: Regular list or 2D array
    - text: The prompt text to display
    - visible_rows: The maximum number of rows to display, default is 25
    Output:
    - The index of the selected option (for a list) or the coordinates (for a 2D array)
    """
    def get_max_width(options):
        if isinstance(options[0], list):  # Check if it's a 2D array
            return max(len(item) for row in options for item in row)
        else:
            return max(len(item) for item in options)

    # Initialize option index
    selected_row = 0
    selected_col = 0
    scroll_offset = 0  # Current scroll offset

    max_width = get_max_width(options) + 2  # Get maximum width and add 2 spaces for alignment

    # First render the prompt text (displayed once)
    rows, cols = array_size if array_size else (len(options), 1)  # Calculate rows and columns
    print(text)  # Display the prompt text once
    print()

    # Render visible options
    def render_page():
        for row in range(scroll_offset, min(scroll_offset + visible_rows, rows)):
            if input_type == 1:
                print("  " + options[row].ljust(max_width))
            elif input_type == 2:
                for col in range(cols):
                    print(f"  {options[row][col].ljust(max_width)}", end="")
                print()

    render_page()

    while True:
        # Move the cursor back to the option section using escape codes
        for _ in range(min(visible_rows, rows)):  # Go back to the options
            print("\033[F", end="")

        # Re-render the options, only updating the highlighted part
        if input_type == 1:  # Handle a regular list
            for idx in range(scroll_offset, min(scroll_offset + visible_rows, len(options))):
                padded_option = options[idx].ljust(max_width)  # Left-align and pad to max width
                if idx == selected_row:
                    print(f"> {WHITE_ON_BLACK}{padded_option}{RESET}")  # Highlight current option
                else:
                    print(f"  {padded_option}")

        elif input_type == 2:  # Handle a 2D array
            for row in range(scroll_offset, min(scroll_offset + visible_rows, rows)):
                for col in range(cols):
                    padded_option = options[row][col].ljust(max_width)  # Left-align and pad to max width
                    if row == selected_row and col == selected_col:
                        print(f"  {WHITE_ON_BLACK}{padded_option}{RESET}", end="")  # Highlight current option
                    else:
                        print(f"  {padded_option}", end="")
                print()  # Newline

        # Capture keyboard input
        key = msvcrt.getch()

        if key == b'\r':  # Enter key
            if input_type == 1:
                return selected_row  # Return option index
            elif input_type == 2:
                return (selected_row, selected_col)  # Return 2D array coordinates

        elif key == b'\xe0':  # Special keys (arrow keys)
            direction = msvcrt.getch()

            if direction == b'H':  # Up arrow key
                if selected_row > 0:
                    selected_row -= 1
                if selected_row < scroll_offset:
                    scroll_offset -= 1  # Scroll up
            elif direction == b'P':  # Down arrow key
                if selected_row < rows - 1:
                    selected_row += 1
                if selected_row >= scroll_offset + visible_rows:
                    scroll_offset += 1  # Scroll down
            elif direction == b'K':  # Left arrow key (only for 2D array)
                if input_type == 2:
                    selected_col = (selected_col - 1) % cols
            elif direction == b'M':  # Right arrow key (only for 2D array)
                if input_type == 2:
                    selected_col = (selected_col + 1) % cols

def display_aligned_text(text_list, leftorright='left', padding=2):
    """
    Display text in the console, ensuring alignment.
    Input:
    - text_list: List of strings
    - leftorright: Alignment, 'left' for left-aligned, 'right' for right-aligned, default is left-aligned
    - padding: Spaces added to the right of the text, default is 2 spaces
    Output:
    - Aligned text display
    """
    max_length = max([len(text) for text in text_list]) + padding

    for text in text_list:
        if leftorright == 'left':
            print(text.ljust(max_length))  # Left-aligned
        elif leftorright == 'right':
            print(text.rjust(max_length))  # Right-aligned

def showing():
    # # Example call to the render_options function, select and highlight options
    # result = input_box_with_prompt("Please enter your name:", "Confirm", "Cancel")
    # if result:
    #     print(f"You entered: {result}")
    # else:
    #     print("Input was canceled")
    # for i in range(100):
    #     show_progress_bar("Downloading..", progress=i, total=100)
    #     time.sleep(0.1)
    text_showing_render = "Welcome to TeiGUI-Lib V1 Test Version\nYou are in __main__ mode (display mode)\nPlease choose the feature to display:"
    a = render_options(input_type=1, options=["2D Array Display", "Progress Display", "Text Display (Left Align)", "Text Display (Right Align)", "Text Input"], text=text_showing_render)
    if a == 0:
        a = render_options(2, array_size=(2,2), options=[['A1', 'B1'], ['A2', 'B2']], text="2D Array Test")
        print(a)
    elif a == 1:
        for i in range(100):
            show_progress_bar("Downloading..", progress=i, total=100)
            time.sleep(0.01)
    elif a == 2:
        display_aligned_text(text_list=["String Text Display", "Welcome to TeiGUI"], leftorright='left')
    elif a == 3:
        display_aligned_text(text_list=["String Text Display", "Welcome to TeiGUI!!!!!!!!!!!"], leftorright='right')
    elif a == 4:
        result = input_box_with_prompt("Please enter (Chinese not supported currently):", "Confirm", "Cancel")
        if result:
            print(f"You entered: {result}")
        else:
            print("Input was canceled")
if __name__ == '__main__':
    showing()
    input("__main__finshed press enter to exit \n return 0")
