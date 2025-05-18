import pygame, sys
from button import Button
from main import main, WIDTH, HEIGHT

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hollow v2")

def get_font(size):
  return pygame.font.Font("assets/font.ttf", size)

def play():
  while True:
    main(window)
    
def options():
  while True:
    options_mouse_pos = pygame.mouse.get_pos()

    window.fill("white")

    options_text = get_font(45).render("This is the OPTIONS window.", True, "Black")
    options_rect = options_text.get_rect(center=(750, 260))
    window.blit(options_text, options_rect)

    options_back = Button(image=None, pos=(750, 460), 
                          text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

    options_back.changeColor(options_mouse_pos)
    options_back.update(window)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.MOUSEBUTTONDOWN:
        if options_back.checkForInput(options_mouse_pos):
          main_menu()

    pygame.display.update()

def main_menu():
  bg_menu = pygame.image.load("assets/MenuBackground.png")
  bg_menu = pygame.transform.scale(bg_menu, (WIDTH, HEIGHT))

  while True:
    window.blit(bg_menu, (0, 0))

    menu_mouse_pos = pygame.mouse.get_pos()

    menu_text = get_font(100).render("Hollow v2", True, "#b68f40")
    menu_rect = menu_text.get_rect(center=(750, 100))

    play_button = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(750, 250), 
                         text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
    options_button = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(750, 400), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
    quit_button= Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(750, 550), 
                         text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

    window.blit(menu_text, menu_rect)

    for button in [play_button, options_button, quit_button]:
      button.changeColor(menu_mouse_pos)
      button.update(window)
        
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.MOUSEBUTTONDOWN:
        if play_button.checkForInput(menu_mouse_pos):
          play()
        if options_button.checkForInput(menu_mouse_pos):
          options()
        if quit_button.checkForInput(menu_mouse_pos):
          pygame.quit()
          sys.exit()

    pygame.display.update()

if __name__ == "__main__":
  main_menu()