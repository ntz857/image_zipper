import streamlit as st
from PIL import Image, ImageOps

def create_collage(images, cols, rows, output_path, fill_method):
    """
    拼接图片成为 cols * rows 的网格
    """
    # 获取第一张图片的尺寸
    width, height = images[0].size
    
    # 计算拼接后的图片尺寸
    collage_width = width * cols
    collage_height = height * rows
    
    # 创建空白拼接图片
    collage = Image.new('RGB', (collage_width, collage_height))
    
    # 遍历每张图片进行拼接
    for i, img in enumerate(images):
        # 计算图片在拼接图片中的位置
        x_offset = i % cols * width
        y_offset = i // cols * height
        
        # 调整图片尺寸以填满宫格
        if fill_method == "拉伸":
            img = img.resize((width, height), Image.LANCZOS)
        elif fill_method == "裁切":
            img = ImageOps.fit(img, (width, height), Image.LANCZOS)
        
        # 将调整后的图片粘贴到拼接图片中
        collage.paste(img, (x_offset, y_offset))
    
    # 保存拼接后的图片
    collage.save(output_path)

def main():
    st.title("图片拼接")
    st.write("上传3:4比例的图片，选择拼接方式，并生成对应的宫格图片")
    
    # 上传图片
    uploaded_files = st.file_uploader("上传图片", accept_multiple_files=True, type=["jpg", "png", "jpeg"])
    
    # 选择填充方式
    fill_method = st.radio("选择填充方式", ("拉伸", "裁切"))
    
    if uploaded_files:
        num_images = len(uploaded_files)
        
        # 根据图片数量选择拼接模式和行列数
        if num_images <= 4:
            cols, rows = 2, 2
        elif num_images <= 6:
            cols, rows = 3, 2
        else:
            cols, rows = 3, 3
        
        images = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            images.append(image)
        
        # 生成拼接后的图片
        collage_output = "collage.jpg"
        create_collage(images, cols, rows, collage_output, fill_method)
        
        # 显示拼接后的图片
        st.image(collage_output, caption='拼接后的图片', use_column_width=True)
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
