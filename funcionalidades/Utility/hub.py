import pygame

CAMERA_SPEED = 200  # píxeles por segundo
PLAYER_SPEED = 200  # píxeles por segundo

TILE_SIZE = 32
VIRTUAL_W = 20 * TILE_SIZE  # 640
VIRTUAL_H = 15 * TILE_SIZE  # 480

def getCollisions(collision_layer):
    rects = []
    for x, y, gid in collision_layer:
        if gid != 0:
            rects.append(pygame.Rect(x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))

    return rects

def draw_map(surface, tmx_data, cam_x, cam_y):
    tile_w = tmx_data.tilewidth
    tile_h = tmx_data.tileheight

    screen_w = surface.get_width()
    screen_h = surface.get_height()

    tiles_x = screen_w // tile_w + 1
    tiles_y = screen_h // tile_h + 1

    start_x = int(cam_x // tile_w)
    start_y = int(cam_y // tile_h)

    offset_x = int(cam_x % tile_w)
    offset_y = int(cam_y % tile_h)

    for layer in tmx_data.visible_layers:
        if not hasattr(layer, "data"):
            continue

        for y in range(tiles_y):
            for x in range(tiles_x):
                map_x = start_x + x
                map_y = start_y + y

                if map_x < 0 or map_y < 0:
                    continue
                if map_x >= tmx_data.width or map_y >= tmx_data.height:
                    continue

                gid = layer.data[map_y][map_x]
                if gid == 0:
                    continue

                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(
                        tile,
                        (
                            x * tile_w - offset_x,
                            y * tile_h - offset_y
                        )
                    )

def drawHub(screen, hub_surface, player_rect, player_img, tmx_data, collision_rects, doors, appState,world):
    clock = pygame.time.Clock()
    dt = clock.tick(60) / 1000
    keys = pygame.key.get_pressed()

    dx = dy = 0
    if keys[pygame.K_a]:
        dx -= PLAYER_SPEED * dt
    if keys[pygame.K_d]:
        dx += PLAYER_SPEED * dt
    if keys[pygame.K_w]:
        dy -= PLAYER_SPEED * dt
    if keys[pygame.K_s]:
        dy += PLAYER_SPEED * dt

    player_rect.x += dx
    for rect in collision_rects:
        if player_rect.colliderect(rect):
            if dx > 0:
                player_rect.right = rect.left
            elif dx < 0:
                player_rect.left = rect.right

    player_rect.y += dy
    for rect in collision_rects:
        if player_rect.colliderect(rect):
            if dy > 0:
                player_rect.bottom = rect.top
            elif dy < 0:
                player_rect.top = rect.bottom

    for rect, target in doors:
        if player_rect.colliderect(rect):
            if target == "dungeon":
                appState = "transition"
            else:
                world = target


    # cámara usando RESOLUCIÓN VIRTUAL
    cam_x = player_rect.centerx - VIRTUAL_W // 2
    cam_y = player_rect.centery - VIRTUAL_H // 2

    max_x = tmx_data.width * tmx_data.tilewidth - VIRTUAL_W
    max_y = tmx_data.height * tmx_data.tileheight - VIRTUAL_H

    cam_x = max(0, min(cam_x, max_x))
    cam_y = max(0, min(cam_y, max_y))

    # ---- DIBUJO EN HUB SURFACE ----
    hub_surface.fill((0, 0, 0))
    draw_map(hub_surface, tmx_data, cam_x, cam_y)

    hub_surface.blit(
        player_img,
        (
            player_rect.x - cam_x,
            player_rect.y - cam_y
        )
    )

    # ---- ESCALADO FINAL A PANTALLA ----
    window_w, window_h = screen.get_size()
    scaled_hub = pygame.transform.scale(hub_surface, (window_w, window_h))
    screen.blit(scaled_hub, (0, 0))

    return appState, world