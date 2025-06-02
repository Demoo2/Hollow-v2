import random, pygame, sys
from button import Button

GAME_OVER = False
pygame.mixer.init()

WIDTH, HEIGHT = 1500, 800
FPS = 60
PLAYER_VEL = 5

hit_sfx = pygame.mixer.Sound("assets/Sounds/PlayerAttack.wav")
dash_sfx = pygame.mixer.Sound("assets/Sounds/PlayerDash.wav")
death_sfx = pygame.mixer.Sound("assets/Sounds/PlayerDeath.wav")
jump_sfx = pygame.mixer.Sound("assets/Sounds/PlayerJump.wav")

def get_font_cinzel(size):
  return pygame.font.Font("assets/Cinzel.ttf", size)


class Player(pygame.sprite.Sprite):
  GRAVITY = 1.2

  def __init__(self, x, y, width, height):
    super().__init__()
    self.rect = pygame.Rect(x, y, width, height)
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.image.fill("green")
    self.mask = pygame.mask.from_surface(self.image)

    self.width = width
    self.height = height

    self.hp = 5
    self.invincible_cooldown = 2000
    self.last_hit_time = 0

    self.x_vel = 0
    self.y_vel = 0
    self.direction = "left"
    self.fall_count = 0
    self.jump_count = 0

    self.hit_time = 0
    self.is_hitting = False

    self.dash_time = 0
    self.is_dashing =  False
    self.dash_cooldown = 1000
    self.last_dash_time = 0

    self.is_jumping = False
    self.jump_start_time = 0
    self.max_jump_duration = 200

  def get_hit(self):
    if current_time - self.last_hit_time >= self.invincible_cooldown:
      death_sfx.play()
      self.hp -= 1
      self.last_hit_time = current_time
    else:
      death_sfx.stop()

  def start_jump(self):
    if self.jump_count < 2 and ((self.fall_count < 10 and self.jump_count == 0) or self.jump_count == 1):
      self.is_jumping = True
      jump_sfx.play()
      self.jump_start_time = pygame.time.get_ticks()
      self.jump_count += 1
      if self.jump_count == 1:
        self.fall_count = 0

  def continue_jump(self):
    if self.is_jumping:
      time_held = pygame.time.get_ticks() - self.jump_start_time
      if time_held < self.max_jump_duration:
        self.y_vel = -self.GRAVITY * 6
      else:
        self.is_jumping = False
        jump_sfx.stop()

  def move(self, dx, dy):
    self.rect.x += dx
    self.rect.y += dy
  
  def move_left(self, vel):
    self.x_vel = -vel
    if self.direction != "left":
      self.direction = "left"

  def move_right(self, vel):
    self.x_vel = vel
    if self.direction != "right":
      self.direction = "right"
  
  def start_dash(self):
    if self.dash_timer():
      self.dash_time = pygame.time.get_ticks()
      self.is_dashing = True
      self.last_dash_time = current_time

  def dash_timer(self):
    return current_time - self.last_dash_time >= self.dash_cooldown

  def use_dash(self, objects):
    if self.is_dashing and pygame.time.get_ticks() - self.dash_time < 120:
      dash_sfx.play()
      keys = pygame.key.get_pressed()
      dash_distance = 5
      dx = 5 if self.direction == "right" else -5
      virtual_rect = pygame.Rect(self.rect.x - dx, self.rect.y, self.width, self.height)
      for _ in range(dash_distance):
        virtual_rect.x += dx * 2
        collided = False
        for obj in objects:
          if virtual_rect.colliderect(obj):
            self.is_dashing = False
            collided = True
            dash_sfx.stop()
            break
        if not collided:
          self.rect.x += dx
          virtual_rect.x -= dx
        else:
          dash_sfx.stop()
          break

      self.fall_count = 0
      self.y_vel = 0
    else:
      self.is_dashing = False

  def start_hit(self):
    self.hit_time = pygame.time.get_ticks()
    self.is_hitting = True

  def hit(self, win, test_enemy, movement):
    keys = pygame.key.get_pressed()
    if self.is_hitting and pygame.time.get_ticks() - self.hit_time < 100:
      hit_image = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
      hit_image.fill((255, 0, 0, 100))

      if keys[movement[0]]:
        hit_rect = pygame.Rect(self.rect.x - 10, self.rect.y - self.rect.height - 20, self.rect.width + 20, self.rect.height + 20)
      elif self.direction == "right":
        hit_rect = pygame.Rect(self.rect.x + self.rect.width, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20) 
      else:
        hit_rect = pygame.Rect(self.rect.x - self.rect.width - 20, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20)
      
      hit_sfx.play()
      win.blit(hit_image, hit_rect)

      if hit_rect.colliderect(test_enemy.rect):
        test_enemy.get_hit()
    else:
      hit_sfx.stop()
      self.is_hitting = False

  def loop(self, fps):
    self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
    self.move(self.x_vel, self.y_vel)

    self.fall_count += 1

  def landed(self):
    self.fall_count = 0
    self.y_vel = 0
    self.jump_count = 0
    self.is_jumping = False

  def hit_head(self):
    self.fall_count = 0
    self.y_vel *= -1
    self.is_jumping = False

  def health_bar(self, win):
    hearth = pygame.Surface((40, 40))
    hearth.fill("red")
    for i in range(self.hp):
      hearth_rect = hearth.get_rect(center = ((i + 1) * 60, 50))
      win.blit(hearth, hearth_rect)

  def draw(self, win, test_enemy, objects, movement):
    win.blit(self.image, (self.rect.x, self.rect.y))

    self.health_bar(win)  
    self.hit(win, test_enemy, movement)
    self.use_dash(objects)


