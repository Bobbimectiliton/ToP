import pygame
import sys

from pygame import mixer 
from timeit import default_timer as timer

# Initialize Pygame
pygame.init()
mixer.init()

#Displayed Scores
score = 0
deaths = 0
start = timer()

#Audio Stuff
mixer.music.load('Wilhelm Scream - Sound Effect-[AudioTrimmer.com].mp3')
audio = True

#Images
Lava = pygame.transform.scale(pygame.image.load('Lava.png'), (40, 40))
Box = pygame.transform.scale(pygame.image.load('BrickTexture.png'), (40, 40))
WholeWall = pygame.transform.scale(pygame.image.load('WallWithTorch.png'),(1200,640))
Wall = pygame.transform.scale(pygame.image.load('WallBrick.png'),(40,40))

# Constants
BLOCK_SIZE = 40
PLAYER_SIZE = BLOCK_SIZE
SCREEN_WIDTH = 30 * BLOCK_SIZE
SCREEN_HEIGHT = 16 * BLOCK_SIZE
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1


# Colors
WHITE = (255, 255, 255)
BLUE = (2, 247, 239)
BLACK = (0,0,0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Game")


# Block Classes
class Block:
   def __init__(self, x, y, block_size):
       self.rect = pygame.Rect(x, y, block_size, block_size)
       self.image = None

   def loadImage(self, imagePath):
       self.image = imagePath.copy()
  
   def draw(self, screen, color):
       if self.image:
          screen.blit(self.image, self.rect) 
       else:
          pygame.draw.rect(screen, color, self.rect)
  
   def collide(self, player_rect):
       return self.rect.colliderect(player_rect)


class GroundBlock(Block):
   def draw(self, screen):
       super().loadImage(Box)
       super().draw(screen, GREEN)


class KillBlock(Block):
   def draw(self, screen):
       super().loadImage(Lava)
       super().draw(screen, RED)
  
   def collide(self, player_rect):
       global deaths
       if super().collide(player_rect):
           if audio:
            mixer.music.play()
           deaths+=1
           return True
       return False


class StartBlock(Block):
   def draw(self, screen):
       super().loadImage(Wall)
       super().draw(screen, BLACK)  # Draw start block in white


   def collide(self, player_rect):
       return False  # Start block doesn't collide with anything


# Player Class
class Player:
   def __init__(self, x, y, size):
       self.start_x = x
       self.start_y = y
       self.rect = pygame.Rect(x, y, size, size)
       self.x_velocity = PLAYER_SPEED
       self.y_velocity = 0
       self.on_ground = False
       self.jumping = False
  
   def move(self, blocks):
       # Horizontal Movement
       self.rect.x += self.x_velocity
       self.handle_horizontal_collisions(blocks)
      
       # Apply gravity before vertical movement
       self.apply_gravity()


       # Vertical Movement
       self.rect.y += self.y_velocity
       self.handle_vertical_collisions(blocks)


       # Auto-jump if space is held and on ground
       if self.on_ground and self.jumping:
           self.jump()


       # Check if player has fallen into a hole (below the screen)
       if self.rect.y > SCREEN_HEIGHT:
           #print("Fell into a hole")
           return True
       return False


   def handle_horizontal_collisions(self, blocks):
       for block in blocks:
           if block.collide(self.rect):
               if isinstance(block, KillBlock):
                   self.respawn()
                   return
               if self.x_velocity > 0:  # Moving right
                   self.rect.right = block.rect.left
                   self.x_velocity = -PLAYER_SPEED
               elif self.x_velocity < 0:  # Moving left
                   self.rect.left = block.rect.right
                   self.x_velocity = PLAYER_SPEED


   def handle_vertical_collisions(self, blocks):
       self.on_ground = False
       for block in blocks:
           if block.collide(self.rect):
               if isinstance(block, KillBlock):
                   self.respawn()
                   return
               if self.y_velocity > 0:  # Falling
                   self.rect.bottom = block.rect.top
                   self.y_velocity = 0
                   self.on_ground = True
               elif self.y_velocity < 0:  # Jumping
                   self.rect.top = block.rect.bottom
                   self.y_velocity = 0


   def jump(self):
       if self.on_ground:
           self.y_velocity = -JUMP_HEIGHT


   def apply_gravity(self):
       if not self.on_ground:
           self.y_velocity += GRAVITY


   def draw(self, screen):
       pygame.draw.rect(screen, BLUE, self.rect)


   def respawn(self):
       self.rect.x = self.start_x
       self.rect.y = self.start_y
       self.y_velocity = 0
       self.on_ground = False


# Function to create blocks from a level array
def create_blocks_from_level(level, block_size):
   blocks = []
   for y, row in enumerate(level):
       for x, cell in enumerate(row):
           if cell == 'g':
               blocks.append(GroundBlock(x * block_size, y * block_size, block_size))
           elif cell == 'r':
               blocks.append(KillBlock(x * block_size, y * block_size, block_size))
           elif cell == 's':
               blocks.append(StartBlock(x * block_size, y * block_size, block_size))
   return blocks


# Function to find the start block and set player position
def find_start_position(level, block_size):
   for y, row in enumerate(level):
       for x, cell in enumerate(row):
           if cell == 's':
               return x * block_size, (y+1) * block_size
   return 0, 0  # Default position if no start block is found


# Example levels (30x16 grid)
BADLEVEL = [
   "ggggggggggggg s   gggggggggggg",
   "                              ",
   "                              ",
   "                              ",
   "                              ",
   "                              ",
   "                              ",
   "      r                      g",
   "gggggggggggggggggggggggggggggg",
   "                              ",
   "          r         r         ",
   "                              ",
   "        g                     ",
   "        g             gg      ",
   "        ggg       ggggg       ",
   "           ggggggg            ",
]

BADDERLEVEL = [
   "gggggggggg    s    ggggggggggg",
   "gggggggggg         ggggggggggg",
   "g  gg                gggggg rg",
   "g                    ggg    rg",
   "                            rg",
   "                            rg",
   "                            rg",
   "                            rg",
   "gggggggggggggggggggggggggggggg",
   "gggggggggggggggggggggggggggggg",
   " gggggg     ggggggg   gggggggg",
   "   gg           gg        gg  ",
   "    g           g         g   ",
   "    g                         ",
   "                              ",
   "                              ",
]

level1001 = [
   "ggggggggggggggggggggggggg   sg",
   "g                       g    g",
   "g                            g",
   "g                            g",
   "g                             ",
   "g    r    r    r    r         ",
   "g gg   gg   gg   gg gggggggggg",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                            g",
   "grrrrrrrrrrrrrrrrrrrrrrrrrrrrg",
   "gggggggggggggggggggggggggggggg",
]


level0 = [
   "gggggggggggggggggggggggggggggg",
   " s    gggggggggggggggggggggggg",
   "      gggggg  gggggg   ggggggg",
   "ggg   g   gg  gggg       ggggg",
   "g g   g         gg       gg  g",
   "g               gg           g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                             ",
   "g                             ",
   "g                             ",
   "g  ggggggg        g    g      ",
   "gggggggggggggggggggrrrrggggggg",
   "gggggggggggggggggggggggggggggg",
]


level1 = [
  "ggggs  ggggggggggggggggggggggg",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g           r                g",
  "ggggggggggggggggggggg  ggggggg"
]


levelOne = [
  "ggggs  ggggggggggggggggggggggg",
  "g                            g",
  "g                            g",
  "gggggggggggggggggggggg       g",
  "g                            g",
  "g            ggggggggg       g",
  "gggggggg              gg   ggg",
  "g                            g",
  "g                            g",
  "g     gggggggggg   gggggggg  g",
  "g                    r       g",
  "g       gg    g      r       g",
  "g   gggg       ggggggggggggggg",
  "g                            g",
  "g          r                 g",
  "ggggggggggggggggggggg  ggggggg"
]

level2 = [
  "ggggggggggggggggggggggggs gggg",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                         gggg",
  "gr      r         r          g",
  "gr      r  g      r          g",
  "gggggg  gggggggggggggggggggggg"
]


level3 = [
  "gs ggggggggggggggggggggggggggg",
  "g  g                         g",
  "g  g                         g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                  rrrrrrr   g",
  "g            ggg             g",
  "g      ggg  g                g",
  "g     r              r       g",
  "g  ggg      g        r       g",
  "ggggggrrrrrrggggggggrrrggg  gg"
]

level4 = [
  "gs ggggggggggggggggggggggggggg",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                       r    g",
  "g                    gg r    g",
  "g      grg  ggr    ggg  r    g",
  "g           g           r    g",
  "ggggggggggggggggggggggggg   gg"]

level5 = [
  "gs ggggggggggggggggggggggggggg",
  "g  g                         g",
  "g  g                         g",
  "g  g                         g",
  "g  g                 g  r    g",
  "g  g               ggg  r    g",
  "g  g             ggggg  r    g",
  "g  g                    r    g",
  "g  g           ggggggg  r    g",
  "g  g         r          r    g",
  "g  g       g            r    g",
  "g  g     g              r    g",
  "g       r               r    g",
  "g     g                r     g",
  "g    r                 r     g",
  "ggggggggggggggggggggg  g    gg"]


level6 = [
  "gs ggggggggggggggggggggggggggg",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "ggggrrgggggg  grrrgrrrgrrrg  g",
  "g                         g  g",
  "g                            g",
  "g  ggggggggggggrrrgggggggggggg",
  "g  g                         g",
  "g  g                         g",
  "g  g                         g",
  "g                            g",
  "ggggg    g    g    g    grrrrg",
  "g   grrrrrrrrrrrrrrg         g",
  "gggggggggggggggggggggggg  gggg"]


level7 = [
  "ggggggggggggg  s ggggggggggggg",
  "g                            g",
  "g                            g",
  "g                            g",
  "g                            g",
  "g            ggg             g",
  "g            rrr             g",
  "g                            g",
  "g     grg         grg        g",
  "g                      grg   g",
  "g          grg               g",
  "g      grg          grg      g",
  "g                            r",
  "g            grg             r",
  "g  grg            grg        g",
  "g  rrrrrrrrrrrrrrrrrrrrrr    g"]


level8 = [
  "gs                           g",
  "g                            g",
  "ggggg                        g",
  "g      g                     g",
  "g                            g",
  "g         g                  g",
  "grrrrrrrrrrrrg    g    g     g",
  "g                      g     g",
  "g                      g     g",
  "g                            g",
  "g                            g",
  "g   grrrgrrrgggrrgggrrgggggggg",
  "g                            g",
  "g                            g",
  "g                            g",
  "ggggggggggggggggggggggggg    g"]


level9 = [
  "ggg s  ggggggggggggggggggggggg",
  "g                   r    r   g",
  "g                  r r  r r  g",
  "g                  rrr   rr  g",
  "g                  r r    r  g",
  "gggggrggg                r   g",
  "g                            g",
  "g          g                 g",
  "g          r   g             g",
  "g              r         gg  g",
  "g      rg          grgrgrrr  g",
  "g      rggggggggggggggggggg  g",
  "g                            g",
  "gg    ggg                    g",
  "gggrggggggrrgrrgggr          g",
  "ggggggggggggggggggg      rgggg"]
 
levelNine = [
   "g s gggggggggggggggggggggggggg",
   "g  g   g          g   g  g   g",
   "g  g   g ggg g g g g ggg ggg g",
   "g  g   g g g ggg ggg  g  g g g",
   "g  g   g ggg  g  g    g  g g g",
   "g                ggg         g",
   "g g g           g         g  g",
   "ggggggg  gg ggg g ggg gg g g g",
   "g g g g  g  g g g g g g  ggg g",
   "g g g g  gg ggg g ggg g    g g",
   "g                         g  g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g                            g",
   "ggggggggggggggggggggggg    ggg",
]


level10 = [
  "gsg                          r",
  "g g    ggggggggg     g       r",
  "g g            g  g  g       g",
  "g gg           grrrrrr   rgggg",
  "g g    g       grrrrrg       g",
  "g g     gg     g     g       g",
  "g g          gg      gggg    g",
  "g g      g   g               g",
  "g g         grg              g",
  "g ggg        r   ggggggggggggg",
  "g g     gg   g               g",
  "g g          g               g",
  "g g         grgggg  grrrrrrrrg",
  "g        gg  rg     g        g",
  "g            r               g",
  "gggggggrrrrrrrggggggggggg    g"]


level11 = [
   "gs ggggggggggggggggggggggggggg",
   "g  g                         g",
   "g  g       g     g g         g",
   "g  g    gg ggg g g g         g",
   "g  g    g  g g g g g         g",
   "g  g    gg g g g g g         g",
   "g  g                         g",
   "g  g                         g",
   "g  g                         g",
   "g  g                    gg   g",
   "g  g                 gg      g",
   "g                gg          g",
   "g            gg              g",
   "g        gg                  g",
   "g    gg                      g",
   "gggggrrrrrrrrrrrrrrrrrrrrg  gg",
]


levelFunkyAlya = [
   "g s gggggggggggggggggggggggggg",
   "g                            g",
   "g          r                 g",
   "g              gg            g",
   "g            gg  g  r        g",
   "g          gr     g          g",
   "g      r  gg       g         g",
   "g       g g        g         g",
   "g   ggg   g    gg  grgg g    g",
   "g   g g  gg  g g g    g      g",
   "g  gg gg  g    gg     g  g   g",
   "g g    grr     g      g      g",
   "g g   g g    g g      gr   g g",
   "gg   r r r     g       g     g",
   "r     r r              g g   g",
   "rrrrrrrrrrrrrrrrrrrrrrrg   ggg",
]


levelangela1 = [
  "g s rrrrrrrrrrrr         rrrrr",
  "g   grrrrrrrr            rrrrr",
  "g   grrrrrg              grrrr",
  "g   grrrrrg    ggrrgrgg  grrrr",
  "g   rrrrrrg       rrrrg  rrrrr",
  "g   rrrrrrrgg      grrg  grrrr",
  "r   grrrrrrrggg    grrr  grrrr",
  "r   grrrrrr        grrg  grrrr",
  "g   grrrrrg      ggrrrg  rrrrr",
  "g   rrrrrrg    gggrrrrr  grrrr",
  "g   rrrrrrg       rrrrg  grrrr",
  "r   grrrrrrgg      grrg  rrrrr",
  "r   grrrrrrrggg    grrr  grrrr",
  "g                  grrg   rrrr",
  "g                ggrrrg    grr",
  "ggggggggggggggggggrrrrg     rr",

]

levelangela2 = [
    "gs grrr     rrrggrrrrrrrr    g",
    "g                            g",
    "g                            g",
    "ggggggggrrgggggrggggggggggg  g",
    "g    rrrggrrrg    grrrrggrr  g",
    "g                            g",
    "g                            r",
    "g  gggggrggggggrrgggggggrggggg",
    "g  rrrggrrrggrrrrrggrrrrr    g",
    "g                            g",
    "r                            g",
    "ggggggrggggrggggggrggggggrg  g",
    "r    grrggrrrg    g    grrr  g",
    "r                            g",
    "r                            r",
    "r  rggggrggggggrrgggrrgggggggg",
]


level111 = [
   "gs  gggggggggggggggggggggggggg",
   "g                            g",
   "g                            g",
   "g                            g",
   "g             r      r       g",
   "gggggggggggggggggggggggggg   g",
   "g                            g",
   "g                            g",
   "g                            g",
   "g              r     r       g",
   "gggggggg   ggggggggggggggggggg",
   "g      g                     g",
   "g      g                     g",
   "g  g   g                     g",
   "g  g        r    r    r      g",
   "g  ggggggggggggggggggggggggggg",
]

level12 = [
    "gggggggggggggggggggggggggggggg",
    "gs    rrrrrrrrrrrrrrrr       g",
    "gg   g                       g",
    "g  gg                      g g",
    "g                          g g",
    "gg                    gg   g g",
    "g    g    rgrrrgrrrgrrrrrrrg g",
    "g  gg gg                   g g",
    "g rrrr                       g",
    "g                            g",
    "g   g                     gggg",
    "ggrrg   g   g   g   g   g    g",
    "g      grrrrrrrrrrrrrrrrrrrrrg",
    "g     g ggggggggggggggggg     ",
    "r                             ",
    "rggggggggggggggggggggggggggggg",
]

levelVladdyDaddy = [
   "gggggggggggggggggggggggggggggg",
   "s                            g",
   "                             g",
   "                             g",
   "ggggrrgggrrgggrrgggrrggg     g",
   "gggggggggggggggggggggggg     g",
   "gggggg                 grr   g",
   "gggggg                 ggg   g",
   "gggggg                       g",
   "gggggg                       g",
   "gggggg   g gg                g",
   "         g     gg            g",
   "         g         gg        g",
   "         g             gg    g",
   "         grrrrrrrrrrrrrrg    g",
   "gggggggggggggggggggggggggggggg",
]
TEST = [
   "gggggggggggggggggggggggggggggg",
   "gg        g        g         g",
   "gg        g        g         g",
   "gggg    g ggg    g ggg    g  g",
   "gg      g g      g g      g  g",
   "gg    ggg g    ggg g    ggg  g",
   "gggg    g ggg    g ggg    g  g",
   "gg      g g      g g      g  g",
   "gg    ggg g    ggg g    ggg  g",
   "gggg    g ggg    g ggg    g  g",
   "gg      g g      g        g  g",
   "gg    ggg g    ggg      ggg  g",
   "gggg    g ggg    ggggg  rgg  g",
   "g       g g      ggggg  rgg  g",
   "gs    ggg      ggggggr  rgg  g",
   "ggggggggggggggggggggggrrggg  g",
]

levels = [BADLEVEL, BADDERLEVEL, level1001, level0, level111, level1,levelOne, 
          level2,level3,level4,level5,level6,level7,level8,level9, levelNine, level10,level11, 
          levelFunkyAlya, levelangela1, levelangela2, levelVladdyDaddy]
current_level = 0


# Global variable to indicate transition
in_transition = False


def fade_to_black():
   for alpha in range(0, 256, 10):
       screen.fill(WHITE)
       for block in blocks:
           block.draw(screen)
       s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) 
       s.set_alpha(alpha)               
       s.fill(BLACK)          
       screen.blit(s, (0,0))   
       pygame.display.flip()
      
