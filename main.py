

import sys
import os
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFileDialog, QCheckBox,
    QDateEdit, QMessageBox, QComboBox, QMenu, QProgressBar
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QCursor, QClipboard

class FileSearchWorker(QObject):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, directory, query, size_min_bytes, size_max_bytes, extensions,
                 before_checked, after_checked, date_before, date_after):
        super().__init__()
        self.directory = directory
        self.query = query
        self.size_min_bytes = size_min_bytes
        self.size_max_bytes = size_max_bytes
        self.extensions = extensions
        self.before_checked = before_checked
        self.after_checked = after_checked
        self.date_before = date_before
        self.date_after = date_after
        self.is_running = True

    def run(self):
        total_files = 0
        for root, dirs, files in os.walk(self.directory):
            total_files += len(files)

        processed_files = 0
        for root, dirs, files in os.walk(self.directory):
            if not self.is_running:
                break
            for file in files:
                file_path = os.path.join(root, file)
                processed_files += 1
                progress_percent = int((processed_files / total_files) * 100)
                self.progress.emit(progress_percent)

                # Search Query Filter
                if self.query and self.query.lower() not in file.lower():
                    continue

                # File Extension Filter
                if self.extensions and not any(file.lower().endswith(f".{ext}") for ext in self.extensions):
                    continue

                # File Size Filter
                file_size = os.path.getsize(file_path)
                if self.size_min_bytes and file_size < self.size_min_bytes:
                    continue
                if self.size_max_bytes and file_size > self.size_max_bytes:
                    continue

                # Date Modified Filter
                file_mtime = datetime.date.fromtimestamp(os.path.getmtime(file_path))
                if self.before_checked and file_mtime >= self.date_before:
                    continue
                if self.after_checked and file_mtime <= self.date_after:
                    continue

                self.result.emit(file_path)
        self.finished.emit()

    def stop(self):
        self.is_running = False

class FileSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Advanced File Search App')
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.thread = None
        self.worker = None

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Directory Selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel('Directory:')
        self.dir_input = QLineEdit()
        dir_button = QPushButton('Browse')
        dir_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        main_layout.addLayout(dir_layout)

        # Search Query
        search_layout = QHBoxLayout()
        search_label = QLabel('Search:')
        self.search_input = QLineEdit()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # File Size Filter
        size_layout = QHBoxLayout()
        size_label = QLabel('Size (Min - Max):')
        self.size_min_input = QLineEdit()
        self.size_min_input.setPlaceholderText('Min Size')
        self.size_max_input = QLineEdit()
        self.size_max_input.setPlaceholderText('Max Size')
        self.size_unit_combo = QComboBox()
        self.size_unit_combo.addItems(['KB', 'MB', 'GB'])
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_min_input)
        size_layout.addWidget(self.size_max_input)
        size_layout.addWidget(self.size_unit_combo)
        main_layout.addLayout(size_layout)

        # File Format Filter
        format_layout = QHBoxLayout()
        format_label = QLabel('File Extension:')
        self.format_input = QLineEdit()
        self.format_input.setPlaceholderText('e.g., txt, pdf')
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_input)
        main_layout.addLayout(format_layout)

        # Date Modified Filter
        date_layout = QHBoxLayout()
        date_label = QLabel('Modified Date:')
        self.date_before_checkbox = QCheckBox('Before')
        self.date_before_input = QDateEdit()
        self.date_before_input.setCalendarPopup(True)
        self.date_before_input.setDate(QDate.currentDate())
        self.date_after_checkbox = QCheckBox('After')
        self.date_after_input = QDateEdit()
        self.date_after_input.setCalendarPopup(True)
        self.date_after_input.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_before_checkbox)
        date_layout.addWidget(self.date_before_input)
        date_layout.addWidget(self.date_after_checkbox)
        date_layout.addWidget(self.date_after_input)
        main_layout.addLayout(date_layout)

        # Search and Save Buttons
        button_layout = QHBoxLayout()
        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.start_search)
        self.save_button = QPushButton('Save Results')
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        button_layout.addStretch()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.save_button)
        main_layout.addLayout(button_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Results List
        self.results_list = QListWidget()
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.open_context_menu)
        main_layout.addWidget(self.results_list)

        self.setLayout(main_layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_input.setText(directory)

    def start_search(self):
        self.results_list.clear()
        self.save_button.setEnabled(False)
        directory = self.dir_input.text()
        query = self.search_input.text()
        size_min = self.size_min_input.text()
        size_max = self.size_max_input.text()
        size_unit = self.size_unit_combo.currentText()
        format_filter = self.format_input.text()
        before_checked = self.date_before_checkbox.isChecked()
        after_checked = self.date_after_checkbox.isChecked()
        date_before = self.date_before_input.date().toPyDate()
        date_after = self.date_after_input.date().toPyDate()

        if not directory:
            QMessageBox.warning(self, "Warning", "Please select a directory.")
            return

        try:
            size_min_bytes = self.convert_size_to_bytes(size_min, size_unit) if size_min else None
            size_max_bytes = self.convert_size_to_bytes(size_max, size_unit) if size_max else None
        except ValueError:
            QMessageBox.warning(self, "Warning", "Invalid size input.")
            return

        if format_filter:
            extensions = [ext.strip().lower() for ext in format_filter.split(',')]
        else:
            extensions = None

        self.search_button.setEnabled(False)
        self.worker = FileSearchWorker(
            directory, query, size_min_bytes, size_max_bytes, extensions,
            before_checked, after_checked, date_before, date_after
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.add_result)
        self.worker.finished.connect(self.search_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def add_result(self, file_path):
        self.results_list.addItem(file_path)

    def search_finished(self):
        self.search_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.progress_bar.setValue(100)
        self.thread.quit()
        self.worker = None
        self.thread = None

    def convert_size_to_bytes(self, size_str, unit):
        size = float(size_str)
        unit = unit.upper()
        if unit == 'KB':
            return size * 1024
        elif unit == 'MB':
            return size * 1024 * 1024
        elif unit == 'GB':
            return size * 1024 * 1024 * 1024
        else:
            raise ValueError('Invalid size unit.')

    def open_context_menu(self, position):
        indexes = self.results_list.selectedIndexes()
        if not indexes:
            return
        menu = QMenu()
        open_action = menu.addAction("Open File")
        copy_path_action = menu.addAction("Copy File Path")
        open_location_action = menu.addAction("Open File Location")
        action = menu.exec_(self.results_list.viewport().mapToGlobal(position))
        selected_item = self.results_list.currentItem()
        if action == open_action:
            self.open_file(selected_item.text())
        elif action == copy_path_action:
            self.copy_file_path(selected_item.text())
        elif action == open_location_action:
            self.open_file_location(selected_item.text())

    def open_file(self, file_path):
        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")

    def copy_file_path(self, file_path):
        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)
        QMessageBox.information(self, "Copied", "File path copied to clipboard.")

    def open_file_location(self, file_path):
        folder = os.path.dirname(file_path)
        try:
            os.startfile(folder)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {e}")

    def save_results(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt)")
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as file:
                    for index in range(self.results_list.count()):
                        file.write(self.results_list.item(index).text() + '\n')
                QMessageBox.information(self, "Success", "Results saved successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save results: {e}")

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = FileSearchApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
