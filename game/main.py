import pygame
import math
import asyncio

pygame.init()

# Set fullscreen mode for Pygbag/browser
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = WIN.get_size()
pygame.display.set_caption("Planet Simulation")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (169, 169, 169)
ORANGE = (255, 165, 0)

FONT = pygame.font.SysFont("comicsans", 16)

class Planet:
    AU = 149.6e6 * 1000  # Astronomical Unit in meters
    G = 6.67428e-11  # Gravitational constant
    SCALE = 250 / AU  # Adjusted scale
    TIMESTEP = 3600 * 24  # 1 day in seconds

    def __init__(self, x, y, radius, color, mass, name=""):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.name = name

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        # Draw orbit
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                px, py = point
                px = px * self.SCALE + WIDTH / 2
                py = py * self.SCALE + HEIGHT / 2
                updated_points.append((px, py))
            pygame.draw.lines(win, self.color, False, updated_points, 2)

        pygame.draw.circle(win, self.color, (int(x), int(y)), self.radius)

        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun / 1e9, 1)}M km", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width() / 2, y - distance_text.get_height() / 2 - 15))

        name_text = FONT.render(self.name, 1, WHITE)
        win.blit(name_text, (x - name_text.get_width() / 2, y + self.radius + 5))

    def attraction(self, other):
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

async def main():
    clock = pygame.time.Clock()

    # Create planets
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30, "Sun")
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24, "Earth")
    earth.y_vel = 29.783 * 1000

    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.4171 * 10**23, "Mars")
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 3.3011 * 10**23, "Mercury")
    mercury.y_vel = -47.362 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 14, ORANGE, 4.8675 * 10**24, "Venus")
    venus.y_vel = -35.02 * 1000

    planets = [sun, earth, mars, mercury, venus]

    run = True
    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        pygame.display.update()
        await asyncio.sleep(0)  # Critical for pygbag

    pygame.quit()

asyncio.run(main())
