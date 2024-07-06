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
            # Các chức năng quản lý tệp (giữ nguyên như cũ)
            # ...

        with tab2:
            st.subheader("Shell")

            # Hiển thị lịch sử shell trong một khung có kích thước cố định
            history_display = st.empty()
            with history_display.container():
                st.markdown("### Lịch sử Shell")
                history_area = st.empty()
                
                # Hiển thị lịch sử shell
                history_text = ""
                for cmd, out in st.session_state.shell_history[-10:]:  # Hiển thị 10 lệnh gần nhất
                    history_text += f"$ {cmd}\n{out}\n\n"
                history_area.code(history_text)

            # Nhập lệnh shell
            shell_command = st.text_input("Nhập lệnh shell:", key="shell_input")
            if shell_command:
                output = execute_shell_command(shell_command)
                st.session_state.shell_history.append((shell_command, output))
                
                # Lưu lịch sử vào file
                with open("shell_history.txt", "a") as f:
                    f.write(f"Command: {shell_command}\n")
                    f.write(f"Output: {output}\n\n")
                
                # Xóa nội dung của ô nhập lệnh
                st.session_state.shell_input = ""
                
                # Cập nhật hiển thị lịch sử
                history_text = ""
                for cmd, out in st.session_state.shell_history[-10:]:
                    history_text += f"$ {cmd}\n{out}\n\n"
                history_area.code(history_text)

    # Hiển thị nội dung file hoặc màn hình chính (giữ nguyên như cũ)
    # ...

if __name__ == "__main__":
    main()