def fade_from_black():
   for alpha in range(256, -1, -10):
       screen.fill(WHITE)
       for block in blocks:
           block.draw(screen)
       s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) 
       s.set_alpha(alpha)               
       s.fill(BLACK)          
       screen.blit(s, (0,0))   
       pygame.display.flip()

def transition_screen():
   global in_transition
   in_transition = True

   fade_to_black()

   # Wait for a short period while the screen is black
   pygame.time.wait(500)  # Wait for 2 seconds before starting the next level

   transition_to_next_level()
  
   fade_from_black()

# Function to transition to the next level
def transition_to_next_level():
   global current_level, in_transition, blocks, score
   current_level = (current_level + 1) % len(levels)
   player.rect.x, player.rect.y = find_start_position(levels[current_level], BLOCK_SIZE)
   player.start_x, player.start_y = find_start_position(levels[current_level], BLOCK_SIZE)
   player.rect.y -= BLOCK_SIZE  # Position player above the screen to fall into the new level
   player.y_velocity = 0  # Reset player's velocity
   score+=1
   in_transition = False  # End transition
   blocks = create_blocks_from_level(levels[current_level], BLOCK_SIZE)

 
def textBox(Text, oriY, oriX):
    font = pygame.font.Font(None, 32)
    text = Text
    input_box = pygame.Rect(oriX, oriY, 250, 32)
    #pygame.draw.rect(screen, WHITE, input_box)
    pygame.draw.rect(screen, WHITE, input_box, 2)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

