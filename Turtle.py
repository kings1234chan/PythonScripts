import turtle
import random

screen = turtle.Screen()
screen.title("Turtle Racing Game")
screen.bgcolor("#9C0000")
screen.setup(width=800, height=600)
screen.tracer(0)  # Turn off automatic updates for instant setup

# Staff setting
staff = turtle.Turtle()
staff.shape("turtle")
staff.speed(0)
staff.penup()
staff.pensize(2)
staff.pencolor("#FFFFFF")

# Finish line
staff.goto(300, 200)
staff.right(90)
staff.pendown()
staff.forward(400)
staff.penup()

# Start Line
staff.goto(-300, 200)
staff.pendown()
staff.forward(400)
staff.penup()

# Staff sit
staff.goto(-280, 200)

# Audience (Created efficiently with tracer off)
audience_color = ["green", "blue", "red", "yellow", "purple"]
audience_row = [250, -250]
for _ in range(100):
    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.color(random.choice(audience_color))
    t.penup()
    position = random.choice(audience_row)
    if position == 250:
        t.right(90)
    else:
        t.left(90)
    t.goto(random.randint(-200, 220), position + random.randint(-5, 5))
    t.showturtle()

screen.tracer(1)  # Turn updates back on for gameplay

# Player 1 (Black)
player1 = turtle.Turtle()
player1.shape("turtle")
player1.shapesize(stretch_wid=2, stretch_len=2)  # Adjusted size for better proportions
player1.color("black")
player1.penup()
player1.goto(-350, 100)
player1.pendown()

# Player 2 (Red)
player2 = turtle.Turtle()
player2.shape("turtle")
player2.shapesize(stretch_wid=2, stretch_len=2)
player2.color("red")
player2.penup()
player2.goto(-350, -100)
player2.pendown()

# Player 3 (Blue)
player3 = turtle.Turtle()
player3.shape("turtle")
player3.shapesize(stretch_wid=2, stretch_len=2)
player3.color("blue")
player3.penup()
player3.goto(-350, 0)
player3.pendown()

gameOver = False

def move_p1():
    global gameOver
    if not gameOver:
        player1.forward(30)
        if player1.xcor() >= 300:
            declare_winner("Player 1 (Black)")

def move_p2():
    global gameOver
    if not gameOver:
        player2.forward(30)
        if player2.xcor() >= 300:
            declare_winner("Player 2 (Red)")

def move_p3():
    global gameOver
    if not gameOver:
        player3.forward(30)
        if player3.xcor() >= 300:
            declare_winner("Player 3 (Blue)")
            
def declare_winner(player_name):
    global gameOver
    gameOver = True
    staff.penup()
    staff.goto(-120, 0)
    staff.pencolor("white")
    staff.write(f"{player_name} Wins!", font=("Arial", 20, "bold"))
    screen.update()

# Key bindings
screen.listen()
screen.onkey(move_p1, "a")
screen.onkey(move_p2, "1")
screen.onkey(move_p3, "l")

screen.mainloop()