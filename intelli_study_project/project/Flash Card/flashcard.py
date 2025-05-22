import gradio as gr
import json
import os
import random
import time
from datetime import datetime

# Database file path
DB_PATH = 'cards.json'

# Initialize database if not exists
if not os.path.exists(DB_PATH):
    with open(DB_PATH, 'w') as f:
        json.dump([
            {"front": "Two Sum", "back": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."},
            {"front": "Reverse Linked List", "back": "Given the head of a singly linked list, reverse the list and return the reversed list."},
            {"front": "Binary Tree Inorder Traversal", "back": "Given the root of a binary tree, return the inorder traversal of its nodes' values."},
            {"front": "Valid Parentheses", "back": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid."},
            {"front": "Merge Two Sorted Lists", "back": "Merge two sorted linked lists and return it as a sorted list."},
            {"front": "Maximum Subarray", "back": "Find the contiguous subarray (containing at least one number) which has the largest sum and return its sum."},
            {"front": "Product of Array Except Self", "back": "Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i]."},
            {"front": "3Sum", "back": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0."},
            {"front": "Container With Most Water", "back": "Given n non-negative integers a1, a2, ..., an , where each represents a point at coordinate (i, ai). n vertical lines are drawn such that the two endpoints of the line i is at (i, ai) and (i, 0). Find two lines, which together with x-axis forms a container, such that the container contains the most water."},
            {"front": "Search in Rotated Sorted Array", "back": "Given the array nums after the possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums."},
            {"front": "Longest Substring Without Repeating Characters", "back": "Given a string s, find the length of the longest substring without repeating characters."},
            {"front": "Longest Palindromic Substring", "back": "Given a string s, return the longest palindromic substring in s."},
            {"front": "Zigzag Conversion", "back": "The string \"PAYPALISHIRING\", is written in a zigzag pattern on a given number of rows like this: (you may want to display this pattern in a fixed font for better legibility)"},
            {"front": "String to Integer (atoi)", "back": "Implement the myAtoi(string s) function, which converts a string to a 32-bit signed integer (similar to C/C++'s atoi function)."},
            {"front": "Roman to Integer", "back": "Given a roman numeral, convert it to an integer."}
        ], f)

# Load cards from database
def load_cards():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

# Save cards to database
def save_cards(cards):
    try:
        with open(DB_PATH, 'w') as f:
            json.dump(cards, f)
        return True
    except Exception as e:
        print(f"Error saving cards: {e}")
        return False

# Current card index
current_card_idx = 0
cards = load_cards()
random_mode = False
timer_active = False

# Flip card function
def flip_card():
    return "Show Back" if flip_btn.value == "Show Front" else "Show Front"

# Update card display
def update_card_display():
    global current_card_idx, cards
    cards = load_cards()
    if not cards:
        return "No cards available", "Add some cards first!", "0/0"
    
    return cards[current_card_idx]["front"], cards[current_card_idx]["back"], f"{current_card_idx + 1}/{len(cards)}"

# Navigation functions
def next_card():
    global current_card_idx
    if cards:
        if random_mode:
            current_card_idx = random.randint(0, len(cards)-1)
        else:
            current_card_idx = (current_card_idx + 1) % len(cards)
    return update_card_display()

def prev_card():
    global current_card_idx
    if cards:
        if random_mode:
            current_card_idx = random.randint(0, len(cards)-1)
        else:
            current_card_idx = (current_card_idx - 1) % len(cards)
    return update_card_display()

def toggle_random():
    global random_mode
    random_mode = not random_mode
    return "Random Mode: ON" if random_mode else "Random Mode: OFF"

def start_timer(duration):
    global timer_active, current_card_idx
    timer_active = True
    
    if random_mode:
        current_card_idx = random.randint(0, len(cards)-1)
    
    for remaining in range(duration, 0, -1):
        time.sleep(1)
        yield f"Time remaining: {remaining}s"
    
    timer_active = False
    yield "Time's up!"
    return "Show Back" if flip_btn.value == "Show Front" else "Show Front"

# Add new card
def add_card(front, back):
    global current_card_idx, cards
    new_card = {"front": front, "back": back}
    cards.append(new_card)
    if not save_cards(cards):
        return "Error saving card!", "", *update_card_display()
    current_card_idx = len(cards) - 1
    return "", "", *update_card_display()

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# Flashcard App")
    
    with gr.Row():
        card_counter = gr.Textbox(label="Card", value=f"1/{len(cards)}", interactive=False)
    
    with gr.Row():
        front_display = gr.Textbox(label="Front", interactive=False, lines=10)
        back_display = gr.Textbox(label="Back", interactive=False, visible=False, lines=10)
    
    with gr.Row():
        flip_btn = gr.Button("Show Back", variant="primary")
        prev_btn = gr.Button("Previous Card")
        next_btn = gr.Button("Next Card")
        random_btn = gr.Button("Random Mode", variant="secondary")
        timer_dropdown = gr.Dropdown([30, 60], value=60, label="Timer Duration (seconds)")
        timer_btn = gr.Button("Start Timer", variant="secondary")
    
    with gr.Accordion("Add New Card", open=False):
        with gr.Row():
            front_input = gr.Textbox(label="Front Text")
            back_input = gr.Textbox(label="Back Text")
        add_btn = gr.Button("Add Card")
    
    # Event handlers
    flip_btn.click(
        lambda: (gr.Textbox(visible=flip_btn.value == "Show Back"), 
                 gr.Textbox(visible=flip_btn.value == "Show Front"),
                 flip_card()),
        outputs=[front_display, back_display, flip_btn]
    )
    
    prev_btn.click(prev_card, outputs=[front_display, back_display, card_counter])
    next_btn.click(next_card, outputs=[front_display, back_display, card_counter])
    random_btn.click(toggle_random, outputs=[random_btn])
    timer_btn.click(start_timer, inputs=[timer_dropdown], outputs=[timer_btn]).then(
        lambda: (gr.Textbox(visible=False), gr.Textbox(visible=True), "Show Back"),
        outputs=[front_display, back_display, flip_btn]
    ).then(
        update_card_display,
        outputs=[front_display, back_display, card_counter]
    )
    
    add_btn.click(
        add_card, 
        inputs=[front_input, back_input], 
        outputs=[front_input, back_input, front_display, back_display, card_counter]
    )
    
    # Initialize display
    app.load(update_card_display, outputs=[front_display, back_display, card_counter])

if __name__ == "__main__":
    app.launch()