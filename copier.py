__author__ = "Juno Park"
__github__ = "https://github.com/junopark00/multi-copier"


import os
import shutil

from PySide2 import QtWidgets, QtCore, QtGui

from copier_ui import CopierUI


class CopyFilesThread(QtCore.QThread):
    """
    This Thread copies the files or directories to the destination paths using shutil.
    """
    copy_finished = QtCore.Signal()
    entire_progress = QtCore.Signal(int)
    progress = QtCore.Signal(int)
    progressing_file = QtCore.Signal(str)
    destination = QtCore.Signal(str)
    
    def __init__(self, origin_list, dst_paths, parent=None):
        super().__init__(parent)
        self.origin_list = origin_list
        self.dst_paths = dst_paths
        self.is_interrupted = False
        self.total_files = 0
        self.copied_files = 0

    def run(self):
        self.total_files = self.count_files(self.origin_list)
        
        for index, dst_path in enumerate(self.dst_paths):
            entire_progress_value = int((index / len(self.dst_paths)) * 100)
            self.entire_progress.emit(entire_progress_value)
            self.copied_files = 0
            self.destination.emit(os.path.basename(dst_path))
            for origin in self.origin_list:
                if self.is_interrupted:
                    break
                try:
                    self.copy_files(origin, dst_path)
                except PermissionError as e:
                    QtWidgets.QMessageBox.critical(
                        None, "Permission Error", f"An error occurred while copying the files to {dst_path}."
                        )
        
        if not self.is_interrupted:
            self.copy_finished.emit()
        
    def count_files(self, paths):
        count = 0
        for path in paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    count += len(files)
            else:
                count += 1
        return count
        
    def copy_files(self, origin, dst_path):
        if os.path.isdir(origin):
            self.copy_dir(origin, dst_path)
        else:
            self.copy_file(origin, dst_path)
            
    def copy_dir(self, origin, dst_path):
        destination = os.path.join(dst_path, os.path.basename(origin))
        if not os.path.exists(destination):
            os.makedirs(destination)
        for root, _, files in os.walk(origin):
            if self.is_interrupted:
                break
            files = sorted(files)
            for file in files:
                if self.is_interrupted:
                    break
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, origin)
                destination_dir = os.path.join(destination, relative_path)
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)
                self.copy_file(source_file, destination_dir)
                if self.is_interrupted:
                    break
        
    def copy_file(self, origin, dst_path):
        if self.is_interrupted:
            return
        shutil.copy2(origin, dst_path)
        self.copied_files += 1
        progress_value = int((self.copied_files / self.total_files) * 100)
        self.progress.emit(progress_value)
        self.progressing_file.emit(os.path.basename(origin))
        
    def stop(self):
        self.is_interrupted = True
        self.quit()
        self.wait(10000)
        

class MultiCopier(CopierUI):
    def __init__(self):
        super().__init__()
        self.copy_thread = CopyFilesThread([], [])
        self.connections()
        
    def connections(self) -> None:
        """
        Connects the signals to slots.
        """
        self.button_copy.clicked.connect(self.start_copy)
        self.button_stop.clicked.connect(self.stop_copy)
        
    def start_copy(self) -> None:
        """
        Starts copying the files.
        """
        origin_list = []
        dst_paths = []
        
        for index in range(self.list_widget_origin.count()):
            item = self.list_widget_origin.item(index)
            widget = self.list_widget_origin.itemWidget(item)
            file_path = widget.file_path
            if file_path is None:
                QtWidgets.QMessageBox.warning(self, "Warning", "There are no files to copy.")
            origin_list.append(file_path)
            
        for index in range(self.list_widget_destination.count()):
            item = self.list_widget_destination.item(index)
            widget = self.list_widget_destination.itemWidget(item)
            file_path = widget.file_path
            dst_paths.append(file_path)
         
        if not len(origin_list):
            QtWidgets.QMessageBox.warning(self, "Warning", "There are no files to copy.")
            return
            
        if not len(dst_paths):
            QtWidgets.QMessageBox.warning(self, "Warning", "There is no destination path.") 
            return
           
        self.copy_thread = CopyFilesThread(origin_list, dst_paths)
        self.copy_thread.entire_progress.connect(self.update_entire_progress)
        self.copy_thread.progress.connect(self.update_progress)
        self.copy_thread.progressing_file.connect(self.line_edit_file.setText)
        self.copy_thread.destination.connect(self.line_edit_dst.setText)
        self.copy_thread.copy_finished.connect(self.finish_copy)
        self.copy_thread.start()
        
    def update_entire_progress(self, value) -> None:
        """
        Updates the entire progress bar.
        
        Args:
            value (int): The value to update the entire progress bar.
        """
        self.progress_bar_all.setValue(value)
        
    def update_progress(self, value) -> None:
        """
        Updates the progress bar.
        
        Args:
            value (int): The value to update the progress bar.
        """
        self.progress_bar.setValue(value)
        
    def update_label(self, file_name) -> None:
        """
        Updates the label with the current file name.
        
        Args:
            file_name (str): The name of the file to update the label.
        """
        self.label_file.setText(f"Coping: {file_name}")
        
    def finish_copy(self) -> None:
        """
        Finishes the copying process.
        """
        self.progress_bar_all.setValue(100)
        self.progress_bar.setValue(100)
        
        if self.action_email.isChecked():
            # self.send_email()
            pass
        
        if self.action_rocketchat.isChecked():
            self.send_rocketchat() 
        
        QtWidgets.QMessageBox.information(self, "Complete", "Copying has been completed.")
        
        self.progress_bar_all.setValue(0)
        self.progress_bar.setValue(0)
        self.line_edit_dst.clear()
        self.line_edit_file.clear()
        
    def stop_copy(self) -> None:
        """
        Stops the copying process.
        """
        self.copy_thread.stop()
        QtWidgets.QMessageBox.information(self, "Stopped", "Copying has been stopped.")
        
    def closeEvent(self, event) -> None:
        """
        Overrides the closeEvent method.
        
        Args:
            event (QCloseEvent): The close event.
        """
        self.copy_thread.stop()
        event.accept()
        
    def send_email(self) -> None:
        """
        Sends an email.
        """
        import smtplib
        from email.mime.text import MIMEText
        
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        
        smtp.login("email", "password")
        
        msg = MIMEText("The copying process has been completed.")
        msg["Subject"] = "Completed copying"
        
        smtp.sendmail("send email", "recieve email", msg.as_string())
        
        smtp.quit()
        
    def send_rocketchat(self) -> None:
        """
        Sends a message to RocketChat.
        """
        print("Sending a message to RocketChat...")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MultiCopier()
    window.show()
    app.exec_()