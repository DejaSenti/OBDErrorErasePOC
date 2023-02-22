import mmap
import pathlib
import tkinter as tk
import tkinter.ttk as ttk

from pygubu.widgets.scrolledframe import ScrolledFrame

import ECUManager
import FileHelper
import Processor
import config
from ECUType import ECUType
from Map import Map

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "ecugui.ui"


class EcuguiApp:

    def __init__(self, master=None):
        config.loaded_ecu = None
        config.app_path = FileHelper.get_app_path()

        # get values to populate gui
        self.ecu_by_brands = dict()
        self.keys = list()
        self.populate_brands()

        # build ui
        self.rows = []
        self.maps = []
        self.map_buttons = []
        self.eraser_filepath = ""
        self.adder_filepath = ""

        self.main = ttk.Notebook(master)
        self.eraser_frame = ttk.Frame(self.main)

        self.eraser_file_button = ttk.Button(self.eraser_frame)
        self.eraser_file_button.configure(text='Click to browse...',
                                          width=0)
        self.eraser_file_button.place(anchor='ne',
                                      bordermode='ignore',
                                      relheight='0.21',
                                      relwidth='1.0',
                                      relx='1.0',
                                      rely='0.0',
                                      x='0',
                                      y='0')
        self.eraser_file_button.configure(command=self.browse_eraser)

        self.eraser_ecu_select_frame = ttk.Frame(self.eraser_frame)

        self.eraser_label_brand = ttk.Label(self.eraser_ecu_select_frame)
        self.eraser_label_brand.configure(text='Brand:')
        self.eraser_label_brand.pack(padx='5',
                                     side='left')

        self.eraser_select_brand = ttk.Combobox(self.eraser_ecu_select_frame)
        self.eraser_select_brand.bind("<<ComboboxSelected>>", self.on_brand_selected)
        self.eraser_select_brand.configure(state='readonly',
                                           validate='none',
                                           values=self.keys)
        self.eraser_select_brand.current(0)
        self.eraser_select_brand.pack(side='left')

        self.eraser_file_label = ttk.Label(self.eraser_frame)
        self.eraser_file_label.configure(anchor='w',
                                         text='Currently editing: ',
                                         padding=5)
        self.eraser_file_label.place(anchor='center',
                                     relwidth='1.0',
                                     relx='0.5',
                                     rely='0.235',
                                     x='0',
                                     y='0')

        self.eraser_label_ecu = ttk.Label(self.eraser_ecu_select_frame)
        self.eraser_label_ecu.configure(text='Name:',
                                        width=0)
        self.eraser_label_ecu.pack(padx='5',
                                   side='left')

        self.eraser_select_ecu = ttk.Combobox(self.eraser_ecu_select_frame,
                                              values=self.ecu_by_brands[self.eraser_select_brand.get()])
        self.eraser_select_ecu.bind("<<ComboboxSelected>>", self.on_ecu_selected)
        self.eraser_select_ecu.current(0)
        self.eraser_select_ecu.configure(state='readonly')
        self.eraser_select_ecu.pack(side='left')

        self.eraser_ecu_select_frame.configure(height='200',
                                               relief='sunken',
                                               width='200')
        self.eraser_ecu_select_frame.place(anchor='center',
                                           relheight='0.1',
                                           relwidth='0.86',
                                           relx='0.5',
                                           rely='0.32',
                                           x='0',
                                           y='0')

        self.eraser_error_list_text = tk.Text(self.eraser_frame)
        self.eraser_error_list_text.configure(height='10',
                                              undo=True,
                                              width=50,
                                              wrap='word')
        self.eraser_error_list_text.place(anchor='center',
                                          bordermode='outside',
                                          relheight='0.1',
                                          relwidth='0.83',
                                          relx='0.5',
                                          rely='0.46',
                                          x='0',
                                          y='0')

        self.eraser_error_list_label = ttk.Label(self.eraser_frame)
        self.eraser_error_list_label.configure(text='Type in numbers of errors to erase, '
                                                    'separated by a comma (e.g. 0016, 0339, etc.):')
        self.eraser_error_list_label.place(anchor='center',
                                           relx='0.5',
                                           rely='0.39',
                                           x='0',
                                           y='0')

        self.eraser_maps_scrollbox = ScrolledFrame(self.eraser_frame,
                                                   scrolltype='vertical')

        self.eraser_maps_label = ttk.Label(self.eraser_maps_scrollbox.innerframe)
        self.eraser_maps_label.configure(text='Maps to modify:')
        self.eraser_maps_label.pack(pady='5',
                                    side='top')

        self.eraser_maps_scrollbox.innerframe.configure(relief='groove')
        self.eraser_maps_scrollbox.configure(usemousewheel=True)
        self.eraser_maps_scrollbox.place(anchor='center',
                                         relheight='0.25',
                                         relwidth='0.21',
                                         relx='0.19',
                                         rely='0.65',
                                         x='0',
                                         y='0')

        self.eraser_selectall = tk.Variable()

        self.eraser_selectall_check = ttk.Checkbutton(self.eraser_frame)
        self.eraser_selectall_check.configure(compound='left',
                                              text='Select All',
                                              width=10,
                                              command=self.select_all_maps,
                                              onvalue=True,
                                              offvalue=False,
                                              variable=self.eraser_selectall)
        self.eraser_selectall_check.place(anchor='e',
                                          relx='0.27',
                                          rely='0.8',
                                          x='0',
                                          y='0')

        self.eraser_process_button = ttk.Button(self.eraser_frame)
        self.eraser_process_button.configure(text='Process and Save!')
        self.eraser_process_button.place(anchor='s',
                                         relheight='0.12',
                                         relwidth='0.22',
                                         relx='0.5',
                                         rely='0.97',
                                         x='0',
                                         y='0')
        self.eraser_process_button.configure(command=self.process)

        self.eraser_frame.configure(height='200',
                                    width='200')
        self.eraser_frame.pack(side='top')

        self.main.add(self.eraser_frame, text='Error Eraser')

        self.adder_frame = ttk.Frame(self.main)

        self.adder_file_button = ttk.Button(self.adder_frame)
        self.adder_file_button.configure(text='Click to browse...',
                                         width=0)
        self.adder_file_button.place(anchor='ne',
                                     bordermode='ignore',
                                     relheight='0.21',
                                     relwidth='1.0',
                                     relx='1.0',
                                     rely='0.0',
                                     x='0',
                                     y='0')
        self.adder_file_button.configure(command=self.browse_adder)

        self.adder_file_label = ttk.Label(self.adder_frame)
        self.adder_file_label.configure(anchor='w',
                                        text='Source file: ',
                                        padding=5)
        self.adder_file_label.place(anchor='center',
                                    relwidth='1.0',
                                    relx='0.5',
                                    rely='0.235',
                                    x='0',
                                    y='0')

        self.adder_create_button = ttk.Button(self.adder_frame)
        self.adder_create_button.configure(text='Create')
        self.adder_create_button.place(anchor='s',
                                       relheight='0.1',
                                       relwidth='0.4',
                                       relx='0.5',
                                       rely='0.96',
                                       x='0',
                                       y='0')
        self.adder_create_button.configure(command=self.create_ecu)

        self.adder_ecu_frame = ttk.Frame(self.adder_frame)

        self.adder_label_brand = ttk.Label(self.adder_ecu_frame)
        self.adder_label_brand.configure(text='Brand:')
        self.adder_label_brand.pack(padx='5',
                                    side='left')

        self.adder_select_brand = ttk.Combobox(self.adder_ecu_frame)
        self.adder_select_brand.configure(state='readonly',
                                          validate='none',
                                          values=self.keys)
        self.adder_select_brand.current(0)
        self.adder_select_brand.pack(side='left')

        self.adder_text_brand = ttk.Entry(self.adder_ecu_frame)
        self.adder_text_brand.pack(padx='3',
                                   side='left')

        self.adder_label_ecu = ttk.Label(self.adder_ecu_frame)
        self.adder_label_ecu.configure(text='Name:',
                                       width=0)
        self.adder_label_ecu.pack(padx='5',
                                  side='left')

        self.adder_text_ecu = ttk.Entry(self.adder_ecu_frame)
        self.adder_text_ecu.configure(width=10)
        self.adder_text_ecu.pack(side='left')

        self.adder_ecu_frame.configure(height='200',
                                       relief='sunken',
                                       width='200')
        self.adder_ecu_frame.place(anchor='center',
                                   relheight='0.1',
                                   relwidth='0.86',
                                   relx='0.5',
                                   rely='0.32',
                                   x='0',
                                   y='0')

        self.adder_maps_scrollbox = ScrolledFrame(self.adder_frame, scrolltype='vertical')

        self.adder_maps_titles_frame = ttk.Frame(self.adder_maps_scrollbox.innerframe)

        self.adder_maps_name_label = ttk.Label(self.adder_maps_titles_frame)
        self.adder_maps_name_label.configure(anchor='center',
                                             font='TkDefaultFont',
                                             text='Map',
                                             width=10)
        self.adder_maps_name_label.grid(column=0,
                                        ipadx='5',
                                        padx='5',
                                        row=0)

        self.adder_maps_titles_frame.rowconfigure('0',
                                                  minsize='30',
                                                  pad='5')
        self.adder_maps_titles_frame.columnconfigure('0',
                                                     minsize='10',
                                                     pad='5')

        self.adder_maps_location_label = ttk.Label(self.adder_maps_titles_frame)
        self.adder_maps_location_label.configure(anchor='center',
                                                 text='Location (HEX)')
        self.adder_maps_location_label.grid(column=1,
                                            padx=1,
                                            row=0)

        self.adder_maps_titles_frame.columnconfigure('1', minsize='10', pad='5')

        self.adder_maps_value_size_label = ttk.Label(self.adder_maps_titles_frame)
        self.adder_maps_value_size_label.configure(anchor='center',
                                                   text='Value Size (bits)')
        self.adder_maps_value_size_label.grid(column=2,
                                              padx='1',
                                              row=0)

        self.adder_maps_titles_frame.columnconfigure('2', minsize='10', pad='5')

        self.adder_maps_new_value_label = ttk.Label(self.adder_maps_titles_frame)
        self.adder_maps_new_value_label.configure(anchor='center',
                                                  text='New Value (HEX)')
        self.adder_maps_new_value_label.grid(column=3,
                                             padx='1',
                                             row=0)

        self.adder_maps_titles_frame.columnconfigure('3', minsize='10', pad='5')
        self.adder_maps_titles_frame.configure(height='10',
                                               width='200')
        self.adder_maps_titles_frame.pack(anchor='n',
                                          fill='x',
                                          padx='5',
                                          pady='3',
                                          side='top')

        self.adder_maps_dtc_frame = ttk.Frame(self.adder_maps_scrollbox.innerframe)

        self.adder_maps_dtc_label = ttk.Label(self.adder_maps_dtc_frame)
        self.adder_maps_dtc_label.configure(anchor='center',
                                            text='DTC',
                                            width=10)
        self.adder_maps_dtc_label.grid(column=0,
                                       ipadx='5',
                                       padx='5',
                                       row=0)

        self.adder_maps_dtc_frame.rowconfigure('0', minsize='15')
        self.adder_maps_dtc_frame.columnconfigure('0', minsize='10', pad='5')

        self.adder_maps_dtc_location_text = ttk.Entry(self.adder_maps_dtc_frame)
        dtc_l_vcmd = self.adder_maps_dtc_location_text.register(EcuguiApp.is_hex)
        self.adder_maps_dtc_location_text.configure(justify='left',
                                                    width=10,
                                                    validate='key',
                                                    validatecommand=(dtc_l_vcmd, '%P'))
        self.adder_maps_dtc_location_text.grid(column=1,
                                               ipadx='5',
                                               padx='5',
                                               row=0)

        self.adder_maps_dtc_frame.columnconfigure('1', minsize='10', pad='5')

        self.adder_maps_dtc_value_size_text = ttk.Entry(self.adder_maps_dtc_frame)
        dtc_vs_vcmd = self.adder_maps_dtc_value_size_text.register(EcuguiApp.is_num)
        self.adder_maps_dtc_value_size_text.configure(width=10,
                                                      validate='key',
                                                      validatecommand=(dtc_vs_vcmd, '%P'))
        self.adder_maps_dtc_value_size_text.grid(column=2,
                                                 ipadx='5',
                                                 padx='5',
                                                 row=0)

        self.adder_maps_dtc_frame.columnconfigure('2', minsize='10', pad='5')

        self.adder_maps_dtc_new_value_text = ttk.Entry(self.adder_maps_dtc_frame)
        dtc_nv_vcmd = self.adder_maps_dtc_new_value_text.register(EcuguiApp.is_hex)
        self.adder_maps_dtc_new_value_text.configure(font='TkDefaultFont',
                                                     width=10,
                                                     validate='key',
                                                     validatecommand=(dtc_nv_vcmd, '%P'))
        self.adder_maps_dtc_new_value_text.grid(column=3,
                                                ipadx='5',
                                                padx='5',
                                                row=0)

        self.adder_maps_dtc_frame.columnconfigure('3', minsize='10', pad='5')
        self.adder_maps_dtc_frame.configure(height='10',
                                            width='200')
        self.adder_maps_dtc_frame.pack(anchor='n',
                                       fill='x',
                                       padx='5',
                                       pady='3',
                                       side='top')

        self.create_map_row()

        self.adder_maps_scrollbox.innerframe.configure(relief='groove')
        self.adder_maps_scrollbox.configure(usemousewheel=False)
        self.adder_maps_scrollbox.place(anchor='center',
                                        relheight='0.38',
                                        relwidth='0.8',
                                        relx='0.45',
                                        rely='0.58',
                                        x='0', y='0')

        self.adder_maps_add_map_button = ttk.Button(self.adder_frame)
        self.adder_maps_add_map_button.configure(text='Add Map')
        self.adder_maps_add_map_button.place(anchor='e',
                                             height='50',
                                             relwidth='0.12',
                                             relx='0.99',
                                             rely='0.5',
                                             x='0',
                                             y='0')
        self.adder_maps_add_map_button.configure(command=self.add_map)

        self.adder_maps_clear_button = ttk.Button(self.adder_frame)
        self.adder_maps_clear_button.configure(text='Clear All')
        self.adder_maps_clear_button.place(anchor='e',
                                           height='50',
                                           relwidth='0.12',
                                           relx='0.99',
                                           rely='0.64',
                                           x='0',
                                           y='0')
        self.adder_maps_clear_button.configure(command=self.clear_maps)

        self.adder_label_map_size = ttk.Label(self.adder_frame)
        self.adder_label_map_size.configure(text='Map Size (# of values):')
        self.adder_label_map_size.place(anchor='sw',
                                        relx='0.19',
                                        rely='0.81',
                                        x='0',
                                        y='0')
        self.adder_text_map_size = ttk.Entry(self.adder_frame)

        ms_vcmd = self.adder_text_map_size.register(EcuguiApp.is_num)
        self.adder_text_map_size.configure(width=10,
                                           validate='key',
                                           validatecommand=(ms_vcmd, '%P'))
        self.adder_text_map_size.place(anchor='sw',
                                       relx='0.44',
                                       rely='0.81',
                                       x='0',
                                       y='0')

        self.adder_flip_bytes_check = ttk.Checkbutton(self.adder_frame)

        self.flip_bytes = tk.BooleanVar()
        self.adder_flip_bytes_check.configure(compound='left',
                                              text='Flip bytes',
                                              width=10,
                                              variable=self.flip_bytes,
                                              onvalue=True,
                                              offvalue=False)
        self.flip_bytes.set(True)
        self.adder_flip_bytes_check.place(anchor='sw',
                                          relx='0.62',
                                          rely='0.81',
                                          x='0',
                                          y='0')

        self.adder_frame.configure(height='200',
                                   width='200')
        self.adder_frame.pack(side='top')

        self.main.add(self.adder_frame, text='ECU Adder')
        self.main.configure(height=600,
                            width=550)
        self.main.pack(side='top')

        self.main.bind('<<NotebookTabChanged>>', self.on_tab_switched)

        # Main widget
        self.mainwindow = self.main

    def run(self):
        self.mainwindow.mainloop()

    def browse_eraser(self):
        self.eraser_filepath = FileHelper.browse_bin_file()
        display_str = self.eraser_filepath.split('/')[-1]
        self.eraser_file_label.configure(text="Currently editing: " + display_str)

    def process(self):
        Processor.process_and_save(self.get_error_numbers(), self.eraser_filepath)

    def browse_adder(self):
        self.adder_filepath = FileHelper.browse_bin_file()
        display_str = self.adder_filepath.split('/')[-1]
        self.adder_file_label.configure(text="Source file: " + display_str)

    def create_ecu(self):
        if len(self.adder_filepath) == 0:
            print("Error! No binary file selected for ECU creation!")
            return

        if self.adder_select_brand.current() > 0:
            brand = self.adder_select_brand.get()
        else:
            brand = self.adder_text_brand.get()
            if len(brand) == 0:
                print("Bad brand selection. Aborting.")
                return

        ecu = self.adder_text_ecu.get()
        if len(ecu) == 0:
            print("Bad ECU name input. Aborting.")
            return

        adder_text_boxes = [self.adder_text_ecu,
                            self.adder_maps_dtc_location_text,
                            self.adder_maps_dtc_value_size_text,
                            self.adder_maps_dtc_new_value_text,
                            self.adder_text_brand,
                            self.adder_text_map_size]

        for text_box in adder_text_boxes:
            if text_box['state'] == tk.NORMAL and len(text_box.get()) == 0:
                print("Not all boxes filled. Aborting.")
                return

        locations = [map_row.location for map_row in self.rows]
        value_sizes = [map_row.value_size for map_row in self.rows]
        new_values = [map_row.new_value for map_row in self.rows]

        adder_text_boxes += locations + value_sizes + new_values
        file = open(self.adder_filepath, 'r+b')
        mapped_file = mmap.mmap(file.fileno(), 0)
        dtc = Map('DTC',
                  self.adder_text_map_size.get(),
                  self.adder_maps_dtc_location_text.get(),
                  self.adder_maps_dtc_value_size_text.get(),
                  self.adder_maps_dtc_new_value_text.get(),
                  mapped_file)
        maps = [dtc] + [Map(row.name.get(),
                        self.adder_text_map_size.get(),
                        row.location.get(),
                        row.value_size.get(),
                        row.new_value.get(),
                        mapped_file) for row in self.rows]
        ECUManager.create_ecu_type(brand, ecu, maps, self.flip_bytes.get())

        self.update_selection_menus()

    def add_map(self):
        self.create_map_row()

    def clear_maps(self):
        for map_row in self.rows:
            map_row.destroy_map()
        self.rows.clear()

    def create_map_row(self):
        frame = ttk.Frame(self.adder_maps_scrollbox.innerframe)
        location = ttk.Entry(frame)
        value_size = ttk.Entry(frame)
        new_value = ttk.Entry(frame)
        remove_button = ttk.Button(frame)
        name = ttk.Entry(frame)

        row = MapRow(self, frame, location, value_size, new_value, remove_button, name)
        self.rows.append(row)

        self.adder_maps_scrollbox.reposition()

    def on_brand_selected(self, event=None):
        brand = self.eraser_select_brand.get()
        self.eraser_select_ecu.configure(values=self.ecu_by_brands[brand])
        self.eraser_select_ecu.current(0)

    def on_ecu_selected(self, event=None):
        if len(self.maps) > 0:
            self.map_buttons.clear()
            for button in self.maps:
                button.destroy()

        brand = self.eraser_select_brand.get()
        ecu = self.eraser_select_ecu.get()
        config.loaded_ecu = ECUManager.get_ecu_type(brand, ecu)
        for map_ in config.loaded_ecu.maps.values():
            map_.edit_on_command = tk.Variable()
            button = ttk.Checkbutton(self.eraser_maps_scrollbox.innerframe)
            button.configure(compound='left',
                             text=map_.name,
                             width=10,
                             variable=map_.edit_on_command,
                             onvalue=True,
                             offvalue=False)
            button.pack(side='top')
            map_.edit_on_command.set(True)
            self.maps.append(button)
            self.map_buttons.append(map_.edit_on_command)
        self.eraser_maps_scrollbox.reposition()

    def select_all_maps(self):
        new_value = self.eraser_selectall.get()
        for map_ in self.map_buttons:
            map_.set(new_value)

    def get_error_numbers(self) -> [str]:
        text = self.eraser_error_list_text.get("1.0", "end-1c")
        split = text.split(",")
        errors = list()
        for error in split:
            filtered = filter(str.isalnum, error)
            error = "".join(filtered)
            if self.is_hex(error) and len(error) == config.loaded_ecu.maps[config.DTC].value_size:
                errors.append(error)

        return errors

    def on_tab_switched(self, event=None):
        self.update_selection_menus()

    def populate_brands(self):
        self.ecu_by_brands = FileHelper.get_brand_names()
        self.keys = list(self.ecu_by_brands.keys())

    def update_selection_menus(self):
        self.populate_brands()
        self.adder_select_brand.configure(values=self.keys)
        self.eraser_select_brand.configure(values=self.keys)

    @staticmethod
    def load_new_ecu(new_ecu: ECUType):
        config.loaded_ecu = new_ecu

    @staticmethod
    def is_hex(text):
        import string
        return all(c in string.hexdigits for c in text) or len(text) == 0

    @staticmethod
    def is_num(text):
        return text.isnumeric() or len(text) == 0


