import streamlit as st
import os
import shutil
from PIL import Image
import pandas as pd
import base64

def get_file_size(file_path):
    return os.path.getsize(file_path)

def get_file_type(file_path):
    _, extension = os.path.splitext(file_path)
    return extension

def get_file_info(file_path):
    return {
        'Size': get_file_size(file_path),
        'Type': get_file_type(file_path),
        'Last Modified': os.path.getmtime(file_path)
    }

def display_file(file_path):
    file_type = get_file_type(file_path).lower()
    
    if file_type in ['.txt', '.py', '.java', '.cpp']:
        with open(file_path, 'r') as file:
            st.text(file.read())
    elif file_type in ['.png', '.jpg', '.jpeg', '.gif']:
        st.image(Image.open(file_path))
    elif file_type in ['.mp3', '.wav']:
        st.audio(file_path)
    elif file_type in ['.mp4', '.avi', '.mov']:
        st.video(file_path)
    elif file_type == '.pdf':
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.write("Không thể hiển thị file này.")

def main():
    st.title("Trình duyệt tệp Streamlit")

    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.getcwd()

    st.sidebar.title("Chức năng")

    # Mở thư mục
    new_path = st.sidebar.text_input("Đường dẫn thư mục:", st.session_state.current_path)
    if new_path != st.session_state.current_path:
        if os.path.exists(new_path) and os.path.isdir(new_path):
            st.session_state.current_path = new_path
        else:
            st.sidebar.error("Đường dẫn không hợp lệ!")

    # Tạo thư mục/tệp mới
    new_item = st.sidebar.text_input("Tên thư mục/tệp mới:")
    create_type = st.sidebar.radio("Loại:", ("Thư mục", "Tệp"))
    if st.sidebar.button("Tạo"):
        new_path = os.path.join(st.session_state.current_path, new_item)
        if create_type == "Thư mục":
            os.makedirs(new_path, exist_ok=True)
        else:
            open(new_path, 'a').close()

    # Xóa thư mục/tệp
    delete_item = st.sidebar.selectbox("Chọn mục để xóa:", os.listdir(st.session_state.current_path))
    if st.sidebar.button("Xóa"):
        delete_path = os.path.join(st.session_state.current_path, delete_item)
        if os.path.isdir(delete_path):
            shutil.rmtree(delete_path)
        else:
            os.remove(delete_path)

    # Di chuyển tệp/thư mục
    move_item = st.sidebar.selectbox("Chọn mục để di chuyển:", os.listdir(st.session_state.current_path))
    move_to = st.sidebar.text_input("Di chuyển đến:")
    if st.sidebar.button("Di chuyển"):
        source = os.path.join(st.session_state.current_path, move_item)
        destination = os.path.join(move_to, move_item)
        shutil.move(source, destination)

    # Hiển thị nội dung thư mục
    st.write(f"Nội dung của: {st.session_state.current_path}")
    for item in os.listdir(st.session_state.current_path):
        col1, col2, col3 = st.columns([3, 1, 1])
        item_path = os.path.join(st.session_state.current_path, item)
        
        if os.path.isdir(item_path):
            if col1.button(f"📁 {item}"):
                st.session_state.current_path = item_path
        else:
            if col1.button(f"📄 {item}"):
                file_info = get_file_info(item_path)
                st.write(f"Thông tin file: {file_info}")
                display_file(item_path)
        
        if col2.button("Thông tin", key=f"info_{item}"):
            st.write(get_file_info(item_path))
        
        if col3.button("Xóa", key=f"delete_{item}"):
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

if __name__ == "__main__":
    main()
