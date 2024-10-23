# color_utils.py

import numpy as np

def color_distance(c1, c2):
    return np.sqrt(
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2 +
        (c1[2] - c2[2]) ** 2
    )

def average_colors(c1, c2):
    return [
        round((c1[0] + c2[0]) / 2),
        round((c1[1] + c2[1]) / 2),
        round((c1[2] + c2[2]) / 2),
    ]

def merge_similar_colors(palette, threshold=30):
    merged_palette = []
    for color in palette:
        similar_color = next(
            (c for c in merged_palette if color_distance(c['color'], color) < threshold),
            None
        )
        if similar_color:
            similar_color['count'] += 1
            similar_color['color'] = average_colors(similar_color['color'], color)
        else:
            merged_palette.append({'color': color, 'count': 1})
    return merged_palette

def adaptive_merge(palette):
    min_distance = float('inf')
    pair = None
    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            distance = color_distance(palette[i]['color'], palette[j]['color'])
            if distance < min_distance:
                min_distance = distance
                pair = [i, j]

    if pair:
        i, j = pair
        new_color = average_colors(palette[i]['color'], palette[j]['color'])
        new_count = palette[i]['count'] + palette[j]['count']
        palette[i] = {'color': new_color, 'count': new_count}
        del palette[j]

    return palette

def calculate_average_color(palette):
    sum_color = np.sum([c['color'] for c in palette], axis=0)
    return [round(v / len(palette)) for v in sum_color]

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(color1, color2):
    lum1 = relative_luminance(color1)
    lum2 = relative_luminance(color2)
    if lum1 > lum2:
        return (lum1 + 0.05) / (lum2 + 0.05)
    else:
        return (lum2 + 0.05) / (lum1 + 0.05)