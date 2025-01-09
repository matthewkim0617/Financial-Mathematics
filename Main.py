from tksheet import Sheet
import tkinter as tk
import pandas as pd
import numpy as np
import JumpMinVar as JMV


#######################Summary################################
# Following Class will display a table where the user can enter
# Instrument, Start Date, End Date, Market Quote, Jump date,
# Horizon date and MCIL. Automatically, the program will output
# Discount Factor and Zero Coupon Rate.

class RateCurveTable(tk.Tk):
    def __init__(self):
        '''
        # Description:
        # The Function is the brain of the program, which does the following:
        # - Display pop-up screen of the table where the user can input the information
        # - Automatically run Jump MinVar program and update the discount factor/zero-coupon rate
        # - Right clicking on the screen, the user can select additional features: Save, Interpolator, Re-computing

        '''


        tk.Tk.__init__(self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame = tk.Frame(self)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.sheet = Sheet(self.frame,
                           row_index_width=100,
                           data=[["" for c in range(8)] for r in range(40)],
                           theme="dark green",
                           height=700,  # height and width arguments are optional
                           width=1200  # For full startup arguments see DOCUMENTATION.md
                           )

        self.sheet.enable_bindings(("single_select",  # "single_select" or "toggle_select"
                                    "drag_select",  # enables shift click selection as well
                                    "column_drag_and_drop",
                                    "row_drag_and_drop",
                                    "column_select",
                                    "row_select",
                                    "column_width_resize",
                                    "double_click_column_resize",
                                    # "row_width_resize",
                                    # "column_height_resize",
                                    "arrowkeys",
                                    "row_height_resize",
                                    "double_click_row_resize",
                                    "right_click_popup_menu",
                                    "rc_select",
                                    "rc_insert_column",
                                    "rc_delete_column",
                                    "rc_insert_row",
                                    "rc_delete_row",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"))
        self.sheet.enable_bindings("enable_all")
        # self.sheet.disable_bindings() #uses the same strings
        # self.bind("<Configure>", self.window_resized)
        self.sheet.set_all_cell_sizes_to_text()

        self.sheet.popup_menu_add_command("Compute", self.JumpMinVarInt)
        self.sheet.popup_menu_add_command("Load Data", self.LoadDataFromExcel)
        self.sheet.popup_menu_add_command("Save", self.SaveData)
        self.frame.grid(row=0, column=0, sticky="nswe")
        self.sheet.grid(row=0, column=0, sticky="nswe")

        """_________________________ EXAMPLES _________________________ """
        """_____________________________________________________________"""

        # __________ CHANGING THEME __________

        # self.sheet.change_theme("dark")

        # __________ HIGHLIGHT / DEHIGHLIGHT CELLS __________
        '''
        self.sheet.highlight_cells(row=5, column=5, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=5, column=1, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=5, bg="#ed4337", fg="white", canvas="row_index")
        self.sheet.highlight_cells(column=0, bg="#ed4337", fg="white", canvas="header")
        '''

        # __________ SETTING ROW HEIGHTS AND COLUMN WIDTHS __________

        # self.sheet.set_cell_data(0, 0, "\n".join([f"Line {x}" for x in range(500)]))
        # self.sheet.set_column_data(1, ("" for i in range(2000)))
        # self.sheet.row_index((f"Row {r}" for r in range(2000))) #any iterable works
        # self.sheet.row_index("\n".join([f"Line {x}" for x in range(500)]), 2)
        # self.sheet.row_height(row = 0, height = 60)
        self.sheet.set_column_widths([120 for c in range(8)])
        self.sheet.column_width(column=0, width=200)

        # self.sheet.set_row_heights([30 for r in range(2000)])
        # self.sheet.set_all_column_widths()
        # self.sheet.set_all_row_heights()
        # self.sheet.set_all_cell_sizes_to_text()

        # __________ BINDING A FUNCTIONS TO USER ACTIONS __________

        self.sheet.extra_bindings([("cell_select", self.cell_select),
                                   # ("begin_edit_cell", self.begin_edit_cell),
                                   ("shift_cell_select", self.shift_select_cells),
                                   ("drag_select_cells", self.drag_select_cells),
                                   ("ctrl_a", self.ctrl_a),
                                   ("row_select", self.row_select),
                                   ("shift_row_select", self.shift_select_rows),
                                   ("drag_select_rows", self.drag_select_rows),
                                   ("column_select", self.column_select),
                                   ("shift_column_select", self.shift_select_columns),
                                   ("drag_select_columns", self.drag_select_columns),
                                   ("deselect", self.deselect)
                                   ])

        # __________ SETTING A CELLS DATA __________

        self.sheet.set_cell_data(0, 0, "Instrument")
        self.sheet.set_cell_data(0, 1, "Start Date")
        self.sheet.set_cell_data(0, 2, "End Date")
        self.sheet.set_cell_data(0, 3, "Discount Factor")
        self.sheet.set_cell_data(0, 4, "ZC Rate")
        self.sheet.set_cell_data(0, 5, "Market Quote")
        self.sheet.set_cell_data(0, 7, "Horizon Date")
        self.sheet.set_cell_data(2, 7, "MCIL")
        self.sheet.set_cell_data(0, 6, "Jump Date")

        # __________ HIGHLIGHT / DEHIGHLIGHT CELLS __________

        self.sheet.highlight_cells(row=0, column=0, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=1, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=2, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=3, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=4, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=5, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=6, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=0, column=7, bg="#ed4337", fg="white")
        self.sheet.highlight_cells(row=2, column=7, bg="#ed4337", fg="white")

        # self.sheet.highlight_cells(row=5, column=1, bg="#ed4337", fg="white")
        # self.sheet.highlight_cells(row=5, bg="#ed4337", fg="white", canvas="row_index")
        # self.sheet.highlight_cells(column=0, bg="#ed4337", fg="white", canvas="header")

        self.sheet.readonly_columns(columns=[3, 4], readonly=True)
        self.sheet.readonly_rows(rows=0, readonly=True)

        # __________ HIDING THE ROW INDEX AND HEADERS __________

        # self.sheet.hide("row_index")
        # self.sheet.hide("top_left")
        self.sheet.hide("header")

        # __________ ADDITIONAL BINDINGS __________

        # self.sheet.bind("<Motion>", self.mouse_motion)



    def begin_edit_cell(self, event):
        pass

    def window_resized(self, event):
        pass
        # print (event)

    def mouse_motion(self, event):
        region = self.sheet.identify_region(event)
        row = self.sheet.identify_row(event, allow_end=False)
        column = self.sheet.identify_column(event, allow_end=False)
        print(region, row, column)

    def deselect(self, event):
        print(event, self.sheet.get_selected_cells())

    def rc(self, event):
        print(event)

    def cell_select(self, response):
        # print (response)
        pass

    def shift_select_cells(self, response):
        print(response)

    def drag_select_cells(self, response):
        pass
        # print (response)

    def ctrl_a(self, response):
        print(response)

    def row_select(self, response):
        print(response)

    def shift_select_rows(self, response):
        print(response)

    def drag_select_rows(self, response):
        pass
        # print (response)

    def column_select(self, response):
        print(response)
        # for i in range(50):
        #    self.sheet.create_dropdown(i, response[1], values=[f"{i}" for i in range(200)], set_value="100",
        #                               destroy_on_select = False, destroy_on_leave = False, see = False)
        # print (self.sheet.get_cell_data(0, 0))
        # self.sheet.refresh()

    def shift_select_columns(self, response):
        print(response)

    def drag_select_columns(self, response):
        pass
        # print (response)

    def LoadDataFromExcel(self, event=None):
        self.data = pd.read_csv("saved_db.csv")
        self.instruments = self.data["Instrument"]
        self.Jumps = self.data["Jump Date"]
        self.StartDate = self.data["Start Date"]
        self.EndDate = self.data["End Date"]
        self.MarketQuote = self.data["Market Quote"]
        self.MCIL = self.data["MCIL"][0]
        self.HorizonDate = self.data['Horizon Date'][0]

        self.LoadingData(self.instruments, 0)
        self.LoadingData(self.StartDate, 1)
        self.LoadingData(self.EndDate, 2)
        self.LoadingData(self.MarketQuote, 5)
        self.LoadingData(self.Jumps, 6)
        self.sheet.set_cell_data(1, 7, self.HorizonDate)
        self.sheet.set_cell_data(3, 7, self.MCIL)

    def LoadingData(self, data, col):
        try:
            length = data.count()
        except:
            length = len(data)

        for i in range(length):
            self.sheet.set_cell_data(i + 1, col, data[i])

    def SaveData(self):
        new_instrument = self.sheet.get_column_data(0)
        new_start_date = self.sheet.get_column_data(1)
        new_end_date = self.sheet.get_column_data(2)
        new_df = self.sheet.get_column_data(3)
        new_zc_rate = self.sheet.get_column_data(4)
        new_marketquote = self.sheet.get_column_data(5)
        new_jump_date = self.sheet.get_column_data(6)
        new_MCIL = (
            'MCIL', self.sheet.get_cell_data(3, 7), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
            '',
            '', '', '', '', '', '', '', '', '', '', '', '')
        new_horizon_date = (
            'Horizon Date', self.sheet.get_cell_data(1, 7), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
            '',
            '', '', '', '', '', '', '', '', '', '', '', '', '', '')

        np.savetxt('saved_db.csv', [p for p in zip(new_instrument, new_start_date, new_end_date, new_df, new_zc_rate,
                                                 new_marketquote, new_jump_date, new_horizon_date, new_MCIL)],
                   delimiter=',', fmt='%s')
        # data = pd.read_csv("scores.csv")

    def JumpMinVarInt(self, event=None):
        self.SaveData()
        self.LoadDataFromExcel()
        JMV_Class = JMV.JumpMinVar()
        self.result, self.lambda_vec = JMV_Class.controller('saved_db.csv')
        length = len(self.StartDate)
        zc_list = []
        df_list = []

        for i in range(length):
            zc_rate, df = JMV_Class.interpolation(self.result, self.lambda_vec, self.StartDate[i], self.EndDate[i])
            zc_list.append(zc_rate)
            df_list.append(df)

        self.LoadingData(zc_list, 4)
        self.LoadingData(df_list, 3)

    # def interpolation


app = RateCurveTable()
app.LoadDataFromExcel()
app.JumpMinVarInt()
app.mainloop()
