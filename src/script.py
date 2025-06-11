import tkinter as tk
from tkinter import ttk
import random
import math
import time
import os


class Animal:
    """Class Animal stores all relevant information about object used in application"""
    def __init__(self, animal_type, canvas, x, y):
        self.type = animal_type
        self.canvas = canvas
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 2
        self.size = 60
        self.direction = 0
        self.move_timer = 0

        # staty 0-100
        self.hunger = 50
        self.boredom = 50
        self.happiness = 70

        self.hungerT = 0
        self.boredomT = 0
        self.last_update = time.time()

        self.moving = False
        self.eating = False
        self.playing = False
        self.actionT = 0

        self.chosenPet = None
        self.bowl = None
        self.food = None
        self.toys = []

        self.foodUsed = None
        self.playtime = None

        self.petImg = None
        self.load_img()
        self.visualize()

    def load_img(self):
        """Function to load PNG image for the pet"""
        try:
            path = f"images/{self.type}.png"
            if os.path.exists(path):
                self.petImg = tk.PhotoImage(file=path)

                width = self.petImg.width()
                height = self.petImg.height()

                if width > self.size or height > self.size:
                    factor = max(width // self.size, height // self.size, 1)
                    self.petImg = self.petImg.subsample(factor, factor)

            else:
                raise FileNotFoundError("nie znalezionp img")

        except Exception as e:
            print(f"Error loading PNG for {self.type}: {e}")
            self.petImg = None

    def visualize(self):
        """Visualize the pet from loaded image with added shadow effect"""
        self.shadow = self.canvas.create_oval(
            self.x - 25, self.y + 20, self.x + 25, self.y + 35,
            fill="gray", outline="", stipple="gray50"
        )


        self.chosenPet = self.canvas.create_image(
        self.x, self.y, image=self.petImg, anchor=tk.CENTER)



    def update(self):
        """Function to control and set movement targets, update stats over elapsed time.
            Updates timers.
            Increases values of hunger, every 3 seconds, and boredom, every 5 seconds.
             Calculates and updates value of happiness"""
        current_time = time.time()
        dt = (current_time - self.last_update) * 1000
        self.last_update = current_time

        self.hungerT += dt
        self.boredomT += dt
        self.move_timer += dt

        if self.hungerT > 3000:
            self.hunger = min(100, self.hunger + 1)
            self.hungerT = 0

        if self.boredomT > 5000:
            self.boredom = min(100, self.boredom + 1)
            self.boredomT = 0

        self.happiness = max(0, 100 - (self.hunger * 0.5) - (self.boredom * 0.5))

        if self.actionT > 0:
            self.actionT -= dt
            if self.actionT <= 0:
                self.eating = False
                self.playing = False
                self.after_eating()

        if not self.eating and not self.playing:
            distance_to_target = math.sqrt((self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2)

            if distance_to_target < 5 or self.move_timer > 2000:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                self.target_x = random.randint(50, max(100, canvas_width - 50))
                self.target_y = random.randint(100, max(150, canvas_height - 50))
                self.move_timer = 0

            if distance_to_target > 5:
                self.direction = math.atan2(self.target_y - self.y, self.target_x - self.x)
                new_x = self.x + math.cos(self.direction) * self.speed
                new_y = self.y + math.sin(self.direction) * self.speed

                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                new_x = max(50, min(canvas_width - 50, new_x))
                new_y = max(80, min(canvas_height - 50, new_y))

                self.move(new_x, new_y)
                self.moving = True
            else:
                self.moving = False

    def move(self, new_x, new_y):
        """Function to move pet with shadow to new coordinates
            Args: new_x, new_y: coordinates of target to move to.

            Moves pet with shadow and updates self coordinates.
        """
        dx = new_x - self.x
        dy = new_y - self.y

        items_to_move = [self.chosenPet, self.shadow]


        for item in items_to_move:
            if item:
                self.canvas.move(item, dx, dy)

        self.x = new_x
        self.y = new_y

    def feed(self, meal):
        """Function to feed the pet.
            Updates hunger and happiness stats based on chosen meal type

            Args: meal(string): chosen meal type
            """
        karma = {
            "Przekąska": {"hunger": 15, "happiness": 5, "duration": 1500},
            "Obiad": {"hunger": 30, "happiness": 10, "duration": 2000},
            "Królewska uczta": {"hunger": 50, "happiness": 20, "duration": 3000}
        }

        foodinfo = karma.get(meal, karma[meal])

        self.hunger = max(0, self.hunger - foodinfo["hunger"])
        self.happiness = min(100, self.happiness + foodinfo["happiness"])
        self.eating = True
        self.actionT = foodinfo["duration"]
        self.foodUsed = meal

        self.vis_bowl()

    def play(self, playtype):
        """Function to feed the pet.
            Updates hunger and happiness stats based on chosen play type

            Args: playtype(string) : chosen play type
            """
        zabawa = {
            "Na odwal": {"boredom": 15, "happiness": 8, "duration": 2000},
            "Z życiem": {"boredom": 25, "happiness": 15, "duration": 3000},
            "Do upadku": {"boredom": 40, "happiness": 25, "duration": 5000}
        }

        playinfo = zabawa.get(playtype, zabawa[playtype])

        self.boredom = max(0, self.boredom - playinfo["boredom"])
        self.happiness = min(100, self.happiness + playinfo["happiness"])
        self.playing = True
        self.actionT = playinfo["duration"]
        self.playtime = playtype

        self.vis_toys()

    def vis_bowl(self):
        """Function visualising a bowl and food based on meal type chosen, to be sure that only one bowl is shown it firtsly clears the canvas from eventual other bowls."""
        bowl_sizes = {"Przekąska": 15, "Obiad": 20, "Królewska uczta": 25}
        size = bowl_sizes.get(self.foodUsed, bowl_sizes[self.foodUsed])

        if self.bowl:
            self.canvas.delete(self.bowl)
        if self.food:
            self.canvas.delete(self.food)

        self.bowl = self.canvas.create_oval(
            self.x - size, self.y + 40, self.x + size, self.y + 50,
            fill="brown", outline="black", width=2
        )

        self.food = self.canvas.create_oval(
            self.x - size + 4, self.y + 42, self.x + size - 4, self.y + 48,
            fill="yellow", outline="orange", width=1
        )

    def vis_toys(self):
        """Function visualising toy or toys based on play type, to be sure that only one set of toys is shown it firtsly clears the canvas from eventual other toys."""
        self.after_play()

        toy_counts = {"Na odwal": 1, "Z życiem": 2, "Do upadku": 3}
        count = toy_counts.get(self.playtime, toy_counts[self.playtime])
        colors = ["red", "blue", "green"]
        shapes = ["oval", "rectangle", "triangle"]

        for i in range(count):
            x_offset = 40 + i * 20
            y_offset = -20 + i * 8
            color = colors[i % len(colors)]
            shape = shapes[i % len(shapes)]

            if shape == "oval":
                toy = self.canvas.create_oval(
                    self.x + x_offset - 8, self.y + y_offset - 8,
                    self.x + x_offset + 8, self.y + y_offset + 8,
                    fill=color, outline="black", width=2
                )
            elif shape == "rectangle":
                toy = self.canvas.create_rectangle(
                    self.x + x_offset - 6, self.y + y_offset - 6,
                    self.x + x_offset + 6, self.y + y_offset + 6,
                    fill=color, outline="black", width=2
                )
            else:
                toy = self.canvas.create_polygon(
                    self.x + x_offset, self.y + y_offset - 8,
                    self.x + x_offset - 8, self.y + y_offset + 8,
                    self.x + x_offset + 8, self.y + y_offset + 8,
                    fill=color, outline="black", width=2
                )

            self.toys.append(toy)

    def after_play(self):
        """Function used to clear the canvas from shown toys."""
        for toy_id in self.toys:
            self.canvas.delete(toy_id)
        self.toys = []

    def after_eating(self):
        """Function used to clear the canvas from any and all visuals shown from actions"""
        if self.bowl:
            self.canvas.delete(self.bowl)
            self.bowl = None
        if self.food:
            self.canvas.delete(self.food)
            self.food = None
        self.after_play()


class StatusBar:
    """Class StatusBar is a class to store info and methods realated to maintaining and updating status bars, helping visualize raw number values"""
    def __init__(self, parent, label, color, max_value=100):
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, text=f"{label}: 0")
        self.label.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(
            self.frame, length=200, mode='determinate',
            maximum=max_value
        )
        self.progress.pack(side=tk.LEFT, padx=(10, 0))

        self.max_value = max_value
        self.label_text = label

    def update(self, value):
        """Function to update the visual of status bar based on current value
            Args: value - current value of a stat.
        """
        self.progress['value'] = value
        self.label.config(text=f"{self.label_text}: {int(value)}")


        if value > 80:
            style = "red.Horizontal.TProgressbar" if self.label_text in ["Głód", "Nuda"] else "green.Horizontal.TProgressbar"
        elif value > 30:
            style= "yellow.Horizontal.TProgressbar"
        else:
            style = "green.Horizontal.TProgressbar" if self.label_text in ["Głód", "Nuda"] else "red.Horizontal.TProgressbar"

        self.progress.config(style=style)


class SelectPet:
    """Class SelectPet is a class used to control showing of window used to select which pet to take care of"""
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Choose Your Pet")
        self.dialog.geometry("600x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        title_label = ttk.Label(self.dialog, text="Choose Your Pet!", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        pet_frame = ttk.Frame(self.dialog)
        pet_frame.pack(pady=20)

        pets = ["Pies", "królik", "Kot", "Ptak"]

        self.preview_images = {}
        for pet in pets:
            try:
                image_path = f"images/{pet.lower()}.png"
                if os.path.exists(image_path):
                    photo = tk.PhotoImage(file=image_path)
                    if photo.width() > 80 or photo.height() > 80:
                        factor = max(photo.width() // 80, photo.height() // 80, 1)
                        photo = photo.subsample(factor, factor)
                    self.preview_images[pet.lower()] = photo
            except Exception as e:
                print(f"nie załadowano {pet}: {e}")

        i = 0
        for pet in pets:
            frame = ttk.Frame(pet_frame)
            frame.grid(row=0, column=i, padx=15, pady=10)

            preview_canvas = tk.Canvas(frame, width=100, height=100, bg="lightgray", relief=tk.RAISED, bd=2)
            preview_canvas.pack()

            if pet.lower() in self.preview_images:
                preview_canvas.create_image(50, 50, image=self.preview_images[pet.lower()], anchor=tk.CENTER)
            else:
                preview_canvas.create_text(50, 50, text=pet, font=("Arial", 24), anchor=tk.CENTER)

            preview_canvas.bind("<Button-1>", lambda l, n=pet.lower(): self.select_pet(n))

            name_label = ttk.Label(frame, text=pet, font=("Arial", 10, "bold"))
            name_label.pack(pady=(5, 0))

            click_label = ttk.Label(frame, text="Click to select", font=("Arial", 8), foreground="gray")
            click_label.pack()
            i += 1


        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

    def select_pet(self, pet_type):
        self.result = pet_type
        self.dialog.destroy()

    def on_close(self):
        self.dialog.destroy()


class SelectAct:
    """Class SelectAct is a class used to control showing of window used to select which action(feeding or playing) to take"""
    def __init__(self, parent, title, options):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))

        title_label = ttk.Label(self.dialog, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=20)

        options_frame = ttk.Frame(self.dialog)
        options_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        for option, description in options.items():
            frame = ttk.Frame(options_frame)
            frame.pack(fill=tk.X, padx=20, pady=10)

            btn = ttk.Button(
                frame,
                text=option.capitalize(),
                command=lambda o=option: self.select_option(o),
                width=15
            )
            btn.pack(side=tk.LEFT)

            desc_label = ttk.Label(frame, text=description, font=("Arial", 10))
            desc_label.pack(side=tk.LEFT, padx=(15, 0))

        cancel_frame = ttk.Frame(self.dialog)
        cancel_frame.pack(pady=20)

        cancel_btn = ttk.Button(cancel_frame, text="Cancel", command=self.on_close)
        cancel_btn.pack()

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

    def select_option(self, option):
        self.result = option
        self.dialog.destroy()

    def on_close(self):
        self.dialog.destroy()


class Simulator:
    """Class Simulator controls how the main window is viewed"""
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Pet Simulator")
        self.root.geometry("800x600")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("red.Horizontal.TProgressbar", background='red')
        self.style.configure("yellow.Horizontal.TProgressbar", background='yellow')
        self.style.configure("green.Horizontal.TProgressbar", background='green')
        self.status_label = None
        self.canvas = None
        self.happinessbar = None
        self.boredombar = None
        self.hungerbar = None
        self.pet_info_label = None
        self.playbutton = None
        self.feedbutton = None
        self.pet = None
        self.ui()
        self.select_pet()

        if self.pet:
            self.start()

    def ui(self):
        """Function used to set up user interface of the main window"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.feedbutton = ttk.Button(control_frame, text="Nakarm", command=self.show_food)
        self.feedbutton.pack(side=tk.LEFT, padx=(0, 10))

        self.playbutton = ttk.Button(control_frame, text="Pobaw się", command=self.show_fun)
        self.playbutton.pack(side=tk.LEFT)

        self.pet_info_label = ttk.Label(control_frame, text="Zwierzak", font=("Arial", 12, "bold"))
        self.pet_info_label.pack(side=tk.RIGHT)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.hungerbar = StatusBar(status_frame, "Głód", "red")
        self.hungerbar.frame.pack(fill=tk.X, pady=2)

        self.boredombar = StatusBar(status_frame, "Nuda", "blue")
        self.boredombar.frame.pack(fill=tk.X, pady=2)

        self.happinessbar = StatusBar(status_frame, "Samopoczucie", "green")
        self.happinessbar.frame.pack(fill=tk.X, pady=2)

        self.canvas = tk.Canvas(main_frame, bg="lightgreen", relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(main_frame, text="Zaopiekuj się zwierzakiem!", font=("Arial", 10))
        self.status_label.pack(pady=(10, 0))

        self.canvas.after(100, self.background)

    def background(self):
        """Function used to control the way a background is displayed"""
        if self.canvas.winfo_width() > 1:

            self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height() // 3, fill="lightblue", outline="", tags="background")

            for _ in range(25):
                x = random.randint(0, self.canvas.winfo_width())
                y = random.randint(self.canvas.winfo_height() // 3, self.canvas.winfo_height())
                size = random.randint(15, 35)
                self.canvas.create_oval(x - size, y - size, x + size, y + size, fill="darkgreen", outline="", tags="background")

    def select_pet(self):
        """Function used to show the pet selection window"""
        dialog = SelectPet(self.root)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            canvas_width = 800
            canvas_height = 400
            self.pet = Animal(dialog.result, self.canvas, canvas_width // 2, canvas_height // 2)
            self.pet_info_label.config(text=f"Futrzak: {dialog.result.capitalize()}")


        else:
            self.root.quit()

    def show_food(self):
        """Function used to control what is displayed in food selection window"""
        if not self.pet:
            return

        options = {
            "Przekąska": "Szybka szamka",
            "Obiad": "Na większy głód",
            "Królewska uczta": "Na prawdziwe gastro"
        }

        dialog = SelectAct(self.root, "Co wpadnie na stół?", options)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.pet.feed(dialog.result)
            self.status_label.config(text=f"{self.pet.type} dostał {dialog.result}")

    def show_fun(self):
        """Function used to control what is displayed in play selection window"""
        if not self.pet:
            return

        options = {
            "Na odwal": "Dziś ci się nie chce...",
            "Z życiem": "Nie ma to jak chwile z futrzakiem!",
            "Do upadku": "Lepiej być nie może!"
        }

        dialog = SelectAct(self.root, "Jak się dziś pobawimy?", options)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.pet.play(dialog.result)
            self.status_label.config(text=f"Playing with your {self.pet.type} for a {dialog.result} session!")

    def update_bars(self):
        """Function used to update all status bars"""
        if self.pet:
            self.hungerbar.update(self.pet.hunger)
            self.boredombar.update(self.pet.boredom)
            self.happinessbar.update(self.pet.happiness)

            # Update status message based on pet condition
            if self.pet.hunger > 80:
                self.status_label.config(text=f"{self.pet.type} jest bardzo głodny", foreground="red")
            elif self.pet.boredom > 80:
                self.status_label.config(text=f"{self.pet.type} jest bardzo znudzony", foreground="blue")
            elif self.pet.happiness > 80:
                self.status_label.config(text=f"{self.pet.type} jest szczęsliwy", foreground="green")
            else:
                self.status_label.config(text=f"{self.pet.type} jest z nim git", foreground="black")

    def start(self):
        """Function starting the loop in which the game will be running"""

        def game_loop():
            if self.pet:
                self.pet.update()
                self.update_bars()

            self.root.after(50, game_loop)  # 20 FPS

        game_loop()

    def run(self):
        """Function starting the application"""

        self.root.mainloop()


def main():
    """Main function to execute the script."""
    app = Simulator()
    app.run()


if __name__ == "__main__":
    main()
