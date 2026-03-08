#!/usr/bin/env python3
"""Fly a plane with WASD keys. Avoid the clouds or game over!
Arrow keys: Up/Down = resize mountain."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

# Cloud definitions: (center_x, center_y, speed, list of (dx, dy, radius) for each puff)
CLOUDS = [
    {"x": 2, "y": 4.5, "speed": 0.03, "puffs": [(-0.3, 0, 0.35), (0, 0.15, 0.4), (0.35, 0, 0.3), (0.15, -0.1, 0.25)]},
    {"x": 6, "y": 5.2, "speed": 0.025, "puffs": [(-0.25, 0.05, 0.3), (0.1, 0.2, 0.35), (0.4, 0, 0.28)]},
    {"x": 8, "y": 3.8, "speed": 0.02, "puffs": [(-0.2, 0, 0.25), (0.15, 0.1, 0.3), (0.45, 0, 0.22)]},
]

# Base mountain shape (peak at center, height 4)
BASE_POINTS = np.array([
    [0, 0],      # Left base
    [2.5, 0],    # Left foot
    [5, 4],      # Peak (center)
    [7.5, 0],    # Right foot
    [10, 0],     # Right base
])

# Size scale: 1.0 = default, range 0.3 to 3.0
mountain_scale = [1.0]  # Use list so callback can modify

# Plane state
plane_x = [1.5]
plane_y = [3.0]
plane_speed = 0.25
plane_radius = 0.22  # Collision hitbox
game_over = [False]  # Use list so callbacks can modify


def get_mountain_points():
    """Get mountain points scaled by current size."""
    points = BASE_POINTS.copy()
    base_y = 0
    points[:, 1] = base_y + (points[:, 1] - base_y) * mountain_scale[0]
    return points


def check_collision():
    """Check if plane collides with any cloud puff."""
    px, py = plane_x[0], plane_y[0]
    for cloud_data, cloud_circles in cloud_patches:
        for circ, dx, dy, r in cloud_circles:
            cx = cloud_data["x"] + dx
            cy = cloud_data["y"] + dy
            dist = np.sqrt((px - cx) ** 2 + (py - cy) ** 2)
            if dist < r + plane_radius:
                return True
    return False


def on_key(event):
    """Handle WASD for plane, arrow keys for mountain."""
    if game_over[0]:
        return

    # WASD - plane movement
    if event.key in ("w", "W"):
        plane_y[0] = min(5.5, plane_y[0] + plane_speed)
    elif event.key in ("s", "S"):
        plane_y[0] = max(0.5, plane_y[0] - plane_speed)
    elif event.key in ("a", "A"):
        plane_x[0] = max(0.3, plane_x[0] - plane_speed)
    elif event.key in ("d", "D"):
        plane_x[0] = min(9.7, plane_x[0] + plane_speed)
    # Arrow keys - mountain size
    elif event.key == "up":
        mountain_scale[0] = min(3.0, mountain_scale[0] + 0.15)
        mountain.set_xy(get_mountain_points())
    elif event.key == "down":
        mountain_scale[0] = max(0.3, mountain_scale[0] - 0.15)
        mountain.set_xy(get_mountain_points())
    else:
        return

    # Update plane position
    if event.key.lower() in ("w", "a", "s", "d"):
        update_plane_position()
        if check_collision():
            trigger_game_over()
        fig.canvas.draw_idle()


def update_plane_position():
    """Update the plane polygon position."""
    px, py = plane_x[0], plane_y[0]
    size = 0.35
    # Simple plane: triangle pointing right (nose)
    plane_points = np.array([
        [px + size, py],       # Nose
        [px - size * 0.6, py + size * 0.5],   # Top rear
        [px - size * 0.6, py - size * 0.5],  # Bottom rear
    ])
    plane_patch.set_xy(plane_points)


def trigger_game_over():
    """End the game and display game over message."""
    game_over[0] = True
    anim.pause()
    game_over_text.set_visible(True)
    game_over_text.set_text("GAME OVER - You hit a cloud!")
    fig.canvas.draw_idle()


def create_cloud(cloud_data):
    """Create circle patches for a fluffy cloud."""
    circles = []
    for dx, dy, r in cloud_data["puffs"]:
        circ = patches.Circle(
            (cloud_data["x"] + dx, cloud_data["y"] + dy),
            r,
            facecolor="white",
            edgecolor="none",
            alpha=0.95,
            zorder=10,
        )
        circles.append((circ, dx, dy, r))
    return circles


def animate_frame(_frame):
    """Move clouds and check collision each frame."""
    if game_over[0]:
        return

    # Move clouds
    for cloud_data, cloud_circles in cloud_patches:
        cloud_data["x"] += cloud_data["speed"]
        if cloud_data["x"] > 12:
            cloud_data["x"] = -2
        for circ, dx, dy, r in cloud_circles:
            circ.center = (cloud_data["x"] + dx, cloud_data["y"] + dy)

    # Check collision after cloud movement
    if check_collision():
        trigger_game_over()


# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

# Set the sky (blue background) - both figure and axis
fig.patch.set_facecolor("#87CEEB")
ax.set_facecolor("#87CEEB")
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)

# Create mountain shape
mountain = patches.Polygon(
    get_mountain_points(),
    closed=True,
    facecolor="#8B4513",
    edgecolor="#654321",
    linewidth=2,
)
ax.add_patch(mountain)

# Create and add clouds
cloud_patches = []
for cloud_data in CLOUDS:
    circles = create_cloud(cloud_data)
    for circ, *_ in circles:
        ax.add_patch(circ)
    cloud_patches.append((cloud_data, circles))

# Create plane (triangle pointing right)
plane_points = np.array([
    [plane_x[0] + 0.35, plane_y[0]],
    [plane_x[0] - 0.21, plane_y[0] + 0.175],
    [plane_x[0] - 0.21, plane_y[0] - 0.175],
])
plane_patch = patches.Polygon(
    plane_points,
    closed=True,
    facecolor="#333333",
    edgecolor="#111111",
    linewidth=2,
    zorder=20,
)
ax.add_patch(plane_patch)

# Game over text (hidden initially)
game_over_text = ax.text(5, 3, "", fontsize=24, ha="center", va="center",
                         color="red", fontweight="bold", visible=False, zorder=100)

# Remove axes for a cleaner look
ax.axis("off")

# Connect keyboard events
fig.canvas.mpl_connect("key_press_event", on_key)

# Animate clouds drifting left to right
anim = FuncAnimation(fig, animate_frame, interval=50, cache_frame_data=False)

plt.tight_layout()
plt.title("WASD = fly plane  |  ↑↓ = resize mountain  |  Avoid clouds!", fontsize=10)
plt.show()