class Enemy(pygame.sprite.Sprite):
  def __init__(self, x, y, width, height, hp):
    super().__init__()
    self.rect = pygame.Rect(x, y, width, height)
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.image.fill("red")
    self.mask = pygame.mask.from_surface(self.image)

    self.width = width
    self.height = height

    self.teleport_cooldown = random.randint(3000, 5000)
    self.last_teleport = 0

    self.last_attack = 0

    self.boss_phase = 0
    self.full_hp = hp
    self.hp = hp

  def get_hit(self):
    self.hp -= 1
    if self.hp <= 0:
      self.image.fill("blue")

  def teleport_timer(self):
    return current_time - self.last_teleport >= self.teleport_cooldown

  def teleport(self, objects):
    if self.teleport_timer():
      object_number = random.randint(0, len(objects) - 1)
      obj = objects[object_number]
      if obj.can_teleport:
        x = obj.rect.x + obj.width / 2 - self.rect.width / 2
        y = obj.rect.y - self.rect.height - 20
        self.rect.x = x
        self.rect.y = y
        self.last_teleport = current_time
    
  def next_attack_cooldown(self, attack):
    return current_time - self.last_attack >= attack.after_attack_cooldown[self.boss_phase]

  def attack(self, attack):
    if self.next_attack_cooldown(attack):
      if self.hp <= self.full_hp // 2:
        self.boss_phase = 1
      attack.can_attack()
      self.last_attack = current_time

  def health_bar(self, win):
    percentage = self.hp / self.full_hp * 100
    healthbar = pygame.Surface((6 * percentage, 50))
    healthbar.fill("red")
    win.blit(healthbar, (450, HEIGHT - 70))

  def draw(self, win):
    self.health_bar(win)
    win.blit(self.image, (self.rect.x, self.rect.y))


