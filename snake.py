from tkinter import *
import pygame
from PIL import Image, ImageTk
from random import randint
from mysql.connector import connect, Error

pygame.mixer.init()


def playmusic():
    pygame.mixer.music.load("D:/Final_project/Lib/assets/audio/snake.mp3")
    pygame.mixer.music.play(loops=0)


playmusic()


def startgame():
    setnewbg()
    stopmusic()
    set_max_score()
    create_objects()
    movesnake()
    perform_actions()
    check_collisions()
    food_collision()
    set_new_food_position()


def stopmusic():
    pygame.mixer.music.stop()


def setnewbg():
    my_canvas1.delete("all")
    bg2 = PhotoImage(file="D:/Final_project/Lib/assets/images/background2.png")
    my_canvas1.create_image(0, 0, image=bg2, anchor="nw")
    my_canvas1.image = bg2


def create_objects():
    global highest_score
    my_canvas1.create_text(60, 15, text=f" Score:{score}", tag="score", fill="black", font=8)
    for x_position, y_position in snake_positions:
        my_canvas1.create_image(x_position, y_position, image=snakebody, tag="snake")
    my_canvas1.create_image(food_position, image=food, tag="food")
    my_canvas1.create_rectangle(10, 30, 750, 390, outline="#525d69")
    my_canvas1.create_text(680, 15, text=f" Best Score:{highest_score}", tag="highest_score", fill="black", font=8)


def movesnake():
    global snake_positions
    global direction
    head_x_position, head_y_position = snake_positions[0]
    new_head_position = []

    if direction == "Left":
        new_head_position = (head_x_position - inc, head_y_position)
    elif direction == "Right":
        new_head_position = (head_x_position + inc, head_y_position)
    elif direction == "Down":
        new_head_position = (head_x_position, head_y_position + inc)
    elif direction == "Up":
        new_head_position = (head_x_position, head_y_position - inc)

    snake_positions = [new_head_position] + snake_positions[:-1]

    for segment, position in zip(my_canvas1.find_withtag("snake"), snake_positions):
        my_canvas1.coords(segment, position)


def food_collision():
    global snake_positions
    global score
    global food_position
    global snakebody
    global highest_score
    if snake_positions[0] == food_position:
        score += 1
        snake_positions.append(snake_positions[-1])
        my_canvas1.create_image(*snake_positions[-1], image=snakebody, tag="snake")
        food_position = set_new_food_position()
        my_canvas1.coords(my_canvas1.find_withtag("food"), *food_position)
        score_tag = my_canvas1.find_withtag("score")
        my_canvas1.itemconfigure(score_tag, text=f"Score: {score}", tag="score")
        beepsound.play()
        if highest_score < score:
            best_score_tag = my_canvas1.find_withtag("highest_score")
            my_canvas1.itemconfigure(best_score_tag, text=f"Best Score: {score}", tag="highest_score")


def key_press(e):
    global direction
    new_direction = e.keysym

    all_directions = ("Up", "Down", "Left", "Right")
    opposites = ({"Up", "Down"}, {"Left", "Right"})

    if (
            new_direction in all_directions
            and {new_direction, direction} not in opposites
    ):
        direction = new_direction


def check_collisions():
    head_x_position, head_y_position = snake_positions[0]
    return (head_x_position == 20
            or head_x_position == 740
            or head_y_position == 40
            or head_y_position == 380
            or (head_x_position, head_y_position) in snake_positions[1:]
            )


def perform_actions():
    if check_collisions():
        end_game()
    else:
        food_collision()
        movesnake()
        window.after(game_speed, perform_actions)


def set_new_food_position():
    while True:
        x_position = randint(3, 35) * inc
        y_position = randint(5, 18) * inc
        current_food_position = (x_position, y_position)

        if current_food_position not in snake_positions:
            return current_food_position


def restart_game():
    global snake_positions, score, direction, food_position

    direction = "Right"
    score = 0
    snake_positions = [(100, 100), (80, 100), (60, 100)]
    food_position = (200, 200)
    startgame()


