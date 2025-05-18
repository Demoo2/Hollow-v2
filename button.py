class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.original_image = image
		self.image = None
		self.is_visible = False

		self.x_pos = pos[0]
		self.y_pos = pos[1]

		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input

		self.text = self.font.render(self.text_input, True, self.base_color)
		self.rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.is_visible and self.original_image is not None:
			self.image = self.original_image
			self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
			screen.blit(self.image, self.rect)
		else:
			self.image = None
			self.is_visible = False
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if self.rect.collidepoint(position):
			return True
		return False

	def changeColor(self, position):
		if self.rect.collidepoint(position):
			self.is_visible = True
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.is_visible = False
			self.text = self.font.render(self.text_input, True, self.base_color)