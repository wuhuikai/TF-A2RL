# -*- coding: utf-8 -*-
import numpy as np
import skimage.transform as transform

def command2action(command_ids, ratios, terminals):
    batch_size = len(command_ids)
    for i in range(batch_size):
        if terminals[i] == 1:
            continue
        if command_ids[i] == 0:
            ratios[i, 0] += 1
            ratios[i, 1] += 1
            ratios[i, 2] -= 1
            ratios[i, 3] -= 1
        elif command_ids[i] == 1:
            ratios[i, 2] -= 1
            ratios[i, 3] -= 1
        elif command_ids[i] == 2:
            ratios[i, 0] += 1
            ratios[i, 3] -= 1
        elif command_ids[i] == 3:
            ratios[i, 1] += 1
            ratios[i, 2] -= 1
        elif command_ids[i] == 4:
            ratios[i, 0] += 1
            ratios[i, 1] += 1
        elif command_ids[i] == 5:
            ratios[i, 0] += 1
            ratios[i, 2] += 1
        elif command_ids[i] == 6:
            ratios[i, 0] -= 1
            ratios[i, 2] -= 1
        elif command_ids[i] == 7:
            ratios[i, 1] -= 1
            ratios[i, 3] -= 1
        elif command_ids[i] == 8:
            ratios[i, 1] += 1
            ratios[i, 3] += 1
        elif command_ids[i] == 9:
            ratios[i, 1] += 1
            ratios[i, 3] -= 1
        elif command_ids[i] == 10:
            ratios[i, 0] += 1
            ratios[i, 2] -= 1
        elif command_ids[i] == 11:
            ratios[i, 1] -= 1
            ratios[i, 3] += 1
        elif command_ids[i] == 12:
            ratios[i, 0] -= 1
            ratios[i, 2] += 1
        elif command_ids[i] == 13:
            terminals[i] = 1
        else:
            raise NameError('undefined command type !!!')

        ratios = np.maximum(ratios, 0)
        ratios = np.minimum(ratios, 20)
        if ratios[i, 2] - ratios[i, 0] <= 4 or ratios[i, 3] - ratios[i, 1] <= 4:
            terminals[i] = 1

    return ratios, terminals

def generate_bbox(input_np, ratios):
    assert len(input_np) == len(ratios)

    bbox = []
    for im, ratio in zip(input_np, ratios):
        height, width = im.shape[:2]
        xmin = int(float(ratio[0]) / 20 * width)
        ymin = int(float(ratio[1]) / 20 * height)
        xmax = int(float(ratio[2]) / 20 * width)
        ymax = int(float(ratio[3]) / 20 * height)
        
        bbox.append((xmin, ymin, xmax, ymax))
        
    return bbox
    
def crop_input(input_np, bbox):
        assert len(input_np) == len(bbox)
    
        result = [transform.resize(im[ymin:ymax, xmin:xmax], (227, 227), mode='constant')
                        for im, (xmin, ymin, xmax, ymax) in zip(input_np, bbox)]
    
        return np.asarray(result, dtype=np.float32)