class HandAttack(pygame.sprite.Sprite):
  def __init__(self, offset, width, height):
    super().__init__()
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.image.fill("yellow")
    self.rect = pygame.Rect(0, -1000, width, height)
    self.mask = pygame.mask.from_surface(self.image)

    self.offset = offset
    self.phase = "done"
    self.attack_start_time = 0

    self.can_hit = True

    self.attacks_rect = []
    self.follow_duration = random.randint(700, 1200)
    self.freeze_duration = 300
    self.descend_distance = 250
    self.descend_duration = 100
    self.after_attack_cooldown = [random.randint(5000, 7000), random.randint(4000, 6000)]

  def can_attack(self):
    self.attack_start_time = current_time
    self.phase = "follow"

  def attack(self, player):
    elapsed = current_time - self.attack_start_time

    if self.phase == "follow":
      self.attacks_rect = []
      if elapsed <= self.follow_duration:
        self.rect.x = player.rect.centerx - self.rect.width // 2
        self.rect.y = player.rect.y - self.offset
        self.attacks_rect.append(self.rect)
      else:
        self.phase = "freeze"
        self.freeze_start_time = current_time

    elif self.phase == "freeze":
      if current_time - self.freeze_start_time > self.freeze_duration:
        self.phase = "descend"
        self.descend_start_y = self.rect.y
        self.descend_start_time = current_time

    elif self.phase == "descend":
      descend_elapsed = current_time - self.descend_start_time
      descend_duration = self.descend_duration
      if descend_elapsed <= descend_duration:
        progress = descend_elapsed / descend_duration
        self.rect.y = self.descend_start_y + progress * self.descend_distance
      else:
        self.rect.y = self.descend_start_y + self.descend_distance
        self.phase = "done"

    elif self.phase == "done":
      self.rect.y = -1000

  def draw(self, win, player):
    win.blit(self.image, (self.rect.x ,self.rect.y))

    self.attack(player)


class GroundSpikeWhole(pygame.sprite.Sprite):
  def __init__(self, margin, countSpikes, width, height):
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.image.fill("yellow")

    self.countSpikes = countSpikes
    self.margin = margin
    self.width = width
    self.height = height

    self.show_duration = 800

    self.phase = "done"
    self.attack_start_time = 0

    self.after_attack_cooldown = [random.randint(6000, 8000), random.randint(5000, 7000)]
    self.choosed_side = ""

    self.attacks_rect = []
    self.grow_index = 0
    self.grow_start_time = 0
    self.grow_interval = 300
    self.grow_duration = 100 + self.grow_interval
    self.descend_interval = 80
    self.descend_duration = 80 + self.descend_interval
    self.grow_start_y = 0

  def can_attack(self):
    self.attack_start_time = current_time
    self.phase = "show" 
  
  def attack(self, player):
    elapsed = current_time - self.attack_start_time
    player_x = player.rect.x

    if self.phase == "show":
      if elapsed <= self.show_duration:
        self.attacks_rect = []

        if player_x <= WIDTH // 2 and self.choosed_side == "":
          self.choosed_side = "left"
        elif player_x >= WIDTH // 2 and self.choosed_side == "":
          self.choosed_side = "right"

        for i in range(self.countSpikes):
          if self.choosed_side == "left":
            x = i * (self.width + self.margin)
          elif self.choosed_side == "right":
            x = WIDTH - (i+1) * (self.width + self.margin)
          y = HEIGHT - 60
          spike_rect = pygame.Rect(x, y, self.width, self.height)
          self.attacks_rect.append(spike_rect)
      else:
        self.phase = "grow"
        self.grow_index = 0
        self.grow_start_y = self.attacks_rect[0].y + 60
        self.grow_start_time = current_time
    
    elif self.phase == "grow":
      if self.grow_index < len(self.attacks_rect):
        grow_elapsed = current_time - self.grow_start_time
        grow_duration = self.grow_duration
        if grow_elapsed >= self.grow_interval:
          spike = self.attacks_rect[self.grow_index]
          if grow_elapsed <= grow_duration:
            progress = (grow_elapsed / grow_duration) ** 2
            spike.y = self.grow_start_y - progress * self.height / 1.5
          else:
            self.attacks_rect[self.grow_index] = spike
            self.grow_index += 1
            self.grow_start_time = current_time
      else:
        self.phase = "done"
        self.grow_index = 0
        self.grow_start_y = self.attacks_rect[0].y
        self.grow_start_time = current_time
    
    elif self.phase == "done":
      self.choosed_side = ""
      if self.grow_index < len(self.attacks_rect):
        descend_elapsed = current_time - self.grow_start_time
        descend_duration = self.descend_duration
        if descend_elapsed >= self.descend_interval:
          spike = self.attacks_rect[self.grow_index]
          if descend_elapsed <= descend_duration:
            progress = (descend_elapsed / descend_duration) ** 2
            spike.y = self.grow_start_y + progress * self.height / 1.4
          else:
            self.attacks_rect[self.grow_index] = spike
            self.grow_index += 1
            self.grow_start_time = current_time

  def draw(self, win, player):
    for spike_rect in self.attacks_rect:
      win.blit(self.image, (spike_rect.x, spike_rect.y))
    self.attack(player)


