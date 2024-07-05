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

def create_directory(path, name):
    new_dir_path = os.path.join(path, name)
    os.makedirs(new_dir_path, exist_ok=True)

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

def handle_upload():
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file is not None:
        file_path = os.path.join(st.session_state.current_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.upload_message = f"File {uploaded_file.name} đã được upload thành công!"
        st.session_state.uploaded_file = None

def main():
    st.set_page_config(layout="wide")
    st.title("File Explorer")

    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.path.expanduser("~")
    
    if 'upload_message' not in st.session_state:
        st.session_state.upload_message = ""
    
    if 'selected_item' not in st.session_state:
        st.session_state.selected_item = None

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Danh sách tệp và thư mục")
        if st.button("⬆️ Lên thư mục cha"):
            st.session_state.current_path = os.path.dirname(st.session_state.current_path)
            st.session_state.selected_item = None

        st.write(f"Đường dẫn hiện tại: {st.session_state.current_path}")

        items = os.listdir(st.session_state.current_path)
        for item in items:
            item_path = os.path.join(st.session_state.current_path, item)
            if os.path.isdir(item_path):
                if st.button(f"📁 {item}", key=f"dir_{item}"):
                    st.session_state.current_path = item_path
                    st.session_state.selected_item = None
                    st.experimental_rerun()
            else:
                if st.button(f"📄 {item}", key=f"file_{item}"):
                    st.session_state.selected_item = item_path

    with col2:
        if st.session_state.selected_item:
            st.subheader(f"Đang xem: {os.path.basename(st.session_state.selected_item)}")
            display_file_content(st.session_state.selected_item)

    with st.sidebar:
        st.subheader("Chức năng")
        
        st.file_uploader("Chọn file để upload", type=None, key="uploaded_file", on_change=handle_upload)

        if st.session_state.upload_message:
            st.success(st.session_state.upload_message)
            st.session_state.upload_message = ""

        new_dir_name = st.text_input("Tên thư mục mới")
        if st.button("Tạo thư mục mới"):
            if new_dir_name:
                create_directory(st.session_state.current_path, new_dir_name)
                st.success(f"Đã tạo thư mục {new_dir_name}")
                st.experimental_rerun()
            else:
                st.warning("Vui lòng nhập tên thư mục")

        if st.session_state.selected_item:
            selected_name = os.path.basename(st.session_state.selected_item)
            st.subheader(f"Thao tác với: {selected_name}")
            
            new_name = st.text_input("Đổi tên", value=selected_name)
            if st.button("Xác nhận đổi tên"):
                rename_item(st.session_state.selected_item, new_name)
                st.session_state.selected_item = os.path.join(os.path.dirname(st.session_state.selected_item), new_name)
                st.success(f"Đã đổi tên thành {new_name}")
                st.experimental_rerun()

            if st.button("Xóa"):
                delete_item(st.session_state.selected_item)
                st.session_state.selected_item = None
                st.success(f"Đã xóa {selected_name}")
                st.experimental_rerun()

            if os.path.isfile(st.session_state.selected_item):
                with open(st.session_state.selected_item, "rb") as file:
                    st.download_button(
                        label="Tải xuống",
                        data=file,
                        file_name=selected_name,
                        mime="application/octet-stream"
                    )

if __name__ == "__main__":
    main()
