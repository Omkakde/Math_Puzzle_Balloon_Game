import random
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import sys

def generate_math_question():
    """Generates a random math question with multiple choice options."""
    operations = ["+", "-", "*"]
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 10)
    operation = random.choice(operations)

    if operation == "+":
        correct_answer = num1 + num2
    elif operation == "-":
        correct_answer = num1 - num2
    else:
        correct_answer = num1 * num2

    # Generate incorrect answer options that are +/- 5 from the correct answer
    incorrect_options = [
        correct_answer + random.randint(-5, 5),
        correct_answer - random.randint(-5, 5),
    ]

    # Ensure all options are unique
    while len(set(incorrect_options + [correct_answer])) != 3:
        incorrect_options.append(random.randint(1, 20))

    random.shuffle(incorrect_options)

    question = f"{num1} {operation} {num2} = ?"
    options = [f"{option}" for option in incorrect_options]
    options.append(f"{correct_answer}")
    random.shuffle(options)

    return question, options, correct_answer

def draw_explosion(surface, explosion_pos):
    # Explosion animation
    colors = [(255, 255, 0), (255, 255, 100), (255, 255, 150), (255, 255, 200)]
    explosion_radius = 10
    max_radius = 60
    while explosion_radius <= max_radius:
        for color in colors:
            pygame.draw.circle(surface, color, explosion_pos, explosion_radius)
            pygame.display.flip()
            pygame.time.delay(10)
            surface.fill((255, 255, 255))  # Clear the explosion
            explosion_radius += 5

# Initialize
pygame.init()

# Create Window/Display
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Math Balloon Pop")

# Initialize Clock for FPS
fps = 30
clock = pygame.time.Clock()

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width
cap.set(4, 720)  # height

# Images
imgBalloon = pygame.image.load(r'D:\Projects\MathBalloonPopGame (1)\BalloonPopGame\Resources\BalloonRed.png').convert_alpha()

rectBalloon = imgBalloon.get_rect()
rectBalloon.x, rectBalloon.y = 500, 300

# Variables
speed = 5  # Increased speed
score = 0
startTime = None  # Updated after "Start Game" button is clicked
totalTime = 60
img = None  # Initialize img outside the loop

# Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Space between balloons
space_between_balloons = 20
start_button_rect = pygame.Rect(500, 400, 200, 50)
def resetBalloon():
    rectBalloon.x = random.randint(100, img.shape[1] - 100)
    rectBalloon.y = img.shape[0] + 50

# Front page loop
front_page = True
player_name = ""
while front_page:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            front_page = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                front_page = False  # Transition to game loop
                startTime = time.time()  # Start the timer
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                player_name += event.unicode

    window.fill((255, 255, 255))  # White background

    # Draw player name input box
    font = pygame.font.Font(None, 30)
    textPlayerName = font.render('Player Name:', True, (255, 128, 0))
    window.blit(textPlayerName, (300, 300))
    pygame.draw.rect(window, (255, 204, 153), pygame.Rect(450, 300, 300, 30))  # Input box
    textInput = font.render(player_name, True, (255, 255, 255))
    window.blit(textInput, (455, 305))

    # Draw start button
    pygame.draw.rect(window, (255, 204, 153), start_button_rect)
    textStart = font.render('Start Game', True, (255, 128, 0))
    window.blit(textStart, (start_button_rect.x + 50, start_button_rect.y + 15))

    pygame.display.update()
    clock.tick(fps)

# Generate the first math question
currentQuestion, options, correct_answer = generate_math_question()

# Define replay button rectangle
replay_button_rect = pygame.Rect(350, 400, 200, 50)
# Define exit button rectangle
exit_button_rect = pygame.Rect(650, 400, 200, 50)

# Main loop
start = True
while start:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if player clicked the replay button
            if replay_button_rect.collidepoint(event.pos):
                # Reset game variables
                score = 0
                speed = 5
                startTime = time.time()
                currentQuestion, options, correct_answer = generate_math_question()
            # Check if player clicked the exit button
            elif exit_button_rect.collidepoint(event.pos):
                with open("scores.txt", "a") as file:
                    file.write(f"Player: {player_name}, Score: {score}, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                pygame.quit()
                sys.exit()

    # Apply Logic
    if startTime is not None:
        timeRemain = int(totalTime - (time.time() - startTime))
        if timeRemain < 0:
            window.fill((255, 255, 255))
            font = pygame.font.Font(None, 50)  # Using default font
            textScore = font.render(f'Your Score: {score}', True, (50, 50, 255))
            textGameOver = font.render('Game Over', True, (50, 50, 255))
            window.blit(textScore, (450, 350))
            window.blit(textGameOver, (500, 275))

            # Draw replay button
            pygame.draw.rect(window, (0, 0, 0), replay_button_rect)
            font_replay = pygame.font.Font(None, 30)
            textReplay = font_replay.render('Replay', True, (255, 255, 255))
            window.blit(textReplay, (replay_button_rect.x + 50, replay_button_rect.y + 15))

            # Draw exit button
            pygame.draw.rect(window, (0, 0, 0), exit_button_rect)
            textExit = font_replay.render('Exit', True, (255, 255, 255))
            window.blit(textExit, (exit_button_rect.x + 65, exit_button_rect.y + 15))

        else:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            hands, img = detector.findHands(img, flipType=False)

            rectBalloon.y -= speed  # Move the balloon up
            # check if balloon has reached the top without pop
            if rectBalloon.y < 0:
                resetBalloon()
                speed += 1

            if hands:
                hand = hands[0]
                x, y = hand['lmList'][8][0:2]
                if rectBalloon.collidepoint(x, y) or any(option_rect.collidepoint(x, y) for option_rect in option_rects):
                    resetBalloon()
                    selected_option = None
                    for i, option_rect in enumerate(option_rects):
                        if option_rect.collidepoint(x, y):
                            selected_option = options[i]
                            draw_explosion(window, (option_rect.x + option_rect.width // 2, option_rect.y + option_rect.height // 2))
                            break

                    if selected_option is not None and selected_option == str(correct_answer):
                        score += 10
                        currentQuestion, options, correct_answer = generate_math_question()

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB = np.rot90(imgRGB)
            frame = pygame.surfarray.make_surface(imgRGB).convert()
            frame = pygame.transform.flip(frame, True, False)
            window.blit(frame, (0, 0))

            # Draw Balloons with Options
            option_rects = []
            for i, option in enumerate(options):
                balloon_x = 100 + i * (200 + space_between_balloons)
                balloon_rect = pygame.Rect(balloon_x, rectBalloon.y, 150, 150)
                option_rects.append(balloon_rect)
                window.blit(imgBalloon, balloon_rect)
                font = pygame.font.Font(None, 30)  # Using default font
                textOption = font.render(str(option), True, (255, 255, 255))
                window.blit(textOption, (balloon_x + 40, rectBalloon.y + 50))

            window.blit(imgBalloon, rectBalloon)

            font = pygame.font.Font(None, 50)  # Using default font
            textScore = font.render(f'Score: {score}', True, (50, 50, 255))
            textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
            window.blit(textScore, (35, 35))
            window.blit(textTime, (1000, 35))

            # Show Math Question with Black Background
            question_rect = pygame.Rect(1000, 150, 250, 60)
            pygame.draw.rect(window, (0, 0, 0), question_rect)
            textQuestion = font.render(currentQuestion, True, (255, 255, 255))
            window.blit(textQuestion, (1000, 150))

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)

