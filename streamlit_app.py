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
        st.audio(open(file_path, 'rb').read())
    elif file_type in ['.mp4', '.avi', '.mov']:
        st.video(open(file_path, 'rb').read())
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
    
    if 'navigation_history' not in st.session_state:
        st.session_state.navigation_history = []

    st.sidebar.title("Chức năng")

    # Mở thư mục
    new_path = st.sidebar.text_input("Đường dẫn thư mục:", st.session_state.current_path)
    if new_path != st.session_state.current_path:
        if os.path.exists(new_path) and os.path.isdir(new_path):
            st.session_state.current_path = new_path
            st.session_state.navigation_history.append(new_path)
        else:
            st.sidebar.error("Đường dẫn không hợp lệ!")

    # Upload file
    with st.sidebar.expander("Upload file"):
        uploaded_file = st.file_uploader("Chọn file để upload", type=None)
        if uploaded_file is not None:
            file_path = os.path.join(st.session_state.current_path, uploaded_file.name)
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Đã upload file {uploaded_file.name} thành công!")
            except Exception as e:
                st.error(f"Lỗi khi upload file: {str(e)}")

    # Tạo thư mục/tệp mới
    with st.sidebar.expander("Tạo mới"):
        new_item = st.text_input("Tên thư mục/tệp mới:")
        create_type = st.radio("Loại:", ("Thư mục", "Tệp"))
        if st.button("Tạo"):
            new_path = os.path.join(st.session_state.current_path, new_item)
            if create_type == "Thư mục":
                os.makedirs(new_path, exist_ok=True)
            else:
                open(new_path, 'a').close()

    # Xóa thư mục/tệp
    with st.sidebar.expander("Xóa"):
        delete_item = st.selectbox("Chọn mục để xóa:", os.listdir(st.session_state.current_path))
        if st.button("Xóa"):
            delete_path = os.path.join(st.session_state.current_path, delete_item)
            if os.path.isdir(delete_path):
                shutil.rmtree(delete_path)
            else:
                os.remove(delete_path)

    # Di chuyển tệp/thư mục
    with st.sidebar.expander("Di chuyển"):
        move_item = st.selectbox("Chọn mục để di chuyển:", os.listdir(st.session_state.current_path))
        move_to = st.text_input("Di chuyển đến:")
        if st.button("Di chuyển"):
            source = os.path.join(st.session_state.current_path, move_item)
            destination = os.path.join(move_to, move_item)
            shutil.move(source, destination)

    # Hiển thị nội dung thư mục
    st.write(f"Nội dung của: {st.session_state.current_path}")
    
    # Thêm nút để điều hướng đến thư mục cha
    if st.button("📁 .."):
        parent_dir = os.path.dirname(st.session_state.current_path)
        st.session_state.navigation_history.append(parent_dir)
        st.experimental_rerun()
    
    for item in os.listdir(st.session_state.current_path):
        item_path = os.path.join(st.session_state.current_path, item)
        
        if os.path.isdir(item_path):
            if st.button(f"📁 {item}", key=f"dir_{item}"):
                st.session_state.navigation_history.append(item_path)
                st.experimental_rerun()
        else:
            if st.button(f"📄 {item}", key=f"file_{item}"):
                file_info = get_file_info(item_path)
                st.write(f"Thông tin file: {file_info}")
                display_file(item_path)

    # Xử lý điều hướng
    if st.session_state.navigation_history:
        st.session_state.current_path = st.session_state.navigation_history.pop()

if __name__ == "__main__":
    main()
