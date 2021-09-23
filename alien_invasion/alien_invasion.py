import sys
from time import sleep
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard

class AlienInvasion:
	def __init__(self):
		pygame.init()
		self.settings = Settings()
		self.bullets = pygame.sprite.Group()
		self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
		self.aliens = pygame.sprite.Group()
		self._create_fleet()
		pygame.display.set_caption("Alien Invasion")
		self.stats = GameStats(self)
		self.ship = Ship(self)
		self.sb = ScoreBoard(self)
		self.play_button = Button(self,'play')

	def _fire_bullet(self):
		if len(self.bullets) < self.settings.bullets_allowed:
			new_bullet = Bullet(self)
			self.bullets.add(new_bullet)

	def _create_fleet(self):
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		ship = Ship(self)
		ship_height = ship.rect.height
		available_space_x = self.settings.screen_width - (alien_width * 2)
		number_aliens_x = available_space_x // (alien_width * 2)
		available_space_y = self.settings.screen_height - (alien_height * 30) - ship_height
		number_rows = available_space_y // (alien_height * 2)
		for alien_row in range(number_rows):
			for alien_number in range(number_aliens_x):
				self._create_alien(alien_number, alien_row)

	def _create_alien(self, alien_number, alien_row):
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		alien.x = alien_width + 2 * alien_width * alien_number
		alien.y = alien_height + 2 * alien_height * alien_row
		alien.rect.x = alien.x
		alien.rect.y = alien.y
		self.aliens.add(alien)

	def _check_fleet_edges(self):
		for alien in self.aliens.sprites():
			if alien.check_edges():
				self._change_fleet_direction()
				break

	def _change_fleet_direction(self):
		for alien in self.aliens.sprites():
			alien.rect.y += self.settings.fleet_drop_speed
		self.settings.fleet_direction *= -1

	def _ship_hit(self):
		if self.stats.ships_left > 0:
			self.stats.ships_left -= 1
			self.sb.prep_ships()			
			self.aliens.empty()
			self.bullets.empty()
			self._create_fleet()
			self.ship.center_ship()
			sleep(0.5)
		else:
			self.stats.game_active = False
			pygame.mouse.set_visible(True)


	def run_game(self):
		while True:
			self._check_events()
			if self.stats.game_active == True:
				self.ship.update()
				self.bullets.update()
				self._update_bullets()
				self.ship.blitme()
				self._update_aliens()
			self._update_screen()

	def _update_bullets(self):
		for bullet in self.bullets.copy():
			if bullet.rect.bottom <= 0:
				self.bullets.remove(bullet)
		self._check_bullet_alien_collisions()
		
	def _check_bullet_alien_collisions(self):
		collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
		if collisions:
			for collision in collisions.values():
				self.stats.score += self.settings.alien_points * len(collision)
			self.sb.prep_score()
			self.sb.check_highest_score()
		if not self.aliens:
			self.bullets.empty()
			self._create_fleet()
			self.settings.increase_speed()
			self.stats.level += 1
			self.sb.prep_level()

	def _update_aliens(self):
		self._check_fleet_edges()
		self.aliens.update()
		if pygame.sprite.spritecollideany(self.ship, self.aliens):
			self._ship_hit()
		self._check_aliens_bottom()

	def _update_screen(self):
		self.screen.fill(self.settings.bg_color)
		self.ship.blitme()
		for bullet in self.bullets.sprites():
			bullet.draw_bullet()
		self.aliens.draw(self.screen)
		if not self.stats.game_active:
			self.play_button.draw_button()
		self.sb.show_score()
		pygame.display.flip()

	def _check_aliens_bottom(self):
		screen_rect = self.screen.get_rect()
		for alien in self.aliens.sprites():
			if alien.rect.bottom >= screen_rect.bottom:
				self._ship_hit()
				break

	def _start_game(self):
		self.stats.reset_stats()
		self.settings.initialize_dynamic_settings()
		self.sb.prep_score()
		self.sb.prep_level()
		self.sb.prep_ships()
		self.stats.game_active = True
		self.aliens.empty()
		self.bullets.empty()
		self._create_fleet()
		self.ship.center_ship()
		pygame.mouse.set_visible(False)

	def _check_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				self._check_play_button(mouse_pos)				
			elif event.type == pygame.KEYDOWN:
				self._check_keydown_events(event)
			elif event.type == pygame.KEYUP:
				self._check_keyup_events(event)

	def _check_keydown_events(self, event):
		if event.key == pygame.K_d:
			self.ship.moving_right = True
		elif event.key == pygame.K_a:
			self.ship.moving_left = True
		elif event.key == pygame.K_w:
			self.ship.moving_up = True
		elif event.key == pygame.K_s:
			self.ship.moving_down = True
		elif event.key == pygame.K_q:
			sys.exit()
		elif event.key == pygame.K_f:
			self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
			self.settings.screen_width = self.screen.get_rect().width
			self.settings.screen_height = self.screen.get_rect().height
		elif event.key == pygame.K_g:
			self.screen = pygame.display.set_mode((1200,800))
		elif event.key == pygame.K_SPACE:
			self._fire_bullet()
		elif event.key == pygame.K_p and not self.stats.game_active:
			self._start_game()
			
	def _check_keyup_events(self, event):
		if event.key == pygame.K_d:
			self.ship.moving_right = False
		if event.key == pygame.K_a:
			self.ship.moving_left = False
		if event.key == pygame.K_w:
			self.ship.moving_up = False
		if event.key == pygame.K_s:
			self.ship.moving_down = False

	def _check_play_button(self, mouse_pos):
		button_clicked = self.play_button.rect.collidepoint(mouse_pos)
		if button_clicked and not self.stats.game_active:
			self._start_game()

if __name__ == '__main__':
	ai = AlienInvasion()
	ai.run_game()