def update_score():
    global score
    try:
        with connect(
                host="localhost",
                user="root",
                password="090197",
                database="bestscore"
        ) as connection:

            get_score_query = "SELECT * FROM best_score"
            with connection.cursor() as cursor:
                cursor.execute(get_score_query)
                scores = cursor.fetchall()
                if len(scores) == 0:
                    insert_query = f"INSERT INTO best_score VALUES({score})"
                    cursor.execute(insert_query)
                    connection.commit()
                else:
                    get_max_query = "SELECT MAX(Best_Score) FROM best_score"
                    cursor.execute(get_max_query)
                    db_max_score = cursor.fetchall()
                    current_highest_score = db_max_score[0]
                    max_value = int(current_highest_score[0])
                    if max_value < score:
                        insert_query = f"INSERT INTO best_score VALUES({score})"
                        cursor.execute(insert_query)
                        connection.commit()

    except Error as e:
        print(e)


def end_game():
    global score
    update_score()
    my_canvas1.delete("all")
    bg3 = PhotoImage(file="D:/Final_project/Lib/assets/images/background3.png")
    my_canvas1.image = bg3
    my_canvas1.create_image(0, 0, image=bg3, anchor="nw")
    my_canvas1.create_text(my_canvas1.winfo_width() / 2,
                           my_canvas1.winfo_height() / 2,
                           text=f"Game over! You scored {score}!",
                           fill="#000",
                           font=("Halevica", 25)
                           )
    restart_button = Button(window, width=10, height=0, text="Restart", font=('Halevica', 15), command=restart_game)
    my_canvas1.create_window(290, 300, anchor='center', window=restart_button)
    end_button = Button(window, width=10, height=0, text="End", font=('Halevica', 15), command=window.destroy)
    my_canvas1.create_window(480, 300, anchor='center', window=end_button)
    gameover.play()


def set_max_score():
    global highest_score
    try:
        with connect(
                host="localhost",
                user="root",
                password="090197",
                database="bestscore"
        ) as connection:
            extract_db = "SELECT MAX(Best_Score) FROM best_score"
            with connection.cursor() as cursor:
                cursor.execute(extract_db)
                the_best = cursor.fetchall()
                content = the_best[0][0]
                if content is not None:
                    highest_score = int(content)
    except Error as e:
        print(e)


window = Tk()
window.title('SNAKE Game')
window.geometry("760x400")
window.resizable(False, False)

beepsound = pygame.mixer.Sound('D:/Final_project/Lib/assets/audio/beep.wav')
gameover = pygame.mixer.Sound('D:/Final_project/Lib/assets/audio/gameover.wav')

score = 0
highest_score = 0
inc = 20
mps = 15
game_speed = 3000 // mps
direction = "Right"
window.bind_all("<Key>", key_press)

bg1 = PhotoImage(file="D:/Final_project/Lib/assets/images/poza.png")

snake_body_image = Image.open("D:/Final_project/Lib/assets/images/snake.png")
snakebody = ImageTk.PhotoImage(snake_body_image)

food_image = Image.open("D:/Final_project/Lib/assets/images/food.png")
food = ImageTk.PhotoImage(food_image)

snake_positions = [(100, 100), (80, 100), (60, 100)]
food_position = (200, 200)

my_canvas1 = Canvas(window, width=760, height=400)
my_canvas1.pack(fill="both", expand=True)
my_canvas1.create_image(0, 0, image=bg1, anchor="nw")

start_button = Button(window, width=10, height=0, text="Start", font=('Halevica', 15), command=startgame)
exit_button = Button(window, width=10, height=0, text="Exit", font=('Halevica', 15), command=window.destroy)

start_button_window = my_canvas1.create_window(300, 350, anchor='center', window=start_button)
exit_button_window = my_canvas1.create_window(460, 350, anchor='center', window=exit_button)

window.mainloop()
