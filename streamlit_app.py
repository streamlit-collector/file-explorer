import streamlit as st
import os
import shutil
from PIL import Image
import pandas as pd
import base64
import subprocess

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

def show_file_list(container):
    items = os.listdir(st.session_state.current_path)
    for item in items:
        item_path = os.path.join(st.session_state.current_path, item)
        if os.path.isdir(item_path):
            if container.button(f"📁 {item}", key=f"dir_{item}"):
                st.session_state.navigation_history.append(st.session_state.current_path)
                st.session_state.current_path = item_path
                st.session_state.viewing_file = None
                st.experimental_rerun()
        else:
            if container.button(f"📄 {item}", key=f"file_{item}"):
                st.session_state.viewing_file = item_path
                st.experimental_rerun()

def execute_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def main():
    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.getcwd()
    if 'viewing_file' not in st.session_state:
        st.session_state.viewing_file = None
    if 'navigation_history' not in st.session_state:
        st.session_state.navigation_history = []
    if 'shell_history' not in st.session_state:
        st.session_state.shell_history = []

    # Hiển thị tiêu đề động
    if st.session_state.viewing_file:
        st.title(os.path.basename(st.session_state.viewing_file))
    else:
        st.title(st.session_state.current_path)

    # Chức năng luôn ở sidebar
    with st.sidebar:
        st.title("Chức năng")
        
        # Tạo tabs trong sidebar
        tab1, tab2 = st.tabs(["File Manager", "Shell"])
        
        with tab1:
            # Mở thư mục
            new_path = st.text_input("Đường dẫn thư mục:", st.session_state.current_path)
            if new_path != st.session_state.current_path:
                if os.path.exists(new_path) and os.path.isdir(new_path):
                    st.session_state.current_path = new_path
                    st.session_state.navigation_history.append(new_path)
                    st.session_state.viewing_file = None
                    st.experimental_rerun()
                else:
                    st.error("Đường dẫn không hợp lệ!")

            # Upload file
            with st.expander("Upload file"):
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
            with st.expander("Tạo mới"):
                new_item = st.text_input("Tên thư mục/tệp mới:")
                create_type = st.radio("Loại:", ("Thư mục", "Tệp"))
                if st.button("Tạo"):
                    new_path = os.path.join(st.session_state.current_path, new_item)
                    if create_type == "Thư mục":
                        os.makedirs(new_path, exist_ok=True)
                    else:
                        open(new_path, 'a').close()
                    st.experimental_rerun()

            # Xóa thư mục/tệp
            with st.expander("Xóa"):
                delete_item = st.selectbox("Chọn mục để xóa:", os.listdir(st.session_state.current_path))
                if st.button("Xóa"):
                    delete_path = os.path.join(st.session_state.current_path, delete_item)
                    if os.path.isdir(delete_path):
                        shutil.rmtree(delete_path)
                    else:
                        os.remove(delete_path)
                    st.experimental_rerun()

            # Di chuyển tệp/thư mục
            with st.expander("Di chuyển"):
                move_item = st.selectbox("Chọn mục để di chuyển:", os.listdir(st.session_state.current_path))
                move_to = st.text_input("Di chuyển đến:")
                if st.button("Di chuyển"):
                    source = os.path.join(st.session_state.current_path, move_item)
                    destination = os.path.join(move_to, move_item)
                    shutil.move(source, destination)
                    st.experimental_rerun()

        with tab2:
            st.subheader("Shell")

            # Hiển thị lịch sử shell
            st.markdown("### Lịch sử Shell")
            history_container = st.container()
            with history_container:
                for cmd, out in st.session_state.shell_history[-10:]:  # Hiển thị 10 lệnh gần nhất
                    st.markdown(f"**$ {cmd}**")
                    st.code(out)

            # Nhập lệnh shell
            shell_command = st.text_input("Nhập lệnh shell:")
            if st.button("Thực thi"):
                output = execute_shell_command(shell_command)
                st.session_state.shell_history.append((shell_command, output))
                
                # Lưu lịch sử vào file
                with open("shell_history.txt", "a") as f:
                    f.write(f"Command: {shell_command}\n")
                    f.write(f"Output: {output}\n\n")
                
                # Cập nhật hiển thị lịch sử
                with history_container:
                    for cmd, out in st.session_state.shell_history[-10:]:
                        st.markdown(f"**$ {cmd}**")
                        st.code(out)

    # Hiển thị nội dung file hoặc màn hình chính
    if st.session_state.viewing_file:
        st.sidebar.title("Files and Folders")
        st.sidebar.write(f"Nội dung của: {st.session_state.current_path}")
        
        # Nút quay lại thư mục cha trong sidebar
        if st.sidebar.button("📁 ..", key="back_button_sidebar"):
            st.session_state.current_path = os.path.dirname(st.session_state.current_path)
            st.session_state.viewing_file = None
            st.experimental_rerun()
        
        # Hiển thị danh sách file và thư mục trong sidebar
        show_file_list(st.sidebar)
        
        # Hiển thị nội dung file trong main area
        file_info = get_file_info(st.session_state.viewing_file)
        st.code(f"{file_info}", language="json")
        display_file(st.session_state.viewing_file)
        if st.button("Trở lại"):
            st.session_state.viewing_file = None
            st.experimental_rerun()
    else:
        # Hiển thị danh sách file và thư mục trong main area
        # Nút quay lại thư mục cha trong main area
        if st.button("📁 .."):
            if st.session_state.navigation_history:
                st.session_state.current_path = st.session_state.navigation_history.pop()
                st.experimental_rerun()
        
        show_file_list(st)

if __name__ == "__main__":
    main()
