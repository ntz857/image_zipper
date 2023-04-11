import streamlit as st
from PIL import Image
import io
import zipfile
import base64

def main():
    st.set_page_config(page_title="图像合成", page_icon="🎨", layout="wide", initial_sidebar_state="collapsed")

    st.title("图像合成")
    st.markdown("上传前景图像和背景图像，将前景图像叠加到每个背景图像上，并下载生成的新图像组。")

    uploaded_foregrounds = st.file_uploader("上传前景图像（可以多选）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    uploaded_backgrounds = st.file_uploader("上传背景图像（可以多选）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if st.button("生成并下载图像"):
        if uploaded_foregrounds and uploaded_backgrounds:
            output_images = []

            for i, background_file in enumerate(uploaded_backgrounds):
                background = Image.open(background_file).convert("RGBA")

                for j, foreground_file in enumerate(uploaded_foregrounds):
                    foreground = Image.open(foreground_file).convert("RGBA")
                    # 如果前景图像比背景图像大，将背景图像扩展到和前景图像一样的大小
                    if foreground.width > background.width or foreground.height > background.height:
                        background = background.resize((foreground.width, foreground.height), Image.BICUBIC)
                        # background = Image.effect_mandelbrot(background.size, (0, 0, background.width // 2, background.height // 2), 32)

                    composite_image = Image.new("RGBA", background.size)
                    composite_image.paste(background, (0, 0))

                    # 计算前景图像的位置，使其在背景图像上居中
                    position = ((background.width - foreground.width) // 2, (background.height - foreground.height) // 2)
                    composite_image.alpha_composite(foreground, position)

                    output_images.append(composite_image)
            
            for i, img in enumerate(output_images):
                st.image(img, caption=f"合成图像 {i+1}")

            if len(output_images) == 1:
                # 如果只有一张图像，并且正在运行在移动设备上，则直接下载图像，而不是打包成ZIP文件
                with io.BytesIO() as buffer:
                    output_images[0].save(buffer, format="PNG")
                    buffer.seek(0)
                    b64 = base64.b64encode(buffer.getvalue()).decode()
                    href = f'<a href="data:image/png;base64,{b64}" download="合成图像.png">点击下载合成图像</a>'
                    st.markdown(href, unsafe_allow_html=True)
            elif len(output_images) > 0:              
                #将它们打包成一个ZIP文件，并提供一个链接以便下载
                with io.BytesIO() as buffer:
                    with zipfile.ZipFile(buffer, "w") as zip_file:
                        for i, img in enumerate(output_images):
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format="PNG")
                            zip_file.writestr(f"合成图像 {i+1}.png", img_bytes.getvalue())
                    buffer.seek(0)
                    b64 = base64.b64encode(buffer.getvalue()).decode()
                    href = f'<a href="data:application/zip;base64,{b64}" download="合成图像.zip">点击下载所有合成图像</a>'
                    st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("请确保已经上传前景图像和背景图像组。")

if __name__ == "__main__":
    main()
