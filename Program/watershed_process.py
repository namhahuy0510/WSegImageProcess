import cv2
import numpy as np
import os

def watershed_segmentation(image_path, save_path=None):
    # Đọc ảnh gốc
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

    # Chuyển sang grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Làm mờ để giảm nhiễu
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Ngưỡng nhị phân (binary)
    ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Tìm sure background (dùng dilation)
    kernel = np.ones((3, 3), np.uint8)
    sure_bg = cv2.dilate(thresh, kernel, iterations=3)

    # Tìm sure foreground (dùng distance transform)
    dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

    # Unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Marker labeling
    ret, markers = cv2.connectedComponents(sure_fg)

    # Tăng marker để không bị trùng với background
    markers = markers + 1
    markers[unknown == 255] = 0

    # Áp dụng watershed
    markers = cv2.watershed(img, markers)
    img[markers == -1] = [0, 0, 255]  # biên màu đỏ

    # Lưu kết quả nếu có save_path
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, img)
        print(f"Ảnh kết quả đã lưu tại: {save_path}")

    return img


if __name__ == "__main__":
    # Ví dụ chạy trực tiếp
    input_image = "D:/Project/WSegImageProcess/Program/test.jpg"
    output_image = "D:/Project/WSegImageProcess/Program/Saved/watershed_result.jpg"

    result = watershed_segmentation(input_image, output_image)

    # Hiển thị kết quả
    cv2.imshow("Watershed Result", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
