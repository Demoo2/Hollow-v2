import random, pygame, sys
from button import Button

WIDTH, HEIGHT = 1500, 800
FPS = 60
PLAYER_VEL = 5


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

  def start_jump(self):
    if self.jump_count < 2 and ((self.fall_count < 10 and self.jump_count == 0) or self.jump_count == 1):
      self.is_jumping = True
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
  
  def start_dash(self, current_time):
    if self.dash_timer(current_time):
      self.dash_time = pygame.time.get_ticks()
      self.is_dashing = True
      self.last_dash_time = current_time

  def dash_timer(self, current_time):
    return current_time - self.last_dash_time >= self.dash_cooldown

  def use_dash(self, objects):
    if self.is_dashing and pygame.time.get_ticks() - self.dash_time < 120:
      dash_distance = 22
      dx = 1 if self.direction == "right" else -1
      for _ in range(dash_distance):
        self.rect.x += dx
        for obj in objects:
          if pygame.sprite.collide_mask(self, obj):
            self.rect.x -= dx
            self.is_dashing = False
            break
        self.fall_count = 0
        self.y_vel = 0
    else:
      self.is_dashing = False

  def start_hit(self):
    self.hit_time = pygame.time.get_ticks()
    self.is_hitting = True

  def hit(self, win, test_enemy):
    keys = pygame.key.get_pressed()
    if self.is_hitting and pygame.time.get_ticks() - self.hit_time < 100:
      hit_image = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
      hit_image.fill((255, 0, 0, 100))

      if keys[pygame.K_w]:
        hit_rect = pygame.Rect(self.rect.x - 10, self.rect.y - self.rect.height - 20, self.rect.width + 20, self.rect.height + 20)
      elif self.direction == "right":
        hit_rect = pygame.Rect(self.rect.x + self.rect.width, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20) 
      else:
        hit_rect = pygame.Rect(self.rect.x - self.rect.width - 20, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20)
      
      win.blit(hit_image, hit_rect)

      if hit_rect.colliderect(test_enemy.rect):
        test_enemy.get_hit()
    else:
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

  def draw(self, win, test_enemy, objects):
    win.blit(self.image, (self.rect.x, self.rect.y))
      
    self.hit(win, test_enemy)
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

  def teleport_timer(self, current_time):
    return current_time - self.last_teleport >= self.teleport_cooldown

  def teleport(self, objects, current_time):
    if self.teleport_timer(current_time):
      object_number = random.randint(0, len(objects) - 1)
      obj = objects[object_number]
      if obj.can_teleport:
        x = obj.rect.x + obj.width / 2 - self.rect.width / 2
        y = obj.rect.y - self.rect.height - 20
        self.rect.x = x
        self.rect.y = y
        self.last_teleport = current_time
    
  def next_attack_cooldown(self, current_time, attack):
    return current_time - self.last_attack >= attack.after_attack_cooldown[self.boss_phase]

  def attack(self, attack, current_time):
    if self.next_attack_cooldown(current_time, attack):
      if self.hp <= self.full_hp // 2:
        self.boss_phase = 1
      attack.can_attack(current_time)
      self.last_attack = current_time

  def draw(self, win):
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

    self.follow_duration = random.randint(700, 1200)
    self.freeze_duration = 300
    self.descend_distance = 250
    self.descend_duration = 100
    self.after_attack_cooldown = [random.randint(5000, 7000), random.randint(4000, 6000)]

  def can_attack(self, current_time):
      self.attack_start_time = current_time
      self.phase = "follow"

  def attack(self, player, current_time):
      elapsed = current_time - self.attack_start_time

      if self.phase == "follow":
          if elapsed <= self.follow_duration:
              self.rect.x = player.rect.centerx - self.rect.width // 2
              self.rect.y = player.rect.y - self.offset
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

  def draw(self, win, player, current_time):
    win.blit(self.image, (self.rect.x ,self.rect.y))

    self.attack(player, current_time)