class MapRow:
    def __init__(self, parent: EcuguiApp,
                 frame: ttk.Frame,
                 location: ttk.Entry,
                 value_size: ttk.Entry,
                 new_value: ttk.Entry,
                 remove_button: ttk.Button,
                 name: ttk.Entry):
        self.frame = frame
        self.parent = parent

        self.location = location
        self.value_size = value_size
        self.new_value = new_value
        self.name = name

        l_vcmd = location.register(EcuguiApp.is_hex)
        nv_vcmd = new_value.register(EcuguiApp.is_hex)
        vs_vcmd = value_size.register(EcuguiApp.is_num)

        location.configure(justify='left',
                           width=10,
                           validate='key',
                           validatecommand=(l_vcmd, '%P'))
        location.grid(column=1, ipadx=5, padx=4, row=0)

        frame.rowconfigure('0', minsize='15')
        frame.columnconfigure('0', minsize='10', pad='5')

        value_size.configure(width=10,
                             validate='key',
                             validatecommand=(vs_vcmd, '%P'))
        value_size.grid(column=2, ipadx=5, padx=5, row=0)
        frame.columnconfigure(1, minsize='10', pad='5')

        new_value.configure(width=10,
                            validate='key',
                            validatecommand=(nv_vcmd, '%P'))
        new_value.grid(column=3, ipadx='5', padx='5', row=0)
        frame.columnconfigure('2', minsize='10', pad='5')

        remove_button.configure(text='x', width=2)
        remove_button.grid(column=4, padx='5', row=0)
        remove_button.configure(command=self.remove_map)

        name.configure(justify='left', width=10)
        name.grid(column=0, ipadx='5', padx='5', row=0)

        frame.columnconfigure('3', minsize='10', pad='5')
        frame.configure(height='10', width='200')
        frame.pack(anchor='n',
                   fill='x',
                   padx='5',
                   pady='1',
                   side='top')

    def remove_map(self):
        self.parent.rows.remove(self)
        self.destroy_map()

    def destroy_map(self):
        self.frame.destroy()
        self.parent.adder_maps_scrollbox.reposition()


if __name__ == '__main__':
    root = tk.Tk()
    app = EcuguiApp(root)
    app.run()
