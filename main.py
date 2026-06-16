import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime

# Set appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class CellCultureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cell Culture Media Calculator - Lab Edition")
        self.root.geometry("750x850")
        self.root.resizable(True, True)

        # ========== TOP BAR (Always visible) ==========
        top_bar = ctk.CTkFrame(root, height=40, corner_radius=0)
        top_bar.pack(fill="x", side="top", pady=(0, 5))
        top_bar.pack_propagate(False)

        # Producer label (left side)
        producer_label = ctk.CTkLabel(
            top_bar,
            text="Produced by Parsa Arabsahi",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2E8B57"  # SeaGreen
        )
        producer_label.pack(side="left", padx=15)

        # Right side container for mode + about buttons
        right_buttons = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_buttons.pack(side="right", padx=10)

        # About button
        self.about_btn = ctk.CTkButton(
            right_buttons,
            text="ℹ️ About",
            width=80,
            command=self.show_about
        )
        self.about_btn.pack(side="left", padx=5)

        # Appearance mode toggle button
        self.mode_button = ctk.CTkButton(
            right_buttons,
            text=self.get_mode_text(ctk.get_appearance_mode()),
            width=100,
            command=self.toggle_appearance_mode
        )
        self.mode_button.pack(side="left", padx=5)

        # Title (below top bar)
        title = ctk.CTkLabel(root, text="Cell Culture Media Calculator", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(5, 10))

        # Main container with scrollable frame (for many inputs)
        self.main_frame = ctk.CTkScrollableFrame(root, height=600)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ========== BASIC PARAMETERS ==========
        basic_frame = ctk.CTkFrame(self.main_frame)
        basic_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(basic_frame, text="Basic Parameters", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0,
                                                                                                          column=0,
                                                                                                          columnspan=4,
                                                                                                          pady=5,
                                                                                                          sticky="w")

        # Final volume with overage
        ctk.CTkLabel(basic_frame, text="Final volume (mL):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.vol_entry = ctk.CTkEntry(basic_frame, width=120)
        self.vol_entry.grid(row=1, column=1, padx=5, pady=5)
        self.vol_entry.insert(0, "250")

        ctk.CTkLabel(basic_frame, text="Overage (%):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.overage_entry = ctk.CTkEntry(basic_frame, width=80)
        self.overage_entry.grid(row=1, column=3, padx=5, pady=5)
        self.overage_entry.insert(0, "10")
        ctk.CTkLabel(basic_frame, text="(extra for filtering loss)", font=("Arial", 10)).grid(row=2, column=2,
                                                                                              columnspan=2, sticky="w")

        # FBS %
        ctk.CTkLabel(basic_frame, text="FBS (%):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.fbs_entry = ctk.CTkEntry(basic_frame, width=120)
        self.fbs_entry.grid(row=3, column=1, padx=5, pady=5)
        self.fbs_entry.insert(0, "10")

        # Pen/Strep %
        ctk.CTkLabel(basic_frame, text="Pen/Strep (%):").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.ps_entry = ctk.CTkEntry(basic_frame, width=120)
        self.ps_entry.grid(row=3, column=3, padx=5, pady=5)
        self.ps_entry.insert(0, "1")

        # Glutamine with custom stock
        ctk.CTkLabel(basic_frame, text="L-Glutamine final (mM):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.glu_final_entry = ctk.CTkEntry(basic_frame, width=120)
        self.glu_final_entry.grid(row=4, column=1, padx=5, pady=5)
        self.glu_final_entry.insert(0, "2")
        ctk.CTkLabel(basic_frame, text="Stock conc (mM):").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.glu_stock_entry = ctk.CTkEntry(basic_frame, width=120)
        self.glu_stock_entry.grid(row=4, column=3, padx=5, pady=5)
        self.glu_stock_entry.insert(0, "200")

        # ========== COMMON SUPPLEMENTS ==========
        supp_frame = ctk.CTkFrame(self.main_frame)
        supp_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(supp_frame, text="Common Supplements", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0,
                                                                                                           column=0,
                                                                                                           columnspan=4,
                                                                                                           pady=5,
                                                                                                           sticky="w")

        self.supp_widgets = {}
        supplements_list = [
            ("β-Mercaptoethanol", "50", "µM"),
            ("NEAA (100x)", "1", "%"),
            ("Sodium Pyruvate", "1", "mM"),
            ("HEPES", "10", "mM")
        ]
        for i, (name, default_conc, unit) in enumerate(supplements_list):
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(supp_frame, text=name, variable=var)
            cb.grid(row=i + 1, column=0, padx=5, pady=2, sticky="w")
            conc_entry = ctk.CTkEntry(supp_frame, width=80)
            conc_entry.insert(0, default_conc)
            conc_entry.grid(row=i + 1, column=1, padx=5)
            unit_label = ctk.CTkLabel(supp_frame, text=unit)
            unit_label.grid(row=i + 1, column=2, padx=5, sticky="w")
            self.supp_widgets[name] = {"var": var, "entry": conc_entry, "unit": unit}

        # ========== MULTIPLE CYTOKINES ==========
        cytokine_frame = ctk.CTkFrame(self.main_frame)
        cytokine_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(cytokine_frame, text="Cytokines / Growth Factors", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=5, pady=5, sticky="w")

        self.add_cytokine_button = ctk.CTkButton(cytokine_frame, text="+ Add Cytokine", command=self.add_cytokine_row,
                                                 width=120)
        self.add_cytokine_button.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        # Headers
        ctk.CTkLabel(cytokine_frame, text="Name", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=5)
        ctk.CTkLabel(cytokine_frame, text="Final (ng/mL)", font=ctk.CTkFont(weight="bold")).grid(row=2, column=1,
                                                                                                 padx=5)
        ctk.CTkLabel(cytokine_frame, text="Stock (µg/mL)", font=ctk.CTkFont(weight="bold")).grid(row=2, column=2,
                                                                                                 padx=5)

        self.cytokine_rows_frame = ctk.CTkFrame(cytokine_frame)
        self.cytokine_rows_frame.grid(row=3, column=0, columnspan=5, sticky="ew")
        self.cytokine_entries = []
        self.add_cytokine_row()  # default row

        # ========== PRESETS ==========
        preset_frame = ctk.CTkFrame(self.main_frame)
        preset_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(preset_frame, text="Presets", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0,
                                                                                                  padx=5)
        preset_options = ["T cell expansion", "B cell culture", "Macrophage differentiation", "Custom"]
        self.preset_var = ctk.StringVar(value="Custom")
        self.preset_menu = ctk.CTkOptionMenu(preset_frame, values=preset_options, variable=self.preset_var,
                                             command=self.load_preset)
        self.preset_menu.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(preset_frame, text="Recipe Name:").grid(row=0, column=2, padx=5)
        self.recipe_name_entry = ctk.CTkEntry(preset_frame, width=150)
        self.recipe_name_entry.grid(row=0, column=3, padx=5)
        self.recipe_name_entry.insert(0, "My_Recipe")

        # ========== BUTTONS ==========
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.calc_btn = ctk.CTkButton(button_frame, text="Calculate", command=self.calculate, width=120)
        self.calc_btn.grid(row=0, column=0, padx=5)

        self.save_btn = ctk.CTkButton(button_frame, text="Save Recipe", command=self.save_recipe, width=120)
        self.save_btn.grid(row=0, column=1, padx=5)

        self.load_btn = ctk.CTkButton(button_frame, text="Load Recipe", command=self.load_recipe_dialog, width=120)
        self.load_btn.grid(row=0, column=2, padx=5)

        self.copy_btn = ctk.CTkButton(button_frame, text="📋 Copy", command=self.copy_results, width=100)
        self.copy_btn.grid(row=0, column=3, padx=5)

        self.export_btn = ctk.CTkButton(button_frame, text="Export TXT", command=self.export_results, width=100)
        self.export_btn.grid(row=0, column=4, padx=5)

        # ========== RESULTS DISPLAY ==========
        results_frame = ctk.CTkFrame(self.main_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(results_frame, text="Results", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=5)

        self.result_text = ctk.CTkTextbox(results_frame, height=300, font=ctk.CTkFont(family="Courier", size=11))
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_recipe_list()

    # ========== ABOUT POPUP ==========
    def show_about(self):
        about_text = """Hello My amigos! This is Parsa.

I just made this app for fun!
I hope you enjoy it.

Adios!

📧 My e-mail address: Arabshahi59@gmail.com"""
        messagebox.showinfo("About the Developer", about_text)

    # ========== HELPER METHODS ==========
    def get_mode_text(self, mode):
        return {"Light": "🌞 Light", "Dark": "🌙 Dark", "System": "💻 System"}.get(mode, "System")

    def toggle_appearance_mode(self):
        current = ctk.get_appearance_mode()
        new = "Dark" if current == "Light" else "System" if current == "Dark" else "Light"
        ctk.set_appearance_mode(new)
        self.mode_button.configure(text=self.get_mode_text(new))

    def add_cytokine_row(self, name="IL-2", final="50", stock="10"):
        frame = ctk.CTkFrame(self.cytokine_rows_frame)
        frame.pack(fill="x", pady=2)
        name_entry = ctk.CTkEntry(frame, width=100)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=2)
        final_entry = ctk.CTkEntry(frame, width=80)
        final_entry.insert(0, final)
        final_entry.pack(side="left", padx=2)
        stock_entry = ctk.CTkEntry(frame, width=80)
        stock_entry.insert(0, stock)
        stock_entry.pack(side="left", padx=2)

        # Store the tuple
        entry_tuple = (name_entry, final_entry, stock_entry, frame)
        self.cytokine_entries.append(entry_tuple)

        # Remove function that cleans the list AND destroys the frame
        def remove_row():
            if entry_tuple in self.cytokine_entries:
                self.cytokine_entries.remove(entry_tuple)
            frame.destroy()

        remove_btn = ctk.CTkButton(frame, text="✖", width=30, command=remove_row)
        remove_btn.pack(side="left", padx=5)

    def clear_cytokines(self):
        for _, _, _, frame in self.cytokine_entries:
            frame.destroy()
        self.cytokine_entries.clear()
        self.add_cytokine_row()

    def load_preset(self, preset):
        if preset == "T cell expansion":
            self.fbs_entry.delete(0, 'end');
            self.fbs_entry.insert(0, "10")
            self.ps_entry.delete(0, 'end');
            self.ps_entry.insert(0, "1")
            self.clear_cytokines()
            self.add_cytokine_row("IL-2", "50", "10")
        elif preset == "B cell culture":
            self.fbs_entry.delete(0, 'end');
            self.fbs_entry.insert(0, "10")
            self.ps_entry.delete(0, 'end');
            self.ps_entry.insert(0, "1")
            self.clear_cytokines()
            self.add_cytokine_row("IL-4", "20", "10")
        elif preset == "Macrophage differentiation":
            self.fbs_entry.delete(0, 'end');
            self.fbs_entry.insert(0, "10")
            self.ps_entry.delete(0, 'end');
            self.ps_entry.insert(0, "1")
            self.clear_cytokines()
            self.add_cytokine_row("M-CSF", "10", "10")
        self.preset_var.set("Custom")

    def validate_warnings(self, vol, fbs, ps, glu_final, glu_stock, cytokine_data):
        warnings = []
        if fbs > 20:
            warnings.append("⚠️ FBS >20% is unusually high (typical 2-20%)")
        if fbs < 1 and fbs > 0:
            warnings.append("⚠️ Very low FBS (<1%) - cells may not grow")
        if ps > 2:
            warnings.append("⚠️ Pen/Strep >2% could be toxic")
        if glu_final > 4:
            warnings.append("⚠️ High glutamine (>4 mM) may cause ammonia buildup")
        if glu_stock not in [100, 200]:
            warnings.append("⚠️ Unusual glutamine stock concentration. Standard is 100 or 200 mM.")
        for cyto in cytokine_data:
            if cyto["final"] > 200:
                warnings.append(f"⚠️ {cyto['name']} final concentration {cyto['final']} ng/mL is very high")
        if vol > 1000:
            warnings.append("⚠️ Volume >1 L – consider making in batches")
        return warnings

    def calculate(self):
        try:
            vol = float(self.vol_entry.get())
            overage_pct = float(self.overage_entry.get())
            total_vol = vol * (1 + overage_pct / 100)
            fbs = float(self.fbs_entry.get())
            ps = float(self.ps_entry.get())
            glu_final = float(self.glu_final_entry.get())
            glu_stock = float(self.glu_stock_entry.get())

            active_supplements = {}
            for name, data in self.supp_widgets.items():
                if data["var"].get():
                    conc = float(data["entry"].get())
                    active_supplements[name] = conc

            cytokine_data = []
            for name_entry, final_entry, stock_entry, _ in self.cytokine_entries:
                name = name_entry.get().strip()
                if not name:
                    continue
                final = float(final_entry.get())
                stock = float(stock_entry.get())
                if final > 0 and stock > 0:
                    cytokine_data.append({"name": name, "final": final, "stock": stock})

            warnings = self.validate_warnings(total_vol, fbs, ps, glu_final, glu_stock, cytokine_data)

            results = {}
            remaining = total_vol

            if fbs > 0:
                vol_fbs = total_vol * (fbs / 100)
                results["FBS"] = round(vol_fbs, 1)
                remaining -= vol_fbs
            if ps > 0:
                vol_ps = total_vol * (ps / 100)
                results["Pen/Strep (100x)"] = round(vol_ps, 1)
                remaining -= vol_ps
            if glu_final > 0 and glu_stock > 0:
                vol_glu = total_vol * (glu_final / glu_stock)
                results[f"L-Glutamine ({glu_stock} mM stock)"] = round(vol_glu, 1)
                remaining -= vol_glu

            for name, conc in active_supplements.items():
                vol_supp = total_vol * (conc / 100)  # assume 100x stocks
                results[name] = round(vol_supp, 1)
                remaining -= vol_supp

            for cyto in cytokine_data:
                stock_ng_per_ul = cyto["stock"]
                target_ng_per_ml = cyto["final"]
                vol_ul = (target_ng_per_ml * total_vol) / stock_ng_per_ul
                results[f"{cyto['name']} (stock {cyto['stock']} µg/mL)"] = f"{round(vol_ul, 1)} µL"
                remaining -= vol_ul / 1000

            results["Base medium (DMEM/RPMI/etc.)"] = round(remaining, 1)

            self.result_text.delete("1.0", "end")
            self.result_text.insert("end",
                                    f"TOTAL VOLUME (including {overage_pct}% overage): {round(total_vol, 1)} mL\n")
            self.result_text.insert("end", f"Target final volume after filtration: {vol} mL\n")
            self.result_text.insert("end", "=" * 50 + "\n\n")
            for key, val in results.items():
                self.result_text.insert("end", f"{key}: {val}\n")
            if warnings:
                self.result_text.insert("end", "\n" + "=" * 50 + "\n⚠️ WARNINGS:\n")
                for w in warnings:
                    self.result_text.insert("end", f"  {w}\n")
            return results
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def copy_results(self):
        text = self.result_text.get("1.0", "end")
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Results copied to clipboard")
        else:
            messagebox.showwarning("Nothing to copy", "Calculate something first")

    def export_results(self):
        text = self.result_text.get("1.0", "end")
        if not text.strip():
            messagebox.showwarning("No results", "Calculate first")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, "w") as f:
                f.write(f"Cell Culture Media Recipe - {datetime.now()}\n")
                f.write("=" * 50 + "\n")
                f.write(text)
            messagebox.showinfo("Exported", f"Saved to {filename}")

    def save_recipe(self):
        recipe = {
            "name": self.recipe_name_entry.get(),
            "volume_ml": self.vol_entry.get(),
            "overage_pct": self.overage_entry.get(),
            "fbs": self.fbs_entry.get(),
            "penstrep": self.ps_entry.get(),
            "glutamine_final": self.glu_final_entry.get(),
            "glutamine_stock": self.glu_stock_entry.get(),
            "supplements": {},
            "cytokines": []
        }
        for name, data in self.supp_widgets.items():
            if data["var"].get():
                recipe["supplements"][name] = data["entry"].get()
        for name_e, final_e, stock_e, _ in self.cytokine_entries:
            if name_e.get().strip():
                recipe["cytokines"].append({
                    "name": name_e.get(),
                    "final": final_e.get(),
                    "stock": stock_e.get()
                })
        recipes = []
        if os.path.exists(self.recipe_file):
            with open(self.recipe_file, "r") as f:
                recipes = json.load(f)
        existing = [r for r in recipes if r.get("name") == recipe["name"]]
        if existing:
            recipes = [r if r.get("name") != recipe["name"] else recipe for r in recipes]
        else:
            recipes.append(recipe)
        with open(self.recipe_file, "w") as f:
            json.dump(recipes, f, indent=4)
        messagebox.showinfo("Saved", f"Recipe '{recipe['name']}' saved")

    def load_recipe_dialog(self):
        if not os.path.exists(self.recipe_file):
            messagebox.showwarning("No recipes", "No saved recipes found")
            return
        with open(self.recipe_file, "r") as f:
            recipes = json.load(f)
        if not recipes:
            messagebox.showwarning("Empty", "No recipes")
            return
        choice = ctk.CTkInputDialog(text="Enter recipe name:", title="Load Recipe")
        chosen_name = choice.get_input()
        if not chosen_name:
            return
        recipe = next((r for r in recipes if r["name"] == chosen_name), None)
        if not recipe:
            messagebox.showerror("Not found", f"No recipe named '{chosen_name}'")
            return
        self.vol_entry.delete(0, 'end');
        self.vol_entry.insert(0, recipe["volume_ml"])
        self.overage_entry.delete(0, 'end');
        self.overage_entry.insert(0, recipe["overage_pct"])
        self.fbs_entry.delete(0, 'end');
        self.fbs_entry.insert(0, recipe["fbs"])
        self.ps_entry.delete(0, 'end');
        self.ps_entry.insert(0, recipe["penstrep"])
        self.glu_final_entry.delete(0, 'end');
        self.glu_final_entry.insert(0, recipe["glutamine_final"])
        self.glu_stock_entry.delete(0, 'end');
        self.glu_stock_entry.insert(0, recipe["glutamine_stock"])
        for name, data in self.supp_widgets.items():
            if name in recipe["supplements"]:
                data["var"].set(True)
                data["entry"].delete(0, 'end')
                data["entry"].insert(0, recipe["supplements"][name])
            else:
                data["var"].set(False)
        self.clear_cytokines()
        for cyto in recipe["cytokines"]:
            self.add_cytokine_row(cyto["name"], cyto["final"], cyto["stock"])
        self.recipe_name_entry.delete(0, 'end')
        self.recipe_name_entry.insert(0, recipe["name"])
        messagebox.showinfo("Loaded", f"Loaded '{recipe['name']}'")

    def load_recipe_list(self):
        pass


if __name__ == "__main__":
    root = ctk.CTk()
    app = CellCultureApp(root)
    root.mainloop()