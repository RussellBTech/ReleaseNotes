import tkinter as tk

from tkinter import messagebox
from tkinter import ttk
from encryption import delete_files
from release_notes import generate_release_notes, open_release_notes
from kirby import get_random_kirby
from encryption import load_decrypted_data, save_encrypted_data
from project import Project


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.projects = {}
        self.shared_pat = tk.StringVar()
        self.shared_org_url = tk.StringVar()
        self.current_tab_name = tk.StringVar()
        self.bound_functions = {}
        self.pack()
        self.create_widgets()

        # Set window title
        self.master.title("Kirby's Release Notes Generator")

        # Set window icon
        self.master.iconbitmap(
            r'C:/Users/RustyBurns/source/util-scripts/ReleaseNotes/assets/kirby.ico')

        # Load the input values when the application is started
        self.get_input_values()

        # Check if there are any tabs in the notebook, if not, create a default tab
        if not self.notebook.tabs():
            tab_name = "Default Tab"
            project_name = "Default Project"
            self.create_new_tab(tab_name, Project(project_name, []))

    def create_widgets(self):
        # Create the menu bar
        self.menu_bar = tk.Menu(self.master)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        def delete_all_data():
            # Confirm before deleting all data
            if not messagebox.askokcancel("Delete Inputs and Close", "Are you sure you want to delete all saved data and close the application?"):
                return

            # Delete all data
            delete_files()
            self.master.destroy()

        self.file_menu.add_command(
            label="Delete All Saved Data", command=delete_all_data)
        self.master.config(menu=self.menu_bar)

        # Add a random Kirby at the top
        self.kirby_label = tk.Label(self, text=get_random_kirby())
        self.kirby_label.pack()

        self.update_kirby_label()

        # Personal Access Token (PAT) input
        self.pat_label = tk.Label(self, text="Personal Access Token (PAT):")
        self.pat_label.pack()

        self.pat_input = tk.Entry(
            self, show="*", width=50, textvariable=self.shared_pat)
        self.pat_input.pack()

        # Organization URL input
        self.org_label = tk.Label(
            self, text="Organization URL:\n(e.g. https://dev.azure.com/your_organization)")
        self.org_label.pack()

        self.org_input = tk.Entry(
            self, width=50, textvariable=self.shared_org_url)
        self.org_input.pack()

        # Frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack()

        # Add project button
        self.add_project_button = tk.Button(
            button_frame, text="Add Project", command=self.create_new_tab)
        self.add_project_button.pack(side="left", padx=5, pady=5)

        # Delete project button
        self.delete_project_button = tk.Button(
            button_frame, text="Delete Project", command=self.delete_project)
        self.delete_project_button.pack(side="left", padx=5, pady=5)

        # Create a notebook (tab control)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Run button
        self.run_button = tk.Button(self, text="Run", command=self.run_script)
        self.run_button.pack(padx=5, pady=5)

        # Update the delete button state
        self.update_delete_button_state()

    def run_script(self):
        # If you hit run, save the input values
        self.save_input_values()

        # Get the selected tab
        selected_tab = self.notebook.select()
        tab_name = self.notebook.tab(selected_tab, "text")

        # Get the input values
        project_name = self.projects[tab_name].project_name
        repositoryNames = self.projects[tab_name].repository_names

        # Run the script
        try:
            release_notes_file, error_message = generate_release_notes(
                self.shared_pat.get(), self.shared_org_url.get(), project_name, repositoryNames)
            if error_message != "":  # If there is an error message, show it in a dialog box
                messagebox.showerror("Error", error_message)
            else:
                open_release_notes(release_notes_file)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_input_values(self):
        data = {
            "pat": self.shared_pat.get(),
            "org_url": self.shared_org_url.get(),
            "projects": {
                tab: {
                    "project_name": project.project_name,
                    "repository_names": project.repository_names
                } for tab, project in self.projects.items()
            }
        }
        save_encrypted_data(data)

    def get_input_values(self):
        input_values = load_decrypted_data()
        if input_values:
            try:
                pat = input_values.get("pat", "")
                org_url = input_values.get("org_url", "")
                projects = input_values.get("projects", {})
                self.shared_pat.set(pat)
                self.shared_org_url.set(org_url)
                self.projects = {
                    tab: Project(details["project_name"],
                                 details["repository_names"])
                    for tab, details in projects.items()
                }

                # Remove existing tabs
                for tab in self.notebook.tabs():
                    self.notebook.forget(tab)

                # Create a tab for each project
                for tab_name, project in self.projects.items():
                    self.create_new_tab(tab_name, project)

            except Exception as e:
                pass

    def delete_project(self):
        # Get the currently selected tab
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")

        # Unbind the update_tab_name function for this tab
        self.notebook.nametowidget(current_tab).children['!entry'].unbind(
            "<FocusOut>", self.bound_functions[tab_name])
        # Remove the tab from the notebook
        self.notebook.forget(current_tab)

        # Remove the project data
        del self.projects[tab_name]

        self.save_input_values()

        # Update the delete button state
        self.update_delete_button_state()

        # Set the current_tab_name to the new selected tab
        selected_tab = self.notebook.select()
        self.current_tab_name.set(self.notebook.tab(selected_tab, "text"))

    def create_new_tab(self, tab_name=None, project=None):
        # Create the frame for the tab
        frame = tk.Frame(self.notebook)

        if tab_name and project:
            project_name = project.project_name
            repository_names = project.repository_names
        else:
            # Set defaults for new project
            tab_name = self.get_unique_tab_name()
            project_name = "Default Project"
            repository_names = []

        # Add the tab to the notebook
        self.notebook.add(frame, text=tab_name)

        # Create the tab name input
        self.create_tab_name_input(frame, tab_name)

        # Project Name input
        self.create_project_name_input(frame, project_name)

        # Repository Names input
        self.create_repository_names_input(frame, repository_names)

        # Save the project data
        self.projects[tab_name] = Project(project_name, repository_names)

        self.save_input_values()

        # Update the delete button state
        self.update_delete_button_state()

        # Select the new tab
        self.notebook.select(self.notebook.index("end") - 1)

    def create_tab_name_input(self, frame, tab_name):
        # Tab name input
        tab_name_label = tk.Label(frame, text="Tab Name")
        tab_name_label.pack()

        tab_name_input = tk.Entry(frame, width=50)
        tab_name_input.pack()
        tab_name_input.insert(0, tab_name)

        def update_tab_name(event):
            old_tab_name = self.current_tab_name.get()
            new_tab_name = tab_name_input.get().strip()  # strip leading/trailing spaces
            if new_tab_name and old_tab_name != new_tab_name and new_tab_name not in self.projects:
                # Check if the tab is still the same
                if old_tab_name in self.projects:
                    selected_tab = self.notebook.select()
                    self.notebook.tab(selected_tab, text=new_tab_name)
                    self.projects[new_tab_name] = self.projects.pop(
                        old_tab_name)
                    self.current_tab_name.set(new_tab_name)
                    self.save_input_values()
                else:
                    # Reset to the old name
                    tab_name_input.delete(0, tk.END)
                    tab_name_input.insert(0, old_tab_name)
            else:
                # Reset to the old name
                tab_name_input.delete(0, tk.END)
                tab_name_input.insert(0, old_tab_name)

        bind_id = tab_name_input.bind("<FocusOut>", update_tab_name)
        self.bound_functions[tab_name] = bind_id
        self.current_tab_name.set(tab_name)

    def create_project_name_input(self, frame, project_name):
        project_label = tk.Label(frame, text="Project Name")
        project_label.pack()

        project_input = tk.Entry(frame, width=50)
        project_input.pack()
        project_input.insert(0, project_name)

        def update_project_name(event):
            tab_name = self.current_tab_name.get()
            old_project_name = self.projects[tab_name].project_name
            new_project_name = project_input.get()

            if new_project_name and new_project_name != "":
                self.projects[tab_name].project_name = new_project_name
                self.save_input_values()
            else:
                messagebox.showwarning(
                    "Warning", "Project name must be at least 1 character. Please enter a project name.")
                project_input.delete(0, tk.END)
                project_input.insert(0, old_project_name)

        project_input.bind("<FocusOut>", update_project_name)

    def create_repository_names_input(self, frame, repository_names):
        repo_label = tk.Label(
            frame, text="Repository Names (comma-separated):")
        repo_label.pack()

        # Adjust height as necessary
        repo_input = tk.Text(frame, width=50, height=10)
        repo_input.pack()
        # Each repository name on a new line
        repo_input.insert(tk.END, ", ".join(repository_names))

        def update_repository_names(event):
            tab_name = self.current_tab_name.get()
            # set repository names to the list of names in the text box while removing any whitespace before and after each name
            self.projects[tab_name].repository_names = [
                name.strip() for name in repo_input.get("1.0", tk.END).split(",") if name.strip()]
            self.save_input_values()

        repo_input.bind("<KeyRelease>", update_repository_names)

    def get_unique_tab_name(self):
        base_name = "New Tab"
        unique_name = base_name
        count = 1
        while unique_name in self.projects:
            unique_name = f"{base_name} ({count})"
            count += 1
        return unique_name

    def update_delete_button_state(self):
        if len(self.notebook.tabs()) > 1:
            self.delete_project_button["state"] = "normal"
        else:
            self.delete_project_button["state"] = "disabled"

    def on_tab_changed(self, event):
        # Get the currently selected tab
        selected_tab = self.notebook.select()
        tab_name = self.notebook.tab(selected_tab, "text")

        # Update the current_tab_name
        self.current_tab_name.set(tab_name)

    def update_kirby_label(self):
        # Update Kirby label with a new random Kirby
        self.kirby_label.configure(text=get_random_kirby())

        # Schedule the next update after 500 milliseconds (half second)
        self.after(500, self.update_kirby_label)
