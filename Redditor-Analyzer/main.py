import praw
import traceback
import pygame
from datetime import datetime
import platform

import pgx

import scenes
from reference import references

width = 800
height = 600

def main():
    pygame.init()
    
    pgx.init([width, height])
    screen = pygame.display.set_mode([width,height], pygame.RESIZABLE)
    pgx.scale.set_mode("full")
    pgx.Text.default_font = pgx.font.sourcesanspro

    bg = pgx.image.scale(pgx.image.load("data/magnifying_glass.tiff"), 20)
    bg.convert_alpha()
    bg = pgx.ui.ImageBox(pgx.Location(["center", 100], "center"), bg)

    pygame.display.set_caption("Redditor Analyzer")
    pygame.display.set_icon(pygame.image.load("data/magnifying_glass.png"))

    reddit = praw.Reddit(client_id = "Cq7lreaXnBTFTA",
                         client_secret = None,
                         user_agent = "reddit account analysis tool by u/starbuck5c")
    references.reddit = reddit

    references.active_scenes = [scenes.EnterUsername()]

    while True:
        screen.fill((10, 130, 190))
        bg.display()
        pgx.tick(144)

        for scene in references.active_scenes:
            scene.run()
        
        pygame.display.flip()
        for event in pgx.events.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, screen.get_flags())
                pgx.scale.apply()


if __name__ == "__main__":
    try:
        main()
    except Exception as E:
        pgx.handle_error(E, popup=False)
