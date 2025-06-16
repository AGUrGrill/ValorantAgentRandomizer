import random
import fandom
from tkinter import *
import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from bs4 import BeautifulSoup

# Fandom Settings
fandom.set_wiki("Valorant")
agent_page = fandom.page(title = "Agent")

# Agent Images (to prevent garbage collection)
saved_images = []

# UI
COLUMN_WIDTH = 4
UI_WIDTH = 48


def get_agent_list(option):
    # Variables
    agent_list = []
    line = ""
    agent = None
    role = None
    line_num = 0
    agent_num = 1
    
    # Fandom Page Selection
    agent_list_page = agent_page.section("List of Agents")

    # Get Data 
    for letter in agent_list_page:
        # If Agent 8, Skip
        if agent_num == 8:
            agent_num += 1
        # If new line, get data from previous line
        if letter != '\n':
            line += letter
        else: # Determine line and get appropriate info
            if line_num == 1: # Set Agent
                agent = line.strip()
                line_num += 1
            elif line_num == 2: # Set Role
                role = line.strip()
                line_num = 0
                # Append Information when role is defined
                if role == option or option == "all":
                    agent_list.append(agent)
                    print(agent)
            elif line == f"0{agent_num}" or line == f"{agent_num}": # Determine if agent info is coming up
                line_num = 1
                agent_num += 1
            
            line = "" # Reset line after using

    return agent_list
    
def get_random_agent(option):
    agent_list = get_agent_list(option)
    print(len(agent_list))
    ran_num = random.randint(0, len(agent_list)-1)
    return agent_list[ran_num]
        
def get_agent_image(agent):
    # Get valorant wiki image (thank you chat gpt this was giving me a headache with valorant wikis horrible page structure)
    img_url = agent_page.images[0] # Fallback img
    base_url = "https://valorant.fandom.com/wiki/"
    agent_url = base_url + agent.replace(" ", "_")

    response = requests.get(agent_url)
    if response.status_code != 200:
        print(f"Failed to get page for {agent}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Get the infobox image (usually the portrait)
    aside = soup.find("aside", class_="portable-infobox")
    if aside is None:
        print(f"Could not find aside infobox for {agent}")

    try:
        img_tag = aside.find("img")
        img_url = img_tag.get("data-src") or img_tag.get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url
    except:
        print(f"Error getting image.")
    
    # Get corresponding agent image
    response = requests.get(img_url)
    image = Image.open(BytesIO(response.content))
    image = image.resize((image.width*2, image.height*2), Image.LANCZOS)
    agent_image_photo = ImageTk.PhotoImage(image)

    return agent_image_photo

def set_random_agent(role):
    agent = get_random_agent(role)
    img = get_agent_image(agent)

    # Change Label to reflect selection
    label.config(text=agent)
    image_label.config(image=img)
    image_label.image = img

def set_all_agents(role):
    global saved_images
    
    # Variables
    agent_list = get_agent_list(role)
    row = 0
    column = 0

    # Place Agents on Frame
    for i in range(len(agent_list)):
        try:
            agent = agent_list[i]
            agent_img = get_agent_image(agent)
            saved_images.append(agent_img)
            img_label = Label(agent_frame, image=agent_img, width=12).grid(row=row, column=column, stick=EW)
            agent_label = Label(agent_frame, text=agent, width=12).grid(row=row+1, column=column, stick=EW)
            column += 1
            if column >= COLUMN_WIDTH:
                row += 3
                column = 0 
            print(f"{agent}, {row}, {column}")
        except:
            print("Error getting agent.")           

# Main UI
root = tk.Tk()
root.title("Valorant Agent Randomizer")
root.resizable(True, True)

for i in range(COLUMN_WIDTH):
    root.columnconfigure(i, weight=0)

image_label = Label(root, width=UI_WIDTH)
image_label.grid(row = 0, column=0, sticky=EW)

label = Label(root, text="?")
label.grid(row = 1, column=0, sticky=EW)

button = tk.Button(root, width=UI_WIDTH, text="Get Random Agent", command=lambda: set_random_agent("all"))
button.grid(row = 2, column=0, sticky=EW)

# Role Buttons
role_frame = Frame(root, width=int(UI_WIDTH/2))
role_frame.grid(row=3, column=0, sticky=EW)
duelist = tk.Button(role_frame, width=int(UI_WIDTH/2), text="Duelist", command=lambda: set_random_agent("Duelist"))
duelist.grid(row = 0, column=0, sticky=EW)
initiator = tk.Button(role_frame, width=int(UI_WIDTH/2), text="Initiator", command=lambda: set_random_agent("Initiator"))
initiator.grid(row = 0, column=1, sticky=EW)
controller = tk.Button(role_frame, width=int(UI_WIDTH/2), text="Controller", command=lambda: set_random_agent("Controller"))
controller.grid(row = 1, column=0, sticky=EW)
sentinel = tk.Button(role_frame, width=int(UI_WIDTH/2), text="Sentinel", command=lambda: set_random_agent("Sentinel"))
sentinel.grid(row = 1, column=1, sticky=EW)

all_button = tk.Button(root, width=UI_WIDTH, text="Get ALL Agents", command=lambda: set_all_agents("all"))
all_button.grid(row = 4, column=0, sticky=EW)

agent_frame = Frame(root, width=UI_WIDTH)
agent_frame.grid(row=5, column=0, sticky=EW)

quit_button = tk.Button(root, width=UI_WIDTH, text="Quit", command=root.destroy)
quit_button.grid(row = 6, column=0, sticky=EW)

root.mainloop()