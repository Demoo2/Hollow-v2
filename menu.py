import pygame, sys
from button import Button
from main import main, WIDTH, HEIGHT, get_font_cinzel

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hollow v2")

def play(start_time):
  main(window, start_time)
    
def options():
  while True:
    options_mouse_pos = pygame.mouse.get_pos()

    window.fill("white")

    options_text = get_font_cinzel(45).render("This is the OPTIONS window.", True, "Black")
    options_rect = options_text.get_rect(center=(WIDTH // 2, 260))
    window.blit(options_text, options_rect)

    options_back = Button(image=None, pos=(WIDTH // 2, 460), text_input="BACK", font=get_font_cinzel(75), base_color="Black", hovering_color="Green")

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
  bg_menu = pygame.image.load("assets/MenuBackgroundVoid.jpg")
  bg_menu = pygame.transform.scale(bg_menu, (WIDTH, HEIGHT))

  while True:
    start_time = pygame.time.get_ticks()
    window.blit(bg_menu, (0, 0))

    menu_mouse_pos = pygame.mouse.get_pos()

    menu_text = get_font_cinzel(100).render("Hollow v2", True, "white")
    menu_rect = menu_text.get_rect(center=(WIDTH // 2, 200))

    play_button = Button(image=None, pos=(WIDTH // 2, 400), text_input="Play Game", font=get_font_cinzel(40), base_color="White", hovering_color="#FAFAF5")
    options_button = Button(image=None, pos=(WIDTH // 2, 460), text_input="Options", font=get_font_cinzel(40), base_color="White", hovering_color="#FAFAF5")
    quit_button= Button(image=None, pos=(WIDTH // 2, 520), text_input="Quit Game", font=get_font_cinzel(40), base_color="White", hovering_color="#FAFAF5")

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
          play(start_time)
        if options_button.checkForInput(menu_mouse_pos):
          options()
        if quit_button.checkForInput(menu_mouse_pos):
          pygame.quit()
          sys.exit()

    pygame.display.update()

if __name__ == "__main__":
  main_menu()