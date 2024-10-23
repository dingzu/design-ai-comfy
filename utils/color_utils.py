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