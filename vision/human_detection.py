def find_human(results):
    biggest_area = 0
    best_box = None

    for result in results:
        boxes = result.boxes.cpu().numpy()
        class_ids = boxes.cls
        confidences = boxes.conf
        xyxys = boxes.xyxy

        for i, class_id in enumerate(class_ids):
            class_name = result.names[int(class_id)]
            if class_name == "person":
                x_min, y_min, x_max, y_max = xyxys[i]
                area = max(0, x_max - x_min) * max(0, y_max - y_min)
                print(f"Found human with confidence {confidences[i]:.2f} at {xyxys[i]}, area: {area}")
                if area > biggest_area:
                    biggest_area = area
                    best_box = xyxys[i]

    return (True, best_box) if best_box is not None else (False, None)
