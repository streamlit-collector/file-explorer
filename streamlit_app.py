import streamlit as st
import os
import shutil
from PIL import Image
import mimetypes

def get_file_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.split('/')[0]
    return 'unknown'

def rename_item(old_path, new_name):
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    os.rename(old_path, new_path)

def delete_item(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

def display_file_content(file_path):
    file_type = get_file_type(file_path)
    
    if file_type == 'text':
        with open(file_path, 'r') as file:
            st.text_area("Nội dung file", file.read(), height=300)
    elif file_type == 'image':
        st.image(Image.open(file_path))
    elif file_type == 'video':
        video_file = open(file_path, 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
    elif file_type == 'audio':
        audio_file = open(file_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
    else:
        st.write("Không thể hiển thị nội dung của file này.")

def main():
    st.title("File Explorer")

    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.path.expanduser("~")
    
    if 'upload_success' not in st.session_state:
        st.session_state.upload_success = False

    if st.button("⬆️ Lên thư mục cha"):
        st.session_state.current_path = os.path.dirname(st.session_state.current_path)

    st.write(f"Đường dẫn hiện tại: {st.session_state.current_path}")

    items = os.listdir(st.session_state.current_path)
    for item in items:
        item_path = os.path.join(st.session_state.current_path, item)
        col1, col2 = st.columns([5, 1])
        
        with col1:
            if os.path.isdir(item_path):
                if st.button(f"📁 {item}", key=f"dir_{item}"):
                    st.session_state.current_path = item_path
                    st.experimental_rerun()
            else:
                if st.button(f"📄 {item}", key=f"file_{item}"):
                    display_file_content(item_path)
        
        with col2:
            option = st.selectbox("", ["...", "Đổi tên", "Xóa", "Tải xuống"], key=f"option_{item}")
            if option == "Đổi tên":
                new_name = st.text_input(f"Đổi tên {item}", value=item, key=f"rename_{item}")
                if st.button("Xác nhận", key=f"confirm_rename_{item}"):
                    rename_item(item_path, new_name)
                    st.experimental_rerun()
            elif option == "Xóa":
                if st.button("Xác nhận xóa", key=f"confirm_delete_{item}"):
                    delete_item(item_path)
                    st.experimental_rerun()
            elif option == "Tải xuống" and os.path.isfile(item_path):
                with open(item_path, "rb") as file:
                    btn = st.download_button(
                        label="Xác nhận tải xuống",
                        data=file,
                        file_name=item,
                        mime="application/octet-stream",
                        key=f"download_{item}"
                    )

    uploaded_file = st.file_uploader("Chọn file để upload", type=None)
    if uploaded_file is not None:
        file_path = os.path.join(st.session_state.current_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.upload_success = True
    
    if st.session_state.upload_success:
        st.success(f"File {uploaded_file.name} đã được upload thành công!")
        st.session_state.upload_success = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
