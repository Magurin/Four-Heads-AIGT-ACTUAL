import cv2
import numpy as np

def apply_yolo_object_detection(image_to_process):
    """
     Распознает и определяет координаты объектов на изображении
        :параметр image_to_process: исходное изображение
        :return: изображение с выделенными объектами и подписями к ним  
    """

    height, width, _ = image_to_process.shape
    blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (608, 608),
                                 (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outs = net.forward(out_layers)
    class_indexes, class_scores, boxes = ([] for i in range(3))
    objects_count = 0

    # Запуск поиска объектов на изображении
    for out in outs:
        for obj in out:
            scores = obj[5:]
            class_index = np.argmax(scores)
            class_score = scores[class_index]
            if class_score > 0:
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                obj_width = int(obj[2] * width)
                obj_height = int(obj[3] * height)
                box = [center_x - obj_width // 2, center_y - obj_height // 2,
                       obj_width, obj_height]
                boxes.append(box)
                class_indexes.append(class_index)
                class_scores.append(float(class_score))

    # Подбор
    chosen_boxes = cv2.dnn.NMSBoxes(boxes, class_scores, 0.0, 0.4)
    for box_index in chosen_boxes:
        box_index = box_index
        box = boxes[box_index]
        class_index = class_indexes[box_index]

        # Для отладки мы рисуем объекты, входящие в нужные классы
        if classes[class_index] in classes_to_look_for:
            objects_count += 1
            image_to_process = draw_object_bounding_box(image_to_process,
                                                        class_index, box)

    final_image = draw_object_count(image_to_process, objects_count)
    return final_image


def draw_object_bounding_box(image_to_process, index, box):
    """
      Рисование границ объектов с подписями
        :параметр image_to_process: исходное изображение
        :параметр index: индекс класса объекта, определенного с помощью YOLO
        :параметр box: координаты области вокруг объекта
        :return: изображение с отмеченными объектами
    """

    x, y, w, h = box
    start = (x, y)
    end = (x + w, y + h)
    color = (0, 255, 0)
    width = 2
    final_image = cv2.rectangle(image_to_process, start, end, color, width)

    start = (x, y - 10)
    font_size = 1
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 2
    text = classes[index]
    final_image = cv2.putText(final_image, text, start, font,
                              font_size, color, width, cv2.LINE_AA)

    return final_image


def draw_object_count(image_to_process, objects_count):
    """
    Подпись количества найденных объектов на изображении
      :параметр image_to_process: исходное изображение
      :параметр objects_count: количество объектов нужного класса
      :return: изображение с помеченным количеством найденных объектов
    """

    start = (10, 120)
    font_size = 1.5
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 3
    text = "Objects found: " + str(objects_count)

    # Текст выводится обводкой
    # (чтобы его было видно при разном освещении изображения)
    white_color = (255, 255, 255)
    black_outline_color = (0, 0, 0)
    final_image = cv2.putText(image_to_process, text, start, font, font_size,
                              black_outline_color, width * 3, cv2.LINE_AA)
    final_image = cv2.putText(final_image, text, start, font, font_size,
                              white_color, width, cv2.LINE_AA)

    return final_image


def start_video_object_detection(video: str):
    """
    Захват и анализ видео в режиме реального времени
    """

    while True:
        try:
            # Захват изображения из видео
            video_camera_capture = cv2.VideoCapture(video)
            
            while video_camera_capture.isOpened():
                ret, frame = video_camera_capture.read()
                if not ret:
                    break
                
                # Применение методов распознавания объектов на видеокадре от YOLO
                frame = apply_yolo_object_detection(frame)
                
                # Отображение обработанного изображения на экране с уменьшенным размером окна
                frame = cv2.resize(frame, (1920 // 2, 1080 // 2))
                cv2.imshow("Video Capture", frame)
                cv2.waitKey(1)
            
            video_camera_capture.release()
            cv2.destroyAllWindows()
    
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    # Загрузка "весов" YOLO из файлов и настройка сети
    net = cv2.dnn.readNetFromDarknet("Resources/yolov4-tiny.cfg",
                                     "Resources/yolov4-tiny.weights")
    layer_names = net.getLayerNames()
    out_layers_indexes = net.getUnconnectedOutLayers()
    out_layers = [layer_names[index - 1] for index in out_layers_indexes]

     # Загрузка из файла классов объектов, которые YOLO может обнаружить
    with open("Resources/coco.names.txt") as file:
        classes = file.read().split("\n")

    # Определение классов, которым будет присвоен приоритет при поиске по изображению
    # Названия указаны в файле coco.names.txt

    video = input("Path to video (or URL): ")
    look_for = input("What we are looking for: ").split(',')
    
    # Удаление пробелов(если в look_for вводить данные через консоль)
    list_look_for = []
    for look in look_for:
        list_look_for.append(look.strip())

    classes_to_look_for = list_look_for

    start_video_object_detection(video)
