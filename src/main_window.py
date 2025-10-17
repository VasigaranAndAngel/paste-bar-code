from typing import Callable, override
from tkinter import Entry, Event, StringVar, Tk, ttk, Misc


class FPSEntry(ttk.Entry):
    def __init__(self, master: Misc) -> None:
        super().__init__(
            master,
            validate="all",
            validatecommand=self._validate,
        )

    def _validate(self) -> bool:
        current_value = self.get()
        if current_value.isdigit():
            return True
        return False


class MainWindow(Tk):
    def __init__(self) -> None:
        super().__init__()

        self.on_fps_change_command: Callable[[int], None] = lambda x: None
        self.before_quit: list[Callable[[], None]] = []

        self.frame_label: ttk.Label = ttk.Label(self, justify="center", width=100)
        self.frame_label.pack(fill="both")

        self._fps_entry: ttk.Entry = ttk.Entry(self)
        self._fps_entry.pack(fill="x")
        _ = self._fps_entry.bind("<KeyRelease>", self._on_fps_change)

        self._selected_label: ttk.Label = ttk.Label(self, text="None", justify="center")
        self._selected_label.pack(fill="x")
        ttk.Button(self, text="Quit", command=self.destroy).pack(anchor="se")

        # region setup combobox
        self._combo_box_var: StringVar = StringVar(self)
        self._combobox: ttk.Combobox = ttk.Combobox(
            self,
            textvariable=self._combo_box_var,
            validate="all",
            validatecommand=self._validate_combobox_value,
        )
        self._combobox.pack(fill="x")
        _ = self._combobox.bind("<<ComboboxSelected>>", self._on_combobox_selection)
        # endregion

        self._update_camera_list()

    def _update_camera_list(self) -> None:
        lst: list[str] = ["Cam 1", "Cam 2"]
        self._combobox["values"] = lst

    def _validate_combobox_value(self) -> bool:
        current_value: str = self._combo_box_var.get()
        available_values: list[str] = self._combobox["values"]

        for value in available_values:
            if current_value.startswith(value):
                return True

        return False

    def _on_combobox_selection(self, *args) -> None:
        self._selected_label["text"] = self._combo_box_var.get()

    def _on_fps_change(self, _) -> None:
        self.on_fps_change_command(int(self._fps_entry.get()))

    def _execute_before_quit(self) -> None:
        for func in self.before_quit:
            func()

    @override
    def quit(self) -> None:
        print("executing before quit in quit")
        self._execute_before_quit()
        return super().quit()

    @override
    def destroy(self) -> None:
        print("executing before quit in destroy")
        self._execute_before_quit()
        return super().destroy()


if __name__ == "__main__":
    MainWindow().mainloop()
