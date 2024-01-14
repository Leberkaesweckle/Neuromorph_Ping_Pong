import pygame
import numpy as np

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)
pygame.display.set_caption("Pong")

clock = pygame.time.Clock() 
FPS = 60
ball_blinking = False
blinking_frequency_ball = 10

# Striker class

def get_camera_position():
	return 30


######################################################
# Game objects
######################################################
class Striker:
	# Take the initial position, dimensions, speed and color of the object
	def __init__(self, posx, posy, width, height, speed, color):
		self.posx = posx
		self.posy = posy
		self.width = width
		self.height = height
		self.speed = speed
		self.color = color
		# Rect that is used to control the position and collision of the object
		self.playerRect = pygame.Rect(posx, posy, width, height)
		# Object that is blit on the screen
		self.player = pygame.draw.rect(screen, self.color, self.playerRect)

	# Used to display the object on the screen
	def display(self):
		self.player = pygame.draw.rect(screen, self.color, self.playerRect)

	def update(self, yFac):
		self.posy = self.posy + self.speed*yFac

		# Restricting the striker to be below the top surface of the screen
		if self.posy <= 0:
			self.posy = 0
		# Restricting the striker to be above the bottom surface of the screen
		elif self.posy + self.height >= HEIGHT:
			self.posy = HEIGHT-self.height

		# Updating the rect with the new values
		self.playerRect = (self.posx, self.posy, self.width, self.height)

	def update_absolute_position(self, yPosFract):
		self.posy = int(yPosFract * HEIGHT) 
		self.posy = np.clip(self.posy, 0, 1)

		# Updating the rect with the new values
		self.playerRect = (self.posx, self.posy, self.width, self.height)

		return

	def displayScore(self, text, score, x, y, color):
		text = font20.render(text+str(score), True, color)
		textRect = text.get_rect()
		textRect.center = (x, y)

		screen.blit(text, textRect)

	def getRect(self):
		return self.playerRect

class Ball:
	def __init__(self, posx, posy, radius, speed, color, blink_frequency):
		self.posx = posx
		self.posy = posy
		self.radius = radius
		self.speed = speed
		self.color = color
		self.xFac = 1
		self.yFac = -1
		self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)
		self.firstTime = 1
		self.blink_frequency = blink_frequency  # Controls the blinking speed
		self.blink_counter = 0
		self.is_visible = True  # Controls the visibility of the ball

	def display(self):
		# Only draw the ball if it's visible
		if self.is_visible:
			self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)
	
	def update_blink(self):
		# Increment the blink counter
		self.blink_counter += 1

		# Toggle visibility based on the frequency
		if self.blink_counter >= self.blink_frequency:
			self.is_visible = not self.is_visible
			self.blink_counter = 0

	def update(self):
		self.posx += self.speed*self.xFac
		self.posy += self.speed*self.yFac

		# If the ball hits the top or bottom surfaces, 
		# then the sign of yFac is changed and 
		# it results in a reflection
		if self.posy <= 0 or self.posy >= HEIGHT:
			self.yFac *= -1

		if self.posx <= 0 and self.firstTime:
			self.firstTime = 0
			return -1
		elif self.posx >= WIDTH and self.firstTime:
			self.firstTime = 0
			return 1
		else:
			return 0

	def reset(self):
		self.posx = WIDTH//2
		self.posy = HEIGHT//2
		self.xFac *= -1
		self.firstTime = 1

	# Used to reflect the ball along the X-axis
	def hit(self):
		self.xFac *= -1

	def getRect(self):
		return self.ball

######################################################
# UI elements
######################################################	
class Button:
	def __init__(self, color, x, y, width, height, text=''):
		self.color = color
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text

	def draw(self, screen, outline=None):
		# Call this method to draw the button on the screen
		if outline:
			pygame.draw.rect(screen, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
			
		pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)
		
		if self.text != '':
			font = pygame.font.SysFont('arial', 20)
			text = font.render(self.text, 1, (0,0,0))
			screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

	def isOver(self, pos):
		# Pos is the mouse position or a tuple of (x,y) coordinates
		if pos[0] > self.x and pos[0] < self.x + self.width:
			if pos[1] > self.y and pos[1] < self.y + self.height:
				return True
		return False