# Main game loop
def main():
   global player, current_level, in_transition, blocks, audio
   clock = pygame.time.Clock()
  
   # Create blocks from the current level array
   blocks = create_blocks_from_level(levels[current_level], BLOCK_SIZE)


   start_x, start_y = find_start_position(levels[current_level], BLOCK_SIZE)
   player = Player(start_x, start_y - BLOCK_SIZE, PLAYER_SIZE)

   running = True
   while running:
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_SPACE:
                   player.jumping = True
               elif event.key == pygame.K_s:
                    audio = not audio
           elif event.type == pygame.KEYUP:
               if event.key == pygame.K_SPACE:
                   player.jumping = False

    
       if not in_transition and player.move(blocks):
           transition_screen()

       screen.fill(WHITE)
       screen.blit(WholeWall,(0,0))

       
       for block in blocks:
           block.draw(screen)
       player.draw(screen)

       end = timer()
       time  = end-start
       textBox('Levels Cleared: ' + str(score), 50,50)
       textBox('Number of Deaths: ' + str(deaths), 90,50)
       textBox('Time Passed: {:.2f}'.format(time), 130,50)
       textBox('Press S to stop Audio', 590,930)

       pygame.display.flip()
       clock.tick(60)

   pygame.quit()
   sys.exit()

if __name__ == "__main__":
   main()