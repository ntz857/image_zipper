import streamlit as st
from PIL import Image
import io
import zipfile
import base64

def main():
    st.set_page_config(page_title="图像合成", page_icon="🎨", layout="wide", initial_sidebar_state="collapsed")

    st.title("图像合成")
    st.markdown("上传一张前景图像和一组背景图像，将前景图像叠加到每个背景图像上，并下载生成的新图像组。")

    uploaded_foreground = st.file_uploader("上传前景图像", type=["png", "jpg", "jpeg"])
    uploaded_backgrounds = st.file_uploader("上传背景图像组（可以多选）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if st.button("生成并下载图像ZIP文件"):
        if uploaded_foreground and uploaded_backgrounds:
            foreground = Image.open(uploaded_foreground).convert("RGBA")
            output_images = []

            for i, background_file in enumerate(uploaded_backgrounds):
                background = Image.open(background_file).convert("RGBA")

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

            with io.BytesIO() as buffer:
                with zipfile.ZipFile(buffer, mode="w") as zf:
                    for i, img in enumerate(output_images):
                        with io.BytesIO() as img_bytes:
                            img.save(img_bytes, format="PNG")
                            img_bytes.seek(0)
                            zf.writestr(f"合成图像_{i+1}.png", img_bytes.read())

                buffer.seek(0)
                b64 = base64.b64encode(buffer.getvalue()).decode()
                href = f'<a href="data:application/zip;base64,{b64}" download="output_images.zip">点击下载合成图像ZIP文件</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("请确保已经上传前景图像和背景图像组。")

if __name__ == "__main__":
    main()
