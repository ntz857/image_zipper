import streamlit as st
import math
from PIL import Image, ImageOps

def create_collage(images, ratio, cols, rows, output_path, fill_method, padding):
    """
    拼接图片成为 cols * rows 的网格，包括最外圈的padding
    """
    total_width = 1200
    #根据ratio计算出每张图片的高度，("3:4", "1:1", "4:3", "16:9", "9:16")
    w, h = ratio.split(':')
    
    # 计算高度
    total_height = total_width * int(h) // int(w)

    # 计算可用于图片的宽度和高度（去除所有padding后）
    available_width = total_width - padding * (cols + 1)  # +1 表示两边的padding
    available_height = total_height - padding * (rows + 1)  # +1 表示上下的padding
    
    # 获取单个图片的尺寸
    width = available_width // cols
    height = available_height // rows
    
    # 计算拼接后的图片尺寸，包含所有padding（包括四周的padding）
    collage_width = width * cols + padding * (cols + 1)
    collage_height = height * rows + padding * (rows + 1)
    
    # 创建空白拼接图片（白色背景）
    collage = Image.new('RGB', (collage_width, collage_height), (238, 238, 238))
    
    # 遍历每张图片进行拼接
    for i, img in enumerate(images):
        if i >= rows * cols:  # 超出网格范围的图片不处理
            break
            
        # 计算图片在拼接图片中的位置（考虑外圈padding）
        x_offset = padding + (i % cols) * (width + padding)
        y_offset = padding + (i // cols) * (height + padding)
        
        # 调整图片尺寸以填满宫格
        if fill_method == "拉伸":
            img = img.resize((width, height), Image.LANCZOS)
        elif fill_method == "裁切":
            img = ImageOps.fit(img, (width, height), Image.LANCZOS)
        
        # 将调整后的图片粘贴到拼接图片中
        collage.paste(img, (x_offset, y_offset))
    
    # 保存拼接后的图片
    collage.save(output_path)

# 版本1
# def calculate_layout(item_count,prefer='横向'):
#     # 首先，获取item数量的平方根
#     sqrt = math.sqrt(item_count)

#     # 按照四舍五入的方法，获得最接近的整数来作为行数和列数
#     approx = round(sqrt)

#     # 检查这个布局是否提供足够的空间来存放所有的图片
#     if approx * approx < item_count:
#         rows = approx
#         cols = approx
#         if prefer == '横向':
#             rows = approx + 1
#         else:
#             cols = approx + 1
#     else:
#         rows = approx
#         cols = approx

#     # 如果这个布局提供的空间过多，那么将减少一行来获取更适合的布局
#     if prefer == 'horizontal':
#         while (cols - 1) * rows >= item_count:
#             cols = cols - 1
#     else:
#         while (rows - 1) * cols >= item_count:
#             rows = rows - 1

#     return cols, rows

# 版本2 
def calculate_layout(item_count,prefer='横向'):
    if item_count == 1:
        return 1, 1
    # 获取因数
    factors = [i for i in range(2, item_count + 1) if item_count % i == 0]

    # 找到最接近平方根的因数对
    sqrt = math.sqrt(item_count) 
    rows, cols = min((abs(sqrt - factor), factor, item_count // factor) for factor in factors)[1:]

    if (prefer == "横向" and rows > cols) or (prefer == "纵向" and cols > rows):
        rows, cols = cols, rows

    return cols, rows

 


def main():
    st.title("图片拼接")
    st.write("上传图片，选择拼接方式，并生成对应的宫格图片，生成比例")

    # 上传图片
    uploaded_files = st.file_uploader("上传图片", accept_multiple_files=True, type=["jpg", "png", "jpeg"])

    # 选择生成图片比例
    ratio = st.radio("选择生成图片比例", ("3:4", "1:1", "4:3", "16:9", "9:16"))

    # 选择填充方式
    fill_method = st.radio("选择填充方式", ("裁切", "拉伸"))

    # 选择布局方式
    prefer_layout = st.radio("选择布局方式", ("纵向", "横向"))
    
    # 选择padding
    padding = st.number_input("选择padding", min_value=0, max_value=100, value=40)
    if uploaded_files:
        num_images = len(uploaded_files)

        # 根据图片数量选择拼接模式和行列数
        # if num_images <= 4:
        #     cols, rows = 2, 2
        # elif num_images <= 6:
        #     cols, rows = 2, 3
        # elif num_images <= 9:
        #     cols, rows = 3, 3

        # else:
        #     cols, rows = 3, 4
        cols, rows = calculate_layout(num_images,prefer_layout)

        images = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            images.append(image)

        # 生成拼接后的图片
        collage_output = "collage.jpg"
        create_collage(images,ratio, cols, rows, collage_output, fill_method, padding)

        # 显示拼接后的图片
        st.image(collage_output, caption='拼接后的图片', use_container_width=True)
        st.text("长按图片下载")
        # # 提供下载链接
        # st.markdown(get_binary_file_downloader_html(collage_output, '图片下载'), unsafe_allow_html=True)

# def get_binary_file_downloader_html(bin_file, file_label='File'):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     bin_str = base64.b64encode(data).decode()
#     href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
#     return href

if __name__ == "__main__":
    main()