class GroundSpikeMargin(pygame.sprite.Sprite):
  def __init__(self, spikeCount, height, repeat):
    self.image = pygame.Surface((WIDTH // spikeCount, height), pygame.SRCALPHA)
    self.image.fill("yellow")

    self.spikeCount = spikeCount
    self.width = WIDTH // spikeCount
    self.height = height

    self.phase = "idle"
    self.attack_start_time = 0
    self.after_attack_cooldown = [random.randint(9000, 11000), random.randint(8000, 10000)]

    self.attacks_rect = [pygame.Rect(i * self.width, HEIGHT, self.width, self.height) for i in range(self.spikeCount)]
    self.original_repeat = repeat
    self.repeat = repeat
    self.spikes = 0
    self.grow_start_time = 0
    self.grow_start_y = 0

    self.grow_duration = 140
    self.descend_duration = 70
    self.freeze_duration = 100
    self.show_duration = 400

  def can_attack(self):
    self.attack_start_time = current_time
    self.phase = "show" 
  
  def attack(self, player):
    elapsed = current_time - self.attack_start_time

    if self.phase == "show":
      if elapsed <= self.show_duration:
        for rect in self.attacks_rect[self.spikes::2]:
          rect.y = HEIGHT - 70
      else:
        self.phase = "grow"
        self.grow_start_y = self.attacks_rect[0].y + 70
        self.grow_start_time = current_time
    
    elif self.phase == "grow":
      grow_elapsed = current_time - self.grow_start_time
      grow_duration = self.grow_duration
      if grow_elapsed <= grow_duration:
        for rect in self.attacks_rect[self.spikes::2]:
          progress = (grow_elapsed / grow_duration) ** 2
          rect.y = self.grow_start_y - progress * self.height / 1.4
      else:
        self.phase = "freeze"
        self.grow_start_time = current_time
    
    elif self.phase == "freeze":
      if current_time - self.grow_start_time > self.freeze_duration:
        self.phase = "done"
        self.grow_start_y = self.attacks_rect[0].y
        self.grow_start_time = current_time
    
    elif self.phase == "done":
      descend_elapsed = current_time - self.grow_start_time
      descend_duration = self.descend_duration
      if descend_elapsed <= descend_duration:
        for rect in self.attacks_rect[self.spikes::2]:
          progress = (descend_elapsed / descend_duration) ** 2
          rect.y = self.grow_start_y + progress * self.height / 1.2
      else:
        if self.repeat > 1:
          self.spikes = 1 - self.spikes
          self.repeat -= 1
          self.phase = "show"
          self.attack_start_time = current_time
        else:
          self.phase = "idle"
          self.repeat = self.original_repeat
    
  def draw(self, win, player):
    for spike_rect in self.attacks_rect:
      win.blit(self.image, (spike_rect.x, spike_rect.y))
    self.attack(player)


class Object(pygame.sprite.Sprite):
  def __init__(self, x, y, width, height, name=None):
    super().__init__()
    self.rect = pygame.Rect(x, y, width, height)
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.width = width
    self.height = height
    self.name = name

  def draw(self, win):
    win.blit(self.image, (self.rect.x, self.rect.y))


class Platform(Object):
  def __init__(self, x, y, width, height, can_teleport=False):
    super().__init__(x, y, width, height)
    self.plat = pygame.Surface((width, height))
    self.plat.fill("gray")
    self.image.blit(self.plat, (0, 0))
    self.mask = pygame.mask.from_surface(self.image)
    self.can_teleport = can_teleport


def draw(window, bg_image, player, objects, test_enemy, attacks, movement):
  window.blit(bg_image, (0, 0))

  for attack in attacks:
      attack.draw(window, player)

  test_enemy.draw(window)
  player.draw(window, test_enemy, objects, movement)

  for obj in objects:
    obj.draw(window)

  pygame.display.update()


def handle_vertical_collision(player, objects, dy):
  collided_objects = []
  for obj in objects:
    if pygame.sprite.collide_mask(player, obj):
      if dy > 0:
        player.rect.bottom = obj.rect.top
        player.landed()
      elif dy < 0:
        player.rect.top = obj.rect.bottom
        player.hit_head()
    
    collided_objects.append(obj)
  return collided_objects


def collide(player, objects, dx):
  player.move(dx, 0)
  player.update()
  collided_object = None
  
  for obj in objects:
    if pygame.sprite.collide_mask(player, obj):
      collided_object = obj
      break
  
  player.move(-dx, 0)
  player.update()
  return collided_object


def handle_move(player, objects, movement):
  keys = pygame.key.get_pressed()

  player.x_vel = 0
  collide_left = collide(player, objects, -PLAYER_VEL)
  collide_right = collide(player, objects, PLAYER_VEL)

  if keys[movement[1]] and not collide_left and not player.is_dashing:
    player.move_left(PLAYER_VEL)
  if keys[movement[2]] and not collide_right and not player.is_dashing:
    player.move_right(PLAYER_VEL)
  if keys[movement[3]]:
    player.continue_jump()
  else:
    player.is_jumping = False

  if player.rect.y > HEIGHT:
    choosen_object = objects[random.randint(0, len(objects) - 1)]
    player.rect.y = choosen_object.rect.y
    player.rect.x = choosen_object.rect.x + (choosen_object.rect.width / 2) - (player.rect.width / 2)
    player.get_hit()
  if player.rect.x < 0:
    player.rect.x = 0
  if player.rect.x > WIDTH - player.width:
    player.rect.x = WIDTH - player.width
  
  handle_vertical_collision(player, objects, player.y_vel)


def handle_enemy(player, enemy, attacks, objects):
  enemy.teleport(objects)

  for attack in attacks:
    attack.attack(player)
    for rect in attack.attacks_rect:
      if rect.colliderect(player):
        player.get_hit()
  current_attack = random.choice(attacks)
  enemy.attack(current_attack)


def main(window, paused_time_offset, movement):
  clock = pygame.time.Clock()

  game_music_onoff = "on"

  bg_image = pygame.image.load("assets/brackground.webp").convert()
  bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

  pause_menu = False
  pause_start_time = 0

  objects = [
    # Left side
    Platform(170, 650, 160, 50, can_teleport=True),
    Platform(370, 500, 100, 50, can_teleport=True),
    Platform(140, 330, 130, 50, can_teleport=True),

    # Middle
    Platform(680, 620, 140, 50, can_teleport=True),
    Platform(570, 400, 120, 50, can_teleport=True),
    Platform(870, 330, 130, 50, can_teleport=True),

    # Right side
    Platform(930, 550, 130, 50, can_teleport=True),
    Platform(1170, 430, 110, 50, can_teleport=True),
    Platform(1280, 660, 150, 50, can_teleport=True)
  ]

  player = Player(100, 100, 50, 50)
  test_enemy = Enemy(650, 100, 200, 300, 200)
  attacks = [
    # HandAttack(150, 200, 70),
    GroundSpikeWhole(40, 6, 150, 1000),
    # GroundSpikeMargin(10, 1000, 3)
  ]

  def game_over_screen(victory):
    GAME_OVER = True
    score = current_time // 1000
    while GAME_OVER:
      game_over_screen = pygame.time.get_ticks()
      window.fill((0, 0, 0))
      game_over_text = get_font_cinzel(60).render("Game Over", True, (255, 0, 0))
      game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, 200))

      if victory:
        score_text = get_font_cinzel(40).render(f"Time spend: {score}", True, (255, 0, 0))
        score_rect = score_text.get_rect(center=(WIDTH // 2, 350))
        window.blit(score_text, score_rect)
        print(game_over_screen)

        with open("bestscore.txt", "a", encoding="utf-8") as f:
          # Sprav tu nech to zapisuje najlepsie skore
          # Najlepsie skore je to ktore je mensie
          # Skore je podla toho ako dlho zabijas bossa cim skor tym lepsie
          pass

      play_again_button = Button(image=None, pos=(WIDTH // 2, 410), text_input="Play Again", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")
      main_menu_button = Button(image=None, pos=(WIDTH // 2, 470), text_input="Main Menu", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")

      for i in [[game_over_text, game_over_rect]]:
        window.blit(i[0], i[1])

      mouse_pos = pygame.mouse.get_pos()
      for button in [play_again_button, main_menu_button]:
        button.changeColor(mouse_pos)
        button.update(window)

      pygame.display.update()

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
          if play_again_button.checkForInput(mouse_pos):
            main(window, game_over_screen, movement)
          if main_menu_button.checkForInput(mouse_pos):
            main_menu(window, movement)

  run = True
  while run:
    clock.tick(FPS)
    global current_time 
    current_time = pygame.time.get_ticks() - paused_time_offset

    if game_music_onoff == "on":
      pass
    else:
      pass

    events = pygame.event.get()
    for event in events:
      if event.type == pygame.QUIT:
        run = False
        break

    if pause_menu:
      menu_mouse_pos = pygame.mouse.get_pos()

      overlay = pygame.Surface((WIDTH / 3, HEIGHT / 1.5), pygame.SRCALPHA)
      overlay.fill((0, 0, 0))
      overlay_rect = overlay.get_rect(center=(WIDTH // 2, HEIGHT // 2))
      window.blit(overlay, overlay_rect)

      text = get_font_cinzel(40).render("Paused", True, (255, 255, 255))
      text_rect = text.get_rect(center=(WIDTH // 2, 280))
      window.blit(text, text_rect)

      continue_game_button = Button(image=None, pos=(WIDTH // 2, 380), text_input="Continue", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")
      quit_game_button = Button(image=None, pos=(WIDTH // 2, 440), text_input="Quit Game", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")
      music_onoff_button = Button(image=None, pos=(WIDTH // 2, 500), text_input="Music {game_music_onoff}", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")

      for button in [continue_game_button, quit_game_button, music_onoff_button]:
        button.changeColor(menu_mouse_pos)
        button.update(window)

      pygame.display.update()
      for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
          if continue_game_button.checkForInput(menu_mouse_pos):
            pause_menu = False
            paused_time_offset += pygame.time.get_ticks() - pause_start_time
          if quit_game_button.checkForInput(menu_mouse_pos):
            run = False
            break
          if music_onoff_button.checkForInput(menu_mouse_pos):
            game_music_onoff = "off"
        
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            pause_menu = False
            paused_time_offset += pygame.time.get_ticks() - pause_start_time
      continue

    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          pause_menu = True
          pause_start_time = pygame.time.get_ticks()

        if event.key == movement[3]:
          player.start_jump()
        if event.key == movement[5]:
          player.start_hit()
        if event.key == movement[4]:
          player.start_dash()
    
    player.loop(FPS)
    handle_move(player, objects, movement)
    handle_enemy(player, test_enemy, attacks, objects)

    if player.hp <= 0:
      game_over_screen(False)
    elif test_enemy.hp <= 0:
      game_over_screen(True)

    draw(window, bg_image, player, objects, test_enemy, attacks, movement)

  pygame.quit()
  sys.exit()


####################### MAIN MENU ###########################


def options(bg_menu, movement):
  while True:
    options_mouse_pos = pygame.mouse.get_pos()

    window.blit(bg_menu, (0, 0))

    options_text = get_font_cinzel(70).render("Option Menu", True, "white")
    options_rect = options_text.get_rect(center=(WIDTH // 2, 200))
    window.blit(options_text, options_rect)

    texts = [
      f'{"Arrow up" if movement[0] == pygame.K_UP else "W"}: look up',
      f'{"Arrow left" if movement[1] == pygame.K_LEFT else "A"}: left',
      f'{"Arrow right" if movement[2] == pygame.K_RIGHT else "D"}: right',
      f'{"Z" if movement[3] == pygame.K_z else "SPACE"}: jump',
      f'{"C" if movement[4] == pygame.K_c else "LEFT SHIFT"}: dash',
      f'{"X" if movement[5] == pygame.K_x else "J"}: hit'
    ]
    for i in range(len(texts)):
      key_text = get_font_cinzel(30).render(texts[i], True, "white")
      key_rect = key_text.get_rect(center=(WIDTH // 2, 300 + i * 40))
      window.blit(key_text, key_rect)

    change_keybinds = Button(image=None, pos=(WIDTH // 2, 560), text_input="Change Keybinds", font=get_font_cinzel(40), base_color="white", hovering_color="Gray")
    options_back = Button(image=None, pos=(WIDTH // 2, 620), text_input="Back", font=get_font_cinzel(40), base_color="white", hovering_color="Gray")

    for button in [change_keybinds, options_back]:
      button.changeColor(options_mouse_pos)
      button.update(window)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.MOUSEBUTTONDOWN:
        if options_back.checkForInput(options_mouse_pos):
          main_menu(window, movement)
        if change_keybinds.checkForInput(options_mouse_pos):
          hollow_key = [pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z, pygame.K_c, pygame.K_x]
          sols_key = [pygame.K_w, pygame.K_a, pygame.K_d, pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_j]
          movement = sols_key if movement == hollow_key else hollow_key
    
    pygame.display.update()

def main_menu(window, movement):
  bg_menu = pygame.image.load("assets/MenuBackgroundVoid.jpg")
  bg_menu = pygame.transform.scale(bg_menu, (WIDTH, HEIGHT))

  while True:
    start_time = pygame.time.get_ticks()
    window.blit(bg_menu, (0, 0))

    menu_mouse_pos = pygame.mouse.get_pos()

    menu_text = get_font_cinzel(100).render("Hollow v2", True, "white")
    menu_rect = menu_text.get_rect(center=(WIDTH // 2, 200))

    play_button = Button(image=None, pos=(WIDTH // 2, 400), text_input="Play Game", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")
    options_button = Button(image=None, pos=(WIDTH // 2, 460), text_input="Options", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")
    quit_button= Button(image=None, pos=(WIDTH // 2, 520), text_input="Quit Game", font=get_font_cinzel(40), base_color="White", hovering_color="Gray")

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
          main(window, start_time, movement)
        if options_button.checkForInput(menu_mouse_pos):
          options(bg_menu, movement)
        if quit_button.checkForInput(menu_mouse_pos):
          pygame.quit()
          sys.exit()

    pygame.display.update()


if __name__ == "__main__":
  movement=[pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z, pygame.K_c, pygame.K_x]
  pygame.init()
  window = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Hollow v2")
  main_menu(window, movement)