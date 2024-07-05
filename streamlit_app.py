import streamlit as st
import os
import shutil
from PIL import Image

def main():
    st.title("File Explorer")

    # Lấy đường dẫn hiện tại
    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.getcwd()

    # Hiển thị đường dẫn hiện tại
    st.write(f"Current path: {st.session_state.current_path}")

    # Nút để quay lại thư mục cha
    if st.button("Go to parent directory"):
        st.session_state.current_path = os.path.dirname(st.session_state.current_path)
        st.experimental_rerun()

    # Hiển thị danh sách tệp và thư mục
    files_and_dirs = os.listdir(st.session_state.current_path)
    for item in files_and_dirs:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        full_path = os.path.join(st.session_state.current_path, item)
        
        if os.path.isdir(full_path):
            with col1:
                if st.button(f"📁 {item}", key=f"dir_{item}"):
                    st.session_state.current_path = full_path
                    st.experimental_rerun()
        else:
            with col1:
                st.write(f"📄 {item}")
        
        # Nút để đổi tên
        with col2:
            if st.button("Rename", key=f"rename_{item}"):
                new_name = st.text_input(f"New name for {item}", value=item)
                if new_name and new_name != item:
                    os.rename(full_path, os.path.join(st.session_state.current_path, new_name))
                    st.experimental_rerun()

        # Nút để mở tệp
        with col3:
            if os.path.isfile(full_path):
                if st.button("Open", key=f"open_{item}"):
                    file_extension = os.path.splitext(item)[1].lower()
                    if file_extension in ['.txt', '.py', '.md']:
                        with open(full_path, 'r') as file:
                            st.text_area("File Content", file.read(), height=300)
                    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                        st.image(Image.open(full_path))
                    elif file_extension in ['.mp3', '.wav']:
                        st.audio(full_path)
                    elif file_extension in ['.mp4', '.avi', '.mov']:
                        st.video(full_path)
                    else:
                        st.write("Unsupported file type")

        # Nút để xóa
        with col4:
            if st.button("Delete", key=f"delete_{item}"):
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                st.experimental_rerun()

if __name__ == "__main__":
    main()
