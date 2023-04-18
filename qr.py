import streamlit as st
import cv2
import numpy as np
from PIL import Image

def find_blank_area(img, threshold=250, min_area=1000, aspect_ratio_tolerance=0.1, avg_white_threshold=220):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations=4)
    st.image(dilation, caption="膨胀操作后的图像", use_column_width=True)

    erosion = cv2.erode(dilation, kernel, iterations=4)
    st.image(erosion, caption="腐蚀操作后的图像", use_column_width=True)

    contours, _ = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = img.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
    st.image(contour_img, caption="找到的轮廓", use_column_width=True)

    max_area = 0
    max_rect = None
    for contour in contours:
        hull = cv2.convexHull(contour)
        area = cv2.contourArea(hull)
        if area > min_area:
            rect = cv2.boundingRect(hull)
            x, y, w, h = rect
            aspect_ratio = float(w) / h
            if (1 - aspect_ratio_tolerance) <= aspect_ratio <= (1 + aspect_ratio_tolerance):
                roi = gray_img[y:y+h, x:x+w]
                avg_value = np.mean(roi)
                if avg_value > avg_white_threshold:
                    if area > max_area:
                        max_area = area
                        max_rect = rect

    return max_rect





def overlay_images(bg_img, fg_img, x, y, w, h):
    # 保持前景图片的宽高比
    fg_width, fg_height = fg_img.size
    ratio = min(w / fg_width, h / fg_height)
    new_fg_size = (int(fg_width * ratio), int(fg_height * ratio))
    
    fg_img = fg_img.resize(new_fg_size, Image.ANTIALIAS)
    bg_img.paste(fg_img, (x + w // 2 - new_fg_size[0] // 2, y + h // 2 - new_fg_size[1] // 2), fg_img)
    return bg_img

st.title("二维码自动叠加")

bg_img_file = st.file_uploader("请选择背景图片", type=["jpg", "jpeg", "png"])
fg_img_file = st.file_uploader("请选择二维码图片", type=["jpg", "jpeg", "png"])

if bg_img_file is not None and fg_img_file is not None:
    bg_img = Image.open(bg_img_file).convert("RGBA")
    fg_img = Image.open(fg_img_file).convert("RGBA")
    bg_img_cv2 = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGBA2BGR)

    blank_area = find_blank_area(bg_img_cv2)
    if blank_area:
        x, y, w, h = blank_area
        result_img = overlay_images(bg_img, fg_img, x, y, w, h)
        st.image(result_img, caption="叠加后的图片", use_column_width=True)
    else:
        st.warning("未找到空白区域。")
