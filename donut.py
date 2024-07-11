import numpy as np
import os
from time import sleep
from numba import njit

screen_width, screen_height = 70, 70
theta_spacing = 0.07
phi_spacing = 0.02

R1 = 1
R2 = 2
K2 = 5

K1 = screen_width * K2 * 3 / (8 * (R1 + R2))
K1_S = K1 * 0.5

def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

@njit
def render_frame(A, B):
    cos_A, sin_A = np.cos(A), np.sin(A)
    cos_B, sin_B = np.cos(B), np.sin(B)

    output = np.zeros((screen_width, screen_height), dtype=np.uint8)
    z_buffer = np.zeros((screen_width, screen_height))

    for theta in np.arange(0, 2 * np.pi, theta_spacing):
        cos_theta, sin_theta = np.cos(theta), np.sin(theta)
        circle_x, circle_y = R2 + R1 * cos_theta, R1 * sin_theta

        for phi in np.arange(0, 2 * np.pi, phi_spacing):
            cos_phi, sin_phi = np.cos(phi), np.sin(phi)

            x = circle_x * (cos_B * cos_phi + sin_A * sin_B * sin_phi) - circle_y * cos_A * sin_B
            y = circle_x * (sin_B * cos_phi - sin_A * cos_B * sin_phi) + circle_y * cos_A * cos_B
            z = K2 + cos_A * circle_x * sin_phi + circle_y * sin_A
            z_recip = 1 / z

            xp = int(screen_width / 2 + K1_S * z_recip * x)
            yp = int(screen_height / 2 - K1 * z_recip * y)

            luminance = cos_phi * cos_theta * sin_B - cos_A * cos_theta * sin_phi - sin_A * sin_theta + cos_B * (cos_A * sin_theta - cos_theta * sin_A * sin_phi)

            if luminance > 0:
                if z_recip > z_buffer[xp, yp]:
                    z_buffer[xp, yp] = z_recip
                    luminance_index = min(int(luminance * 8), 11)
                    output[xp, yp] = luminance_index

    return output

def draw_frame(A, B):
    frame = render_frame(A, B)
    ascii_f_map = map(lambda row: "".join(map(lambda luminance_index: " .,-~:=!*#$@"[luminance_index], row)), frame)
    clear_screen()
    print(*ascii_f_map, sep="\n")

def main(angle_increment=0.1):
    A = 0
    B = 0
    while True:
        A += angle_increment
        B += angle_increment
        draw_frame(A, B)


if __name__ == "__main__":
    main()
