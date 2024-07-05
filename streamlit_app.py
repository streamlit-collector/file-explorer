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
    return new_path

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

def handle_upload():
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file is not None:
        file_path = os.path.join(st.session_state.current_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.upload_message = f"File {uploaded_file.name} đã được upload thành công!"
        st.session_state.uploaded_file = None

def main():
    st.title("File Explorer")

    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.path.expanduser("~")
    
    if 'upload_message' not in st.session_state:
        st.session_state.upload_message = ""
    
    if 'selected_item' not in st.session_state:
        st.session_state.selected_item = None

    # Sidebar
    with st.sidebar:
        st.header("Chức năng")
        
        # File uploader
        st.file_uploader("Chọn file để upload", type=None, key="uploaded_file", on_change=handle_upload)

        # Display upload message
        if st.session_state.upload_message:
            st.success(st.session_state.upload_message)
            st.session_state.upload_message = ""

        if st.session_state.selected_item:
            item_path = os.path.join(st.session_state.current_path, st.session_state.selected_item)
            st.write(f"Đang chọn: {st.session_state.selected_item}")

            # Rename function
            new_name = st.text_input("Đổi tên", value=st.session_state.selected_item)
            if st.button("Xác nhận đổi tên"):
                new_path = rename_item(item_path, new_name)
                st.session_state.selected_item = os.path.basename(new_path)
                st.experimental_rerun()

            # Delete function
            if st.button("Xóa"):
                delete_item(item_path)
                st.session_state.selected_item = None
                st.experimental_rerun()

            # Download function (only for files)
            if os.path.isfile(item_path):
                with open(item_path, "rb") as file:
                    st.download_button(
                        label="Tải xuống",
                        data=file,
                        file_name=st.session_state.selected_item,
                        mime="application/octet-stream"
                    )

    # Main content
    if st.button("⬆️ Lên thư mục cha"):
        st.session_state.current_path = os.path.dirname(st.session_state.current_path)
        st.session_state.selected_item = None

    st.write(f"Đường dẫn hiện tại: {st.session_state.current_path}")

    # Display files and directories
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
                st.session_state.selected_item = item
                display_file_content(item_path)

if __name__ == "__main__":
    main()