class GroundSpikeWhole(pygame.sprite.Sprite):
  def __init__(self, margin, countSpikes, width, height):
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.image.fill("yellow")
    self.rect = pygame.Rect(margin, 60, width, height)

    self.countSpikes = countSpikes
    self.margin = margin
    self.width = width
    self.height = height

    self.show_duration = 1000

    self.phase = "done"
    self.attack_start_time = 0

    self.after_attack_cooldown = [random.randint(6000, 8000), random.randint(5000, 7000)]

    self.spikes = []
    self.grow_index = 0
    self.grow_start_time = 0
    self.grow_interval = 300
    self.grow_duration = 100 + self.grow_interval
    self.descend_interval = 80
    self.descend_duration = 80 + self.descend_interval
    self.grow_start_y = 0

  def can_attack(self, current_time):
    self.attack_start_time = current_time
    self.phase = "show" 
  
  def attack(self, player, current_time):
    elapsed = current_time - self.attack_start_time

    if self.phase == "show":
      if elapsed <= self.show_duration:
        self.spikes = []
        for i in range(self.countSpikes):
          x = i * (self.width + self.margin)
          y = self.height - (self.height - HEIGHT) - 60
          spike_rect = pygame.Rect(x, y, self.width, self.height)
          self.spikes.append(spike_rect)
      else:
        self.phase = "grow"
        self.grow_index = 0
        self.grow_start_y = self.spikes[0].y + 60
        self.grow_start_time = current_time
    
    elif self.phase == "grow":
      if self.grow_index < len(self.spikes):
        grow_elapsed = current_time - self.grow_start_time
        grow_duration = self.grow_duration
        if grow_elapsed >= self.grow_interval:
          spike = self.spikes[self.grow_index]
          if grow_elapsed <= grow_duration:
            progress = (grow_elapsed / grow_duration) ** 2
            spike.y = self.grow_start_y - progress * self.height / 1.5
          else:
            self.spikes[self.grow_index] = spike
            self.grow_index += 1
            self.grow_start_time = current_time
      else:
        self.phase = "done"
        self.grow_index = 0
        self.grow_start_y = self.spikes[0].y
        self.grow_start_time = current_time
    
    elif self.phase == "done":
      if self.grow_index < len(self.spikes):
        descend_elapsed = current_time - self.grow_start_time
        descend_duration = self.descend_duration
        if descend_elapsed >= self.descend_interval:
          spike = self.spikes[self.grow_index]
          if descend_elapsed <= descend_duration:
            progress = (descend_elapsed / descend_duration) ** 2
            spike.y = self.grow_start_y + progress * self.height / 1.4
          else:
            self.spikes[self.grow_index] = spike
            self.grow_index += 1
            self.grow_start_time = current_time


  def draw(self, win, player, current_time):
    for spike_rect in self.spikes:
      win.blit(self.image, (spike_rect.x, spike_rect.y))
    self.attack(player, current_time)


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


def draw(window, bg_image, player, objects, test_enemy, attacks, current_time):
  window.blit(bg_image, (0, 0))

  for attack in attacks:
      attack.draw(window, player, current_time)

  test_enemy.draw(window)
  player.draw(window, test_enemy, objects)

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


def handle_move(player, objects):
  keys = pygame.key.get_pressed()

  player.x_vel = 0
  collide_left = collide(player, objects, -PLAYER_VEL)
  collide_right = collide(player, objects, PLAYER_VEL)

  if keys[pygame.K_a] and not collide_left:
    player.move_left(PLAYER_VEL)
  if keys[pygame.K_d] and not collide_right:
    player.move_right(PLAYER_VEL)
  if keys[pygame.K_SPACE]:
    player.continue_jump()
  else:
    player.is_jumping = False

  if player.rect.y > HEIGHT - 50:
    player.rect.y = HEIGHT - 50 
    # Nechapem preco ma to clipuje pod objekty ale tak tento if statement aspon zaisti ze nevypadnem z mapy
  if player.rect.x < 0:
    player.rect.x = 0
  if player.rect.x > WIDTH - player.width:
    player.rect.x = WIDTH - player.width
  handle_vertical_collision(player, objects, player.y_vel)


def main(window, paused_time_offset):
  clock = pygame.time.Clock()

  bg_image = pygame.image.load("assets/brackground.webp").convert()
  bg_image = pygame.transform.scale(bg_image, (1500, 800))

  pause_menu = False
  pause_start_time = 0

  floor = Platform(0, HEIGHT - 50, WIDTH, 50)
  objects = [
    floor, 
    Platform(110, 450, 100, 50, can_teleport=True),
    Platform(620, 400, 100, 50, can_teleport=True),
    Platform(1310, 560, 100, 50, can_teleport=True),
    Platform(860, 600, 100, 50, can_teleport=True)
  ]

  player = Player(100, 100, 50, 50)
  test_enemy = Enemy(650, 100, 200, 300, 200)
  attacks = [
    HandAttack(150, 200, 70),
    GroundSpikeWhole(40, 6, 150, 1000)
  ]

  run = True
  while run:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks() - paused_time_offset

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

      continue_game_button = Button(image=None, pos=(WIDTH // 2, 380), text_input="Continue", font=get_font_cinzel(40), base_color="White", hovering_color="#FAFAF5")
      quit_game_button = Button(image=None, pos=(WIDTH // 2, 440), text_input="Quit Game", font=get_font_cinzel(40), base_color="White", hovering_color="#FAFAF5")

      for button in [continue_game_button, quit_game_button]:
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

        if event.key == pygame.K_SPACE:
          player.start_jump()
        if event.key == pygame.K_j:
          player.start_hit()
        if event.key == pygame.K_LSHIFT:
          player.start_dash(current_time)
    
    player.loop(FPS)
    test_enemy.teleport(objects, current_time)
    handle_move(player, objects)

    for attack in attacks:
      attack.attack(player, current_time)

    attack = random.choice(attacks)
    test_enemy.attack(attack, current_time)

    draw(window, bg_image, player, objects, test_enemy, attacks, current_time)

  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  pygame.init()
  window = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Hollow v2")
  main(window, paused_time_offset=0)