class ToggleSwitch:
	def __init__(self, x, y, width, height, is_on=False, text_on='', text_off=''):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.is_on = is_on
		self.text_on = text_on
		self.text_off = text_off

	def draw(self, screen, outline=None):
		if outline:
			pygame.draw.rect(screen, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
		if self.is_on:
			pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
			if self.text_on != '':
				font = pygame.font.SysFont('arial', 20)
				text = font.render(self.text_on, 1, (0,0,0))
				screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
		else:
			pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
			if self.text_off != '':
				font = pygame.font.SysFont('arial', 20)
				text = font.render(self.text_off, 1, (0,0,0))
				screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = event.pos
			if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
				self.is_on = not self.is_on

######################################################
# Initializing the game
######################################################	

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
CONTROL_AREA_WIDTH = 200  # Zusätzlicher Bereich für Steuerungselemente
TOTAL_WIDTH = WIDTH + CONTROL_AREA_WIDTH  # Gesamtbreite inklusive Steuerungsbereich
screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Game Manager
def main():
	running = True

	# Defining the objects
	player1 = Striker(20, 0, 10, 100, 10, GREEN)
	player2 = Striker(WIDTH-30, 0, 10, 100, 8, GREEN)
	ball = Ball(posx=WIDTH//2, posy=HEIGHT//2, radius=7, speed=7, color=WHITE, blink_frequency=blinking_frequency_ball)

	# Buttons innerhalb des Steuerungsbereichs positionieren
	toggleSwitchSingleplayer = ToggleSwitch(WIDTH + 50, HEIGHT-150, 100, 50, is_on=True, text_on='Singleplayer', text_off='Multiplayer')
	toggleSwitchCameraControl = ToggleSwitch(WIDTH + 50, HEIGHT-90, 100, 50, is_on=True, text_on='Camera Control', text_off='Keyboard Control')
	#buttonUp = Button(GREEN, WIDTH + 50, HEIGHT-150, 100, 50, 'UP')
	#buttonDown = Button(GREEN, WIDTH + 50, HEIGHT-90, 100, 50, 'DOWN')

	player1Score, player2Score = 0, 0
	player1YFac = 0
	player2YFac = 0

	######################################################
	# Game loop
	######################################################	
	while running:
		screen.fill(BLACK)

		# Drawing of control area
		pygame.draw.rect(screen, WHITE, (WIDTH, 0, CONTROL_AREA_WIDTH, HEIGHT))

		# blinking of objects
		if ball_blinking:
			ball.update_blink()

		# Event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					player1YFac = -1
				if event.key == pygame.K_DOWN:
					player1YFac = 1
				if event.key == pygame.K_w:
					player2YFac = -1
				if event.key == pygame.K_s:
					player2YFac = 1
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					player1YFac = 0
				if event.key == pygame.K_w or event.key == pygame.K_s:
					player2YFac = 0
			toggleSwitchSingleplayer.handle_event(event)          
			toggleSwitchCameraControl.handle_event(event)   

		# Collision detection
		if pygame.Rect.colliderect(ball.getRect(), player1.getRect()) or pygame.Rect.colliderect(ball.getRect(), player2.getRect()):
			ball.hit()

		# Updating the objects
		point = ball.update()  # Ball.update() sollte nur einmal aufgerufen werden
		
		# Paddle control
		if toggleSwitchSingleplayer.is_on:
			########################
			# Singleplayer
			########################

			# Player 1
			if toggleSwitchCameraControl.is_on:
				camera_player_1_pos = get_camera_position() #fraction between 0 and 1
				player1.update_absolute_position(camera_player_1_pos)
			else:
				player1.update(player1YFac)

			# AI-movement based on ball position
			if ball.posy > player2.posy + player2.height / 2:
				player2.update(1)
			elif ball.posy < player2.posy:
				player2.update(-1)
				
		else:
			########################
			# Multiplayer
			########################
			if toggleSwitchCameraControl.is_on:
				# Player 1
				camera_player_1_pos = get_camera_position() #fraction between 0 and 1
				player1.update_absolute_position(camera_player_1_pos)

				# Player 2
				camera_player_2_pos = get_camera_position() #fraction between 0 and 1
				player2.update_absolute_position(camera_player_2_pos)
			else:
				player1.update(player1YFac)
				player2.update(player2YFac)
			pass

		# Count points and reset the ball 
		if point != 0:
			if point == 1:
				player1Score += 1
			elif point == -1:
				player2Score += 1
			ball.reset()

		# Displaying the objects on the screen
		player1.display()
		player2.display()
		ball.display()

		# Drawing the ui elements
		#buttonUp.draw(screen, outline=True)
		#buttonDown.draw(screen, outline=True)
		toggleSwitchSingleplayer.draw(screen, outline=True)
		toggleSwitchCameraControl.draw(screen, outline=True)       

		# Displaying the scores
		if toggleSwitchSingleplayer.is_on:
			player1.displayScore("Player: ", player1Score, WIDTH + 100, 20, BLACK)
			player1.displayScore("AI: ", player2Score, WIDTH + 100, 60, BLACK)
		else:
			player1.displayScore("Player 1: ", player1Score, WIDTH + 100, 20, BLACK)
			player1.displayScore("Player 2: ", player2Score, WIDTH + 100, 60, BLACK)

		pygame.display.update()
		clock.tick(FPS)

if __name__ == "__main__":
	main()
	pygame.